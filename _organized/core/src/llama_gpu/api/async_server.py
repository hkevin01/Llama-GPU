"""Async FastAPI server for Llama-GPU advanced inference."""

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
import asyncio
from llama_gpu import LlamaGPU
from utils.memory import get_gpu_memory_usage, get_cpu_memory_usage
import logging

app = FastAPI()
llama = LlamaGPU("path/to/model", prefer_gpu=True)

logging.basicConfig(
    filename='logs/api_requests.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logging.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logging.info(f"Response status: {response.status_code}")
    return response

@app.post("/infer")
async def infer(request: Request):
    data = await request.json()
    input_text = data.get("input", "")
    result = await asyncio.to_thread(llama.infer, input_text)
    return JSONResponse({"result": result})

@app.post("/batch_infer")
async def batch_infer(request: Request):
    data = await request.json()
    inputs = data.get("inputs", [])
    batch_size = data.get("batch_size", None)
    results = await asyncio.to_thread(llama.batch_infer, inputs, batch_size)
    return JSONResponse({"results": results})

@app.post("/stream_infer")
async def stream_infer(request: Request):
    data = await request.json()
    input_text = data.get("input", "")
    max_tokens = data.get("max_tokens", None)
    def token_stream():
        for token in llama.stream_infer(input_text, max_tokens):
            yield token
    return StreamingResponse(token_stream(), media_type="text/plain")

@app.get("/monitor/memory")
async def monitor_memory():
    cpu_stats = get_cpu_memory_usage()
    gpu_stats = get_gpu_memory_usage()
    return JSONResponse({"cpu": cpu_stats, "gpu": gpu_stats})

@app.get("/monitor/gpu")
async def monitor_gpu():
    gpu_stats = get_gpu_memory_usage()
    return JSONResponse({"gpu": gpu_stats})
