"""Minimal FastAPI server with OpenAI-style endpoints and WS stream.

Stable baseline that works on CPU and powers the React GUI for demos/tests.
"""

import os
import time
from typing import Dict, List, Optional

from fastapi import FastAPI, Header, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.llama_gpu import LlamaGPU

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*")
REQUIRE_API_KEY = os.getenv("REQUIRE_API_KEY", "false").lower() == "true"
API_KEY = os.getenv("API_KEY", "")

app = FastAPI(title="Llama-GPU API", version="0.1.0")

if ALLOWED_ORIGINS == "*":
    allow_origins = ["*"]
else:
    allow_origins = [
        o.strip() for o in ALLOWED_ORIGINS.split(",") if o.strip()
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = LlamaGPU(model_path=None, prefer_gpu=True)


def guard_api_key(authorization: Optional[str]) -> None:
    if not REQUIRE_API_KEY:
        return
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing API key")
    token = authorization.split(" ", 1)[1].strip()
    if token != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")


class CompletionRequest(BaseModel):
    model: Optional[str] = "llama-base"
    prompt: str
    max_tokens: int = 128
    temperature: float = 0.7


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: Optional[str] = "llama-base"
    messages: List[ChatMessage]
    max_tokens: int = 128
    temperature: float = 0.7


@app.get("/healthz")
def healthz() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/livez")
def livez() -> Dict[str, str]:
    return {"status": "ready"}


@app.get("/v1/models")
def list_models() -> Dict[str, List[Dict[str, str]]]:
    return {"data": [{"id": "llama-base", "object": "model"}]}


@app.post("/v1/models/load")
def load_model(path: str, name: Optional[str] = None) -> Dict[str, str]:
    # Stub: accept and respond OK
    return {"status": "loaded", "name": name or "llama-base", "path": path}


@app.post("/v1/completions")
def completions(
    req: CompletionRequest, authorization: Optional[str] = Header(None)
) -> Dict[str, object]:
    guard_api_key(authorization)
    text = engine.infer(
        req.prompt, max_tokens=req.max_tokens, temperature=req.temperature
    )
    now = int(time.time())
    return {
        "id": f"cmpl-{now}",
        "object": "text_completion",
        "created": now,
        "model": req.model,
        "choices": [
            {
                "text": text,
                "index": 0,
                "logprobs": None,
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": len(req.prompt.split()),
            "completion_tokens": len(text.split()),
            "total_tokens": len(req.prompt.split()) + len(text.split()),
        },
    }


@app.post("/v1/chat/completions")
def chat_completions(
    req: ChatRequest, authorization: Optional[str] = Header(None)
) -> Dict[str, object]:
    guard_api_key(authorization)
    prompt = "\n".join([f"{m.role}: {m.content}" for m in req.messages])
    text = engine.infer(
        prompt, max_tokens=req.max_tokens, temperature=req.temperature
    )
    now = int(time.time())
    return {
        "id": f"chatcmpl-{now}",
        "object": "chat.completion",
        "created": now,
        "model": req.model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": text},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": len(prompt.split()),
            "completion_tokens": len(text.split()),
            "total_tokens": len(prompt.split()) + len(text.split()),
        },
    }


@app.websocket("/v1/stream")
async def stream(ws: WebSocket) -> None:
    await ws.accept()
    try:
        init = await ws.receive_text()
        prompt = init
        # optional: initial JSON with {"prompt": "..."} can be added later
        for token in engine.stream_infer(prompt):
            await ws.send_text(token)
        await ws.close()
    except WebSocketDisconnect:
        pass


if __name__ == "__main__":
    import uvicorn

    reload_flag = os.getenv("ENV_DEV_RELOAD", "true").lower() == "true"
    uvicorn.run("src.api_server:app", host=HOST, port=PORT, reload=reload_flag)
