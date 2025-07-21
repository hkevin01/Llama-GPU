import asyncio
import json
import logging
import os
import queue
import threading
import time
from collections import defaultdict, deque
from datetime import datetime
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from model_manager import ModelManager

# Import multi-GPU support
from multi_gpu import GPUConfig, MultiGPUInference, ParallelismStrategy

# Import quantization support
from quantization import (
    QuantizationCache,
    QuantizationConfig,
    QuantizationManager,
    QuantizationType,
    QuantizedInference,
)

# Configure logging
LOG_DIR = os.environ.get("LLAMA_GPU_LOG_DIR", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# API request/response logging
api_logger = logging.getLogger("api")
api_logger.setLevel(logging.INFO)
api_handler = logging.FileHandler(os.path.join(LOG_DIR, "api_requests.log"))
api_handler.setFormatter(logging.Formatter(
    "[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
))
api_logger.addHandler(api_handler)

# Batch processing logging
batch_logger = logging.getLogger("batch")
batch_logger.setLevel(logging.INFO)
batch_handler = logging.FileHandler(os.path.join(LOG_DIR, "batch_processing.log"))
batch_handler.setFormatter(logging.Formatter(
    "[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
))
batch_logger.addHandler(batch_handler)

# Error logging
error_logger = logging.getLogger("errors")
error_logger.setLevel(logging.ERROR)
error_handler = logging.FileHandler(os.path.join(LOG_DIR, "errors.log"))
error_handler.setFormatter(logging.Formatter(
    "[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
))
error_logger.addHandler(error_handler)

app = FastAPI(title="LLaMA GPU API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Security
security = HTTPBearer()
API_KEYS = {os.environ.get("LLAMA_GPU_API_KEY", "test-key")}
RATE_LIMIT = 60  # requests per minute
rate_limit_counter = defaultdict(lambda: {"count": 0, "reset_time": time.time()})

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials not in API_KEYS:
        error_logger.error(f"Invalid API key attempt: {credentials.credentials}")
        raise HTTPException(status_code=401, detail="Invalid API key")
    return credentials.credentials

def check_rate_limit(api_key: str):
    now = time.time()
    if now - rate_limit_counter[api_key]["reset_time"] >= 60:
        rate_limit_counter[api_key] = {"count": 0, "reset_time": now}
    
    rate_limit_counter[api_key]["count"] += 1
    if rate_limit_counter[api_key]["count"] > RATE_LIMIT:
        error_logger.warning(f"Rate limit exceeded for API key: {api_key}")
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

# Model manager
model_manager = ModelManager()

# Multi-GPU configuration
multi_gpu_config = GPUConfig(
    gpu_ids=[0, 1],  # Default to 2 GPUs
    strategy=ParallelismStrategy.TENSOR,
    tensor_parallel_size=2,
    pipeline_parallel_size=2,
    load_balancing="round_robin"
)
multi_gpu_inference = None  # Will be initialized when model is loaded

# Quantization configuration
quantization_config = QuantizationConfig(
    quantization_type=QuantizationType.INT8,
    dynamic=True,
    memory_efficient=True
)
quantization_manager = QuantizationManager(quantization_config)
quantization_cache = QuantizationCache()

# Request queues and batching
completion_queue = queue.Queue()
chat_queue = queue.Queue()
batch_workers = {}
batch_stats = {
    "total_batches": 0,
    "avg_batch_size": 0,
    "avg_processing_time": 0
}

class CompletionRequest(BaseModel):
    prompt: str
    max_tokens: int = 50
    model_name: Optional[str] = None
    revision: Optional[str] = None
    stream: bool = False

class ChatRequest(BaseModel):
    messages: List[Dict[str, str]]
    max_tokens: int = 50
    model_name: Optional[str] = None
    revision: Optional[str] = None
    stream: bool = False

class ModelLoadRequest(BaseModel):
    model_name: str
    revision: Optional[str] = None

class MultiGPUConfigRequest(BaseModel):
    gpu_ids: List[int]
    strategy: str = "tensor"  # tensor, pipeline, data, hybrid
    tensor_parallel_size: int = 2
    pipeline_parallel_size: int = 2
    data_parallel_size: int = 1
    load_balancing: str = "round_robin"  # round_robin, least_loaded, adaptive

class MultiGPUStatsRequest(BaseModel):
    include_metrics: bool = True

class QuantizationConfigRequest(BaseModel):
    quantization_type: str = "int8"  # int8, int4, fp16, bf16, dynamic, static
    dynamic: bool = True
    per_channel: bool = True
    symmetric: bool = True
    reduce_range: bool = True
    memory_efficient: bool = True
    preserve_accuracy: bool = True

class QuantizationStatsRequest(BaseModel):
    model_name: Optional[str] = None
    include_overall: bool = True

class QuantizationCacheRequest(BaseModel):
    model_name: str
    quantization_type: str = "int8"
    action: str = "cache"  # cache, load, clear

def log_api_request(endpoint: str, request_data: dict, response_data: dict, status_code: int):
    api_logger.info(f"API {endpoint}: {status_code} - Request: {request_data} - Response: {response_data}")

def log_batch_event(event_type: str, batch_id: str, details: dict):
    batch_logger.info(f"BATCH {event_type}: {batch_id} - {details}")

async def batch_worker(queue_name: str, queue_obj: queue.Queue):
    """Background worker for processing batched requests"""
    worker_id = f"{queue_name}_worker_{threading.current_thread().ident}"
    batch_logger.info(f"Starting batch worker: {worker_id}")
    
    while True:
        try:
            # Collect requests for batching
            batch_requests = []
            batch_start_time = time.time()
            
            # Wait for first request
            first_request = queue_obj.get(timeout=1)
            batch_requests.append(first_request)
            
            # Collect additional requests for 100ms
            try:
                while time.time() - batch_start_time < 0.1 and len(batch_requests) < 10:
                    request = queue_obj.get_nowait()
                    batch_requests.append(request)
            except queue.Empty:
                pass
            
            batch_id = f"{queue_name}_{int(time.time() * 1000)}"
            batch_size = len(batch_requests)
            
            log_batch_event("START", batch_id, {
                "worker_id": worker_id,
                "batch_size": batch_size,
                "requests": [r["prompt"][:50] + "..." for r in batch_requests]
            })
            
            # Process batch
            batch_start = time.time()
            try:
                # Load model if needed
                model_name = batch_requests[0].get("model_name")
                if model_name:
                    model = model_manager.load_model(model_name)
                else:
                    model = model_manager.get_default_model()
                
                # Process each request in batch
                results = []
                for req in batch_requests:
                    if queue_name == "completion":
                        result = model.generate(req["prompt"], req["max_tokens"])
                    else:  # chat
                        result = model.chat(req["messages"], req["max_tokens"])
                    results.append(result)
                
                batch_time = time.time() - batch_start
                
                # Update batch stats
                batch_stats["total_batches"] += 1
                batch_stats["total_requests"] += batch_size
                batch_stats["avg_batch_size"] = batch_stats["total_requests"] / batch_stats["total_batches"]
                batch_stats["avg_processing_time"] = (
                    (batch_stats["avg_processing_time"] * (batch_stats["total_batches"] - 1) + batch_time) 
                    / batch_stats["total_batches"]
                )
                
                log_batch_event("COMPLETE", batch_id, {
                    "worker_id": worker_id,
                    "batch_size": batch_size,
                    "processing_time": batch_time,
                    "results_count": len(results)
                })
                
                # Return results to callers
                for req, result in zip(batch_requests, results):
                    req["future"].set_result(result)
                    
            except Exception as e:
                error_logger.error(f"Batch processing error in {batch_id}: {str(e)}")
                log_batch_event("ERROR", batch_id, {
                    "worker_id": worker_id,
                    "error": str(e)
                })
                # Return error to all callers
                for req in batch_requests:
                    req["future"].set_exception(e)
                    
        except queue.Empty:
            continue
        except Exception as e:
            error_logger.error(f"Batch worker error in {worker_id}: {str(e)}")
            await asyncio.sleep(1)

# Start batch workers
def start_batch_workers():
    for queue_name, queue_obj in [("completion", completion_queue), ("chat", chat_queue)]:
        worker_thread = threading.Thread(
            target=lambda: asyncio.run(batch_worker(queue_name, queue_obj)),
            daemon=True
        )
        worker_thread.start()
        batch_workers[queue_name] = worker_thread

@app.on_event("startup")
async def startup_event():
    start_batch_workers()

@app.post("/v1/completions")
async def completions(request: CompletionRequest, api_key: str = Depends(verify_api_key)):
    check_rate_limit(api_key)
    
    try:
        if request.stream:
            # Streaming response
            return StreamingResponse(
                stream_completion(request.prompt, request.max_tokens, request.model_name),
                media_type="text/plain"
            )
        else:
            # Batch processing
            future = asyncio.Future()
            completion_queue.put({
                "prompt": request.prompt,
                "max_tokens": request.max_tokens,
                "model_name": request.model_name,
                "future": future
            })
            
            result = await future
            
            response_data = {
                "choices": [{"text": result}],
                "model": request.model_name or "llama-base"
            }
            
            log_api_request("/v1/completions", request.dict(), response_data, 200)
            return response_data
            
    except Exception as e:
        error_logger.error(f"Completion error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest, api_key: str = Depends(verify_api_key)):
    check_rate_limit(api_key)
    
    try:
        if request.stream:
            # Streaming response
            return StreamingResponse(
                stream_chat(request.messages, request.max_tokens, request.model_name),
                media_type="text/plain"
            )
        else:
            # Batch processing
            future = asyncio.Future()
            chat_queue.put({
                "messages": request.messages,
                "max_tokens": request.max_tokens,
                "model_name": request.model_name,
                "future": future
            })
            
            result = await future
            
            response_data = {
                "choices": [{"message": {"content": result, "role": "assistant"}}],
                "model": request.model_name or "llama-base"
            }
            
            log_api_request("/v1/chat/completions", request.dict(), response_data, 200)
            return response_data
            
    except Exception as e:
        error_logger.error(f"Chat completion error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/models/load")
async def load_model(request: ModelLoadRequest, api_key: str = Depends(verify_api_key)):
    check_rate_limit(api_key)
    
    try:
        model = model_manager.load_model(request.model_name, request.revision)
        response_data = {
            "status": "loaded",
            "model_name": request.model_name,
            "revision": request.revision
        }
        
        log_api_request("/v1/models/load", request.dict(), response_data, 200)
        return response_data
        
    except Exception as e:
        error_logger.error(f"Model load error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/multi-gpu/config")
async def set_multi_gpu_config(request: MultiGPUConfigRequest, api_key: str = Depends(verify_api_key)):
    check_rate_limit(api_key)
    
    try:
        multi_gpu_config.gpu_ids = request.gpu_ids
        multi_gpu_config.strategy = ParallelismStrategy(request.strategy)
        multi_gpu_config.tensor_parallel_size = request.tensor_parallel_size
        multi_gpu_config.pipeline_parallel_size = request.pipeline_parallel_size
        multi_gpu_config.data_parallel_size = request.data_parallel_size
        multi_gpu_config.load_balancing = request.load_balancing
        
        response_data = {
            "status": "config_updated",
            "multi_gpu_config": {
                "gpu_ids": multi_gpu_config.gpu_ids,
                "strategy": multi_gpu_config.strategy.value,
                "tensor_parallel_size": multi_gpu_config.tensor_parallel_size,
                "pipeline_parallel_size": multi_gpu_config.pipeline_parallel_size,
                "data_parallel_size": multi_gpu_config.data_parallel_size,
                "load_balancing": multi_gpu_config.load_balancing
            }
        }
        
        log_api_request("/v1/multi-gpu/config", request.dict(), response_data, 200)
        return response_data
        
    except Exception as e:
        error_logger.error(f"Multi-GPU config error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/multi-gpu/stats")
async def get_multi_gpu_stats(include_metrics: bool = True, api_key: str = Depends(verify_api_key)):
    check_rate_limit(api_key)
    
    try:
        stats = multi_gpu_inference.get_stats() if multi_gpu_inference else {}
        if not include_metrics:
            stats = {k: v for k, v in stats.items() if k not in ["metrics"]}
        
        response_data = {
            "status": "success",
            "multi_gpu_stats": stats
        }
        
        log_api_request("/v1/multi-gpu/stats", {"include_metrics": include_metrics}, response_data, 200)
        return response_data
        
    except Exception as e:
        error_logger.error(f"Multi-GPU stats error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/quantization/config")
async def set_quantization_config(request: QuantizationConfigRequest, api_key: str = Depends(verify_api_key)):
    check_rate_limit(api_key)
    
    try:
        # Update quantization configuration
        global quantization_config, quantization_manager
        
        quantization_type = QuantizationType(request.quantization_type)
        quantization_config = QuantizationConfig(
            quantization_type=quantization_type,
            dynamic=request.dynamic,
            per_channel=request.per_channel,
            symmetric=request.symmetric,
            reduce_range=request.reduce_range,
            memory_efficient=request.memory_efficient,
            preserve_accuracy=request.preserve_accuracy
        )
        
        quantization_manager = QuantizationManager(quantization_config)
        
        response_data = {
            "status": "config_updated",
            "quantization_config": {
                "quantization_type": quantization_config.quantization_type.value,
                "dynamic": quantization_config.dynamic,
                "per_channel": quantization_config.per_channel,
                "symmetric": quantization_config.symmetric,
                "reduce_range": quantization_config.reduce_range,
                "memory_efficient": quantization_config.memory_efficient,
                "preserve_accuracy": quantization_config.preserve_accuracy
            }
        }
        
        log_api_request("/v1/quantization/config", request.dict(), response_data, 200)
        return response_data
        
    except Exception as e:
        error_logger.error(f"Quantization config error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/quantization/stats")
async def get_quantization_stats(model_name: Optional[str] = None, include_overall: bool = True, api_key: str = Depends(verify_api_key)):
    check_rate_limit(api_key)
    
    try:
        response_data = {"status": "success"}
        
        if model_name:
            # Get stats for specific model
            model_stats = quantization_manager.get_quantization_stats(model_name)
            response_data["model_stats"] = model_stats
        
        if include_overall:
            # Get overall stats
            overall_stats = quantization_manager.get_overall_stats()
            response_data["overall_stats"] = overall_stats
        
        # Get cache stats
        cache_stats = quantization_cache.get_cache_stats()
        response_data["cache_stats"] = cache_stats
        
        log_api_request("/v1/quantization/stats", {"model_name": model_name, "include_overall": include_overall}, response_data, 200)
        return response_data
        
    except Exception as e:
        error_logger.error(f"Quantization stats error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/quantization/cache")
async def manage_quantization_cache(request: QuantizationCacheRequest, api_key: str = Depends(verify_api_key)):
    check_rate_limit(api_key)
    
    try:
        quantization_type = QuantizationType(request.quantization_type)
        
        if request.action == "cache":
            # Cache a quantized model
            model = model_manager.get_model(request.model_name)
            if model:
                quantized_model = quantization_manager.quantize_model(model, request.model_name)
                quantization_cache.cache_model(request.model_name, quantized_model, quantization_config)
                response_data = {"status": "cached", "model_name": request.model_name}
            else:
                raise HTTPException(status_code=404, detail=f"Model {request.model_name} not found")
        
        elif request.action == "load":
            # Load a cached quantized model
            cached_model = quantization_cache.load_cached_model(request.model_name, quantization_type)
            if cached_model:
                response_data = {"status": "loaded", "model_name": request.model_name}
            else:
                raise HTTPException(status_code=404, detail=f"Cached model {request.model_name} not found")
        
        elif request.action == "clear":
            # Clear cache (implementation would need to be added to QuantizationCache)
            response_data = {"status": "cache_cleared", "model_name": request.model_name}
        
        else:
            raise HTTPException(status_code=400, detail=f"Invalid action: {request.action}")
        
        log_api_request("/v1/quantization/cache", request.dict(), response_data, 200)
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        error_logger.error(f"Quantization cache error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/monitor/queues")
async def monitor_queues(api_key: str = Depends(verify_api_key)):
    check_rate_limit(api_key)
    
    response_data = {
        "completion_queues": {
            "size": completion_queue.qsize(),
            "workers": len([w for w in batch_workers if "completion" in w])
        },
        "chat_queues": {
            "size": chat_queue.qsize(),
            "workers": len([w for w in batch_workers if "chat" in w])
        }
    }
    
    log_api_request("/v1/monitor/queues", {}, response_data, 200)
    return response_data

@app.get("/v1/monitor/batches")
async def monitor_batches(api_key: str = Depends(verify_api_key)):
    check_rate_limit(api_key)
    
    response_data = {
        "batch_stats": batch_stats,
        "active_workers": len(batch_workers),
        "worker_status": {
            name: "running" if worker.is_alive() else "stopped"
            for name, worker in batch_workers.items()
        }
    }
    
    log_api_request("/v1/monitor/batches", {}, response_data, 200)
    return response_data

@app.get("/v1/monitor/workers")
async def monitor_workers(api_key: str = Depends(verify_api_key)):
    check_rate_limit(api_key)
    
    response_data = {
        "workers": {
            name: {
                "status": "running" if worker.is_alive() else "stopped",
                "thread_id": worker.ident,
                "daemon": worker.daemon
            }
            for name, worker in batch_workers.items()
        },
        "total_workers": len(batch_workers)
    }
    
    log_api_request("/v1/monitor/workers", {}, response_data, 200)
    return response_data

@app.websocket("/v1/stream")
async def websocket_stream(websocket: WebSocket):
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_text()
            request = json.loads(data)
            
            prompt = request.get("prompt", "")
            max_tokens = request.get("max_tokens", 50)
            model_name = request.get("model_name")
            
            # Load model
            if model_name:
                model = model_manager.load_model(model_name)
            else:
                model = model_manager.get_default_model()
            
            # Stream response
            for token in model.generate_stream(prompt, max_tokens):
                await websocket.send_text(token)
            
            await websocket.send_text("[END]")
            
    except WebSocketDisconnect:
        pass
    except Exception as e:
        error_logger.error(f"WebSocket error: {str(e)}")
        await websocket.close()

async def stream_completion(prompt: str, max_tokens: int, model_name: Optional[str]):
    """Stream completion tokens"""
    try:
        if model_name:
            model = model_manager.load_model(model_name)
        else:
            model = model_manager.get_default_model()
        
        for token in model.generate_stream(prompt, max_tokens):
            yield token
    except Exception as e:
        error_logger.error(f"Stream completion error: {str(e)}")
        yield f"Error: {str(e)}"

async def stream_chat(messages: List[Dict[str, str]], max_tokens: int, model_name: Optional[str]):
    """Stream chat completion tokens"""
    try:
        if model_name:
            model = model_manager.load_model(model_name)
        else:
            model = model_manager.get_default_model()
        
        for token in model.chat_stream(messages, max_tokens):
            yield token
    except Exception as e:
        error_logger.error(f"Stream chat error: {str(e)}")
        yield f"Error: {str(e)}"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)