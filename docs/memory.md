# Memory Management in Llama-GPU

Llama-GPU provides utilities to monitor and report memory usage for both GPU and CPU backends.

## Features
- GPU memory usage reporting (CUDA)
- CPU memory usage reporting
- Integrated with backend and main interface

## Usage
```python
from llama_gpu import LlamaGPU
llama = LlamaGPU(model_path="path/to/model")
mem_stats = llama.get_memory_usage()
print(mem_stats)
```

## Implementation
- See `src/utils/memory.py` for utility functions.
- Backends expose `get_memory_usage()` for unified reporting.

## Notes
- GPU memory stats require CUDA and PyTorch support.
- CPU stats use `psutil` for cross-platform compatibility.

## References
- [PyTorch CUDA Memory Management](https://pytorch.org/docs/stable/cuda.html)
- [psutil Documentation](https://psutil.readthedocs.io/en/latest/)
