# API Documentation: Llama-GPU

## Backends
- `Backend` (abstract): `load_model(model_path)`, `infer(input_data)`, `is_available()`
- `CPUBackend`, `CUDABackend`, `ROCMBackend`: Implement the above interface

## Main Interface
- `LlamaGPU(model_path: str, prefer_gpu: bool = True)`
  - Selects the best backend and loads the model
  - `.infer(input_data)`: Run inference on input text

## Utilities
- Logging: `src/utils/logging.py`
- Resource monitoring: `scripts/monitor_resources.py`

## Async API Endpoints (FastAPI)

### POST /infer
- Single inference (async)
- Request: `{ "input": "text" }`
- Response: `{ "result": "output" }`

### POST /batch_infer
- Batch inference (async)
- Request: `{ "inputs": ["text1", "text2"], "batch_size": 2 }`
- Response: `{ "results": ["output1", "output2"] }`

### POST /stream_infer
- Streaming inference (async)
- Request: `{ "input": "text", "max_tokens": 10 }`
- Response: Streaming tokens (plain text)

### GET /monitor/memory
- Returns current CPU and GPU memory usage
- Response: `{ "cpu": { ... }, "gpu": { ... } }`

### GET /monitor/gpu
- Returns current GPU memory usage
- Response: `{ "gpu": { ... } }`

## API Request Logging

- All incoming requests and responses to the async API server are logged in `logs/api_requests.log`.
- Middleware automatically records method, URL, and response status for every request.

All endpoints are documented and tested. Test outputs are logged in `logs/test_output.log`.

---
For usage examples, see `examples/` and the user guide.
