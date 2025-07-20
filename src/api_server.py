import asyncio
import os
import threading
import time
from collections import defaultdict, deque
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple

from fastapi import FastAPI, Header, HTTPException, Request, WebSocket
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

# --- Logging Setup ---
LOG_DIR = os.environ.get("LLAMA_GPU_LOG_DIR", "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "api_server.log")
import logging

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("api_server")

# --- API Key Auth & Rate Limiting ---
API_KEY = os.environ.get("LLAMA_GPU_API_KEY", "test-key")
RATE_LIMIT = int(os.environ.get("LLAMA_GPU_RATE_LIMIT", 60))  # requests per minute
_rate_limiters: Dict[str, deque] = defaultdict(deque)  # ip -> deque[timestamps]

async def check_auth_and_rate_limit(request: Request, x_api_key: str = Header(None)):
    client_ip = request.client.host
    if x_api_key != API_KEY:
        logger.warning(f"Unauthorized access from {client_ip}")
        raise HTTPException(status_code=401, detail="Invalid API key")
    now = datetime.utcnow().timestamp()
    dq = _rate_limiters[client_ip]
    dq.append(now)
    # Remove timestamps older than 60s
    while dq and now - dq[0] > 60:
        dq.popleft()
    if len(dq) > RATE_LIMIT:
        logger.warning(f"Rate limit exceeded for {client_ip}")
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

# Placeholder import for LlamaGPU and ModelManager
try:
    from llama_gpu import LlamaGPU
except ImportError:
    LlamaGPU = None
try:
    from model_manager import ModelManager
except ImportError:
    ModelManager = None

app = FastAPI(title="Llama-GPU API Server", version="0.4.0")

# --- Request/Response Schemas ---
class CompletionRequest(BaseModel):
    prompt: str
    max_tokens: Optional[int] = 256
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    stream: Optional[bool] = False
    model_name: Optional[str] = None
    revision: Optional[str] = None

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    messages: List[ChatMessage]
    max_tokens: Optional[int] = 256
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    stream: Optional[bool] = False
    model_name: Optional[str] = None
    revision: Optional[str] = None

class ModelLoadRequest(BaseModel):
    model_name: str
    revision: Optional[str] = None

# --- Model Management ---
MODEL_PATH = os.environ.get("LLAMA_GPU_MODEL_PATH", "path/to/model")
DEFAULT_MODEL_NAME = os.environ.get("LLAMA_GPU_MODEL_NAME", "llama-base")

model_manager = ModelManager() if ModelManager else None
# Global cache: (model_name, revision) -> LlamaGPU instance
_loaded_models: Dict[Tuple[str, Optional[str]], LlamaGPU] = {}
_loaded_models_lock = threading.Lock()

def get_llama(model_name: Optional[str], revision: Optional[str]) -> Optional[LlamaGPU]:
    key = (model_name or DEFAULT_MODEL_NAME, revision)
    with _loaded_models_lock:
        if key in _loaded_models:
            return _loaded_models[key]
        if not model_manager:
            return None
        model_path = model_manager.download_model(key[0], key[1])
        llama = LlamaGPU(str(model_path))
        _loaded_models[key] = llama
        return llama

# --- Request Queuing and Dynamic Batching ---
class BatchRequest:
    def __init__(self, req: Any, future: asyncio.Future):
        self.req = req
        self.future = future

# Queues: (model_name, revision) -> deque of BatchRequest
_completion_queues: Dict[Tuple[str, Optional[str]], deque] = defaultdict(deque)
_chat_queues: Dict[Tuple[str, Optional[str]], deque] = defaultdict(deque)
BATCH_SIZE = int(os.environ.get("LLAMA_GPU_BATCH_SIZE", 4))
BATCH_INTERVAL = float(os.environ.get("LLAMA_GPU_BATCH_INTERVAL", 0.05))  # 50ms

async def batch_worker(queue: deque, is_chat: bool, model_name: str, revision: Optional[str]):
    while True:
        await asyncio.sleep(BATCH_INTERVAL)
        batch = []
        while queue and len(batch) < BATCH_SIZE:
            batch.append(queue.popleft())
        if not batch:
            continue
        llama = get_llama(model_name, revision)
        if not llama:
            for br in batch:
                br.future.set_result({"error": "LlamaGPU or ModelManager not available"})
            logger.error(f"Batch error: LlamaGPU or ModelManager not available for {model_name}:{revision}")
            continue
        if is_chat:
            prompts = ["\n".join([f"{m.role}: {m.content}" for m in br.req.messages]) for br in batch]
        else:
            prompts = [br.req.prompt for br in batch]
        # Batch inference
        try:
            results = llama.batch_infer(prompts, batch_size=len(batch))
            for br, result in zip(batch, results):
                if is_chat:
                    br.future.set_result({"id": "chatcmpl-1", "object": "chat.completion", "choices": [{"message": {"role": "assistant", "content": result}}]})
                else:
                    br.future.set_result({"id": "cmpl-1", "object": "text_completion", "choices": [{"text": result}]})
            logger.info(f"Batch processed: model={model_name} rev={revision} size={len(batch)} queue_len={len(queue)}")
        except Exception as e:
            for br in batch:
                br.future.set_result({"error": str(e)})
            logger.error(f"Batch error: {e}")

# Start batch workers for each model on demand
_batch_workers: Dict[Tuple[str, Optional[str], bool], asyncio.Task] = {}

def ensure_batch_worker(model_name: str, revision: Optional[str], is_chat: bool):
    key = (model_name, revision, is_chat)
    if key in _batch_workers:
        return
    queue = _chat_queues[(model_name, revision)] if is_chat else _completion_queues[(model_name, revision)]
    loop = asyncio.get_event_loop()
    _batch_workers[key] = loop.create_task(batch_worker(queue, is_chat, model_name, revision))

# --- Monitoring Endpoints ---
@app.get("/v1/monitor/queues")
async def monitor_queues(request: Request, x_api_key: str = Header(None)):
    await check_auth_and_rate_limit(request, x_api_key)
    data = {
        "completion_queues": {str(k): len(v) for k, v in _completion_queues.items()},
        "chat_queues": {str(k): len(v) for k, v in _chat_queues.items()}
    }
    logger.info(f"Monitor queues: {data}")
    return data

@app.get("/v1/monitor/batches")
async def monitor_batches(request: Request, x_api_key: str = Header(None)):
    await check_auth_and_rate_limit(request, x_api_key)
    data = {"batch_workers": list(_batch_workers.keys())}
    logger.info(f"Monitor batches: {data}")
    return data

# --- REST Endpoints ---
@app.post("/v1/completions")
async def completions(req: CompletionRequest, request: Request, x_api_key: str = Header(None)):
    await check_auth_and_rate_limit(request, x_api_key)
    if req.stream:
        llama = get_llama(req.model_name, req.revision)
        if not llama:
            logger.error("LlamaGPU or ModelManager not available for streaming completion")
            return JSONResponse({"error": "LlamaGPU or ModelManager not available"}, status_code=503)
        async def token_stream() -> AsyncGenerator[str, None]:
            for token in llama.stream_infer(req.prompt, max_tokens=req.max_tokens):
                yield token
        return StreamingResponse(token_stream(), media_type="text/plain")
    # Queued + batched
    model_name = req.model_name or DEFAULT_MODEL_NAME
    revision = req.revision
    ensure_batch_worker(model_name, revision, is_chat=False)
    queue = _completion_queues[(model_name, revision)]
    loop = asyncio.get_event_loop()
    future = loop.create_future()
    queue.append(BatchRequest(req, future))
    result = await future
    logger.info(f"Completion request processed: model={model_name} rev={revision}")
    return result

@app.post("/v1/chat/completions")
async def chat_completions(req: ChatCompletionRequest, request: Request, x_api_key: str = Header(None)):
    await check_auth_and_rate_limit(request, x_api_key)
    if req.stream:
        llama = get_llama(req.model_name, req.revision)
        if not llama:
            logger.error("LlamaGPU or ModelManager not available for streaming chat completion")
            return JSONResponse({"error": "LlamaGPU or ModelManager not available"}, status_code=503)
        prompt = "\n".join([f"{m.role}: {m.content}" for m in req.messages])
        async def token_stream() -> AsyncGenerator[str, None]:
            for token in llama.stream_infer(prompt, max_tokens=req.max_tokens):
                yield token
        return StreamingResponse(token_stream(), media_type="text/plain")
    # Queued + batched
    model_name = req.model_name or DEFAULT_MODEL_NAME
    revision = req.revision
    ensure_batch_worker(model_name, revision, is_chat=True)
    queue = _chat_queues[(model_name, revision)]
    loop = asyncio.get_event_loop()
    future = loop.create_future()
    queue.append(BatchRequest(req, future))
    result = await future
    logger.info(f"Chat completion request processed: model={model_name} rev={revision}")
    return result

@app.post("/v1/models/load")
async def load_model(req: ModelLoadRequest, request: Request, x_api_key: str = Header(None)):
    await check_auth_and_rate_limit(request, x_api_key)
    if not model_manager:
        logger.error("ModelManager not available for model load")
        return JSONResponse({"error": "ModelManager not available"}, status_code=503)
    model_path = model_manager.download_model(req.model_name, req.revision)
    with _loaded_models_lock:
        _loaded_models[(req.model_name, req.revision)] = LlamaGPU(str(model_path))
    logger.info(f"Model loaded: {req.model_name} rev={req.revision}")
    return {"status": "loaded", "model_name": req.model_name, "revision": req.revision}

# --- WebSocket Streaming Endpoint ---
@app.websocket("/v1/stream")
async def websocket_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        prompt = data.get("prompt", "")
        max_tokens = data.get("max_tokens", 256)
        model_name = data.get("model_name")
        revision = data.get("revision")
        llama = get_llama(model_name, revision)
        if not llama:
            await websocket.send_json({"error": "LlamaGPU or ModelManager not available"})
            logger.error("LlamaGPU or ModelManager not available for websocket stream")
            return
        for token in llama.stream_infer(prompt, max_tokens=max_tokens):
            await websocket.send_text(token)
        await websocket.send_text("[END]")
        logger.info(f"WebSocket stream completed: model={model_name} rev={revision}")
    except Exception as e:
        await websocket.send_json({"error": str(e)})
        logger.error(f"WebSocket error: {e}")
    finally:
        await websocket.close() 