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

---
For usage examples, see `examples/` and the user guide.
