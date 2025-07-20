import asyncio
import os
import threading
from typing import AsyncGenerator, Dict, List, Optional, Tuple

from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

# Placeholder import for LlamaGPU and ModelManager
try:
    from llama_gpu import LlamaGPU
except ImportError:
    LlamaGPU = None
try:
    from model_manager import ModelManager
except ImportError:
    ModelManager = None

app = FastAPI(title="Llama-GPU API Server", version="0.2.0")

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

# --- REST Endpoints ---
@app.post("/v1/completions")
async def completions(req: CompletionRequest):
    llama = get_llama(req.model_name, req.revision)
    if not llama:
        return JSONResponse({"error": "LlamaGPU or ModelManager not available"}, status_code=503)
    if req.stream:
        async def token_stream() -> AsyncGenerator[str, None]:
            for token in llama.stream_infer(req.prompt, max_tokens=req.max_tokens):
                yield token
        return StreamingResponse(token_stream(), media_type="text/plain")
    else:
        result = llama.infer(req.prompt)
        return {"id": "cmpl-1", "object": "text_completion", "choices": [{"text": result}]}

@app.post("/v1/chat/completions")
async def chat_completions(req: ChatCompletionRequest):
    llama = get_llama(req.model_name, req.revision)
    if not llama:
        return JSONResponse({"error": "LlamaGPU or ModelManager not available"}, status_code=503)
    prompt = "\n".join([f"{m.role}: {m.content}" for m in req.messages])
    if req.stream:
        async def token_stream() -> AsyncGenerator[str, None]:
            for token in llama.stream_infer(prompt, max_tokens=req.max_tokens):
                yield token
        return StreamingResponse(token_stream(), media_type="text/plain")
    else:
        result = llama.infer(prompt)
        return {"id": "chatcmpl-1", "object": "chat.completion", "choices": [{"message": {"role": "assistant", "content": result}}]}

@app.post("/v1/models/load")
async def load_model(req: ModelLoadRequest):
    if not model_manager:
        return JSONResponse({"error": "ModelManager not available"}, status_code=503)
    model_path = model_manager.download_model(req.model_name, req.revision)
    with _loaded_models_lock:
        _loaded_models[(req.model_name, req.revision)] = LlamaGPU(str(model_path))
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
            return
        for token in llama.stream_infer(prompt, max_tokens=max_tokens):
            await websocket.send_text(token)
        await websocket.send_text("[END]")
    except Exception as e:
        await websocket.send_json({"error": str(e)})
    finally:
        await websocket.close() 