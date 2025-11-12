"""Unified API server supporting multiple inference backends (LlamaGPU + Ollama)."""

import os
import time
import logging
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, Header, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import backends
from src.llama_gpu import LlamaGPU
from src.backends.ollama import OllamaBackend

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*")
REQUIRE_API_KEY = os.getenv("REQUIRE_API_KEY", "false").lower() == "true"
API_KEY = os.getenv("API_KEY", "")
PREFERRED_BACKEND = os.getenv("BACKEND", "auto")  # auto, ollama, llama-gpu

app = FastAPI(
    title="Llama-GPU Unified API",
    description="Multi-backend inference API supporting LlamaGPU and Ollama",
    version="0.2.0"
)

# CORS configuration
if ALLOWED_ORIGINS == "*":
    allow_origins = ["*"]
else:
    allow_origins = [o.strip() for o in ALLOWED_ORIGINS.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize backends
backends = {}
active_backend = None


def initialize_backends():
    """Initialize all available backends."""
    global backends, active_backend
    
    logger.info("Initializing inference backends...")
    
    # Try Ollama first
    try:
        ollama = OllamaBackend()
        if ollama.initialize():
            backends["ollama"] = ollama
            logger.info("✅ Ollama backend initialized")
            if active_backend is None or PREFERRED_BACKEND == "ollama":
                active_backend = "ollama"
    except Exception as e:
        logger.warning(f"⚠️  Ollama backend initialization failed: {e}")
    
    # Try LlamaGPU
    try:
        llama_gpu = LlamaGPU(model_path=None, prefer_gpu=True)
        backends["llama-gpu"] = llama_gpu
        logger.info("✅ LlamaGPU backend initialized")
        if active_backend is None or PREFERRED_BACKEND == "llama-gpu":
            active_backend = "llama-gpu"
    except Exception as e:
        logger.warning(f"⚠️  LlamaGPU backend initialization failed: {e}")
    
    if not backends:
        logger.error("❌ No backends available!")
        raise RuntimeError("No inference backends could be initialized")
    
    logger.info(f"🚀 Active backend: {active_backend}")
    logger.info(f"📦 Available backends: {list(backends.keys())}")


# Initialize on startup
@app.on_event("startup")
async def startup_event():
    initialize_backends()


def guard_api_key(authorization: Optional[str]) -> None:
    """Validate API key if required."""
    if not REQUIRE_API_KEY:
        return
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing API key")
    token = authorization.split(" ", 1)[1].strip()
    if token != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")


class CompletionRequest(BaseModel):
    model: Optional[str] = None
    prompt: str
    max_tokens: int = 512
    temperature: float = 0.7
    backend: Optional[str] = None


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: Optional[str] = None
    messages: List[ChatMessage]
    max_tokens: int = 512
    temperature: float = 0.7
    backend: Optional[str] = None


@app.get("/healthz")
def healthz() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "backends": list(backends.keys())}


@app.get("/livez")
def livez() -> Dict[str, Any]:
    """Liveness check with backend status."""
    return {
        "status": "ready",
        "active_backend": active_backend,
        "available_backends": list(backends.keys())
    }


@app.get("/v1/backends")
def list_backends() -> Dict[str, Any]:
    """List all available backends with their status."""
    backend_info = {}
    for name, backend in backends.items():
        if name == "ollama":
            backend_info[name] = backend.get_device_info()
        else:
            backend_info[name] = {"backend": name, "available": True}
    return {"backends": backend_info, "active": active_backend}


@app.get("/v1/models")
def list_models() -> Dict[str, List[Dict[str, Any]]]:
    """List all available models across all backends."""
    models = []
    
    # Get models from each backend
    for backend_name, backend in backends.items():
        if backend_name == "ollama":
            ollama_models = backend.list_models()
            for model in ollama_models:
                models.append({
                    "id": model["name"],
                    "object": "model",
                    "backend": "ollama",
                    "size": model.get("size", 0)
                })
        elif backend_name == "llama-gpu":
            models.append({
                "id": "llama-base",
                "object": "model",
                "backend": "llama-gpu"
            })
    
    return {"data": models}


@app.post("/v1/completions")
def completions(
    req: CompletionRequest,
    authorization: Optional[str] = Header(None)
) -> Dict[str, Any]:
    """Text completion endpoint supporting multiple backends."""
    guard_api_key(authorization)
    
    # Determine which backend to use
    backend_name = req.backend or active_backend
    if backend_name not in backends:
        raise HTTPException(
            status_code=400,
            detail=f"Backend '{backend_name}' not available"
        )
    
    backend = backends[backend_name]
    
    try:
        # Generate text
        if backend_name == "ollama":
            text = backend.infer(
                prompt=req.prompt,
                model=req.model,
                max_tokens=req.max_tokens,
                temperature=req.temperature
            )
        else:
            text = backend.infer(
                req.prompt,
                max_tokens=req.max_tokens,
                temperature=req.temperature
            )
        
        now = int(time.time())
        return {
            "id": f"cmpl-{now}",
            "object": "text_completion",
            "created": now,
            "model": req.model or "default",
            "backend": backend_name,
            "choices": [
                {
                    "text": text,
                    "index": 0,
                    "logprobs": None,
                    "finish_reason": "stop"
                }
            ]
        }
    except Exception as e:
        logger.error(f"Completion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/chat/completions")
def chat_completions(
    req: ChatRequest,
    authorization: Optional[str] = Header(None)
) -> Dict[str, Any]:
    """Chat completion endpoint supporting multiple backends."""
    guard_api_key(authorization)
    
    # Determine which backend to use
    backend_name = req.backend or active_backend
    if backend_name not in backends:
        raise HTTPException(
            status_code=400,
            detail=f"Backend '{backend_name}' not available"
        )
    
    backend = backends[backend_name]
    
    try:
        # Convert messages
        messages = [{"role": m.role, "content": m.content} for m in req.messages]
        
        # Generate response
        if backend_name == "ollama":
            content = backend.chat(
                messages=messages,
                model=req.model,
                max_tokens=req.max_tokens,
                temperature=req.temperature
            )
        else:
            # For LlamaGPU, convert to simple prompt
            prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
            content = backend.infer(
                prompt,
                max_tokens=req.max_tokens,
                temperature=req.temperature
            )
        
        now = int(time.time())
        return {
            "id": f"chatcmpl-{now}",
            "object": "chat.completion",
            "created": now,
            "model": req.model or "default",
            "backend": backend_name,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": content
                    },
                    "finish_reason": "stop"
                }
            ]
        }
    except Exception as e:
        logger.error(f"Chat completion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/backend/switch")
def switch_backend(backend: str) -> Dict[str, str]:
    """Switch the active backend."""
    global active_backend
    
    if backend not in backends:
        raise HTTPException(
            status_code=400,
            detail=f"Backend '{backend}' not available"
        )
    
    active_backend = backend
    logger.info(f"Switched to backend: {backend}")
    return {"status": "ok", "active_backend": active_backend}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
