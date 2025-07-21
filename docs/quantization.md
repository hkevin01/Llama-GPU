# Quantization Support in Llama-GPU

Llama-GPU now supports model quantization for efficient inference on CPU and GPU backends.

## Features
- Dynamic quantization (int8) for linear layers
- Float16 quantization for GPU acceleration
- Easily configurable via the main interface

## Usage
```python
from llama_gpu import LlamaGPU
llama = LlamaGPU(model_path="path/to/model", prefer_gpu=True, quant_type="int8")
result = llama.infer("Hello, world!")
```

## Supported Quantization Types
- `int8`: Dynamic quantization for CPU (reduces memory and speeds up inference)
- `float16`: Half-precision for GPU (reduces memory, increases throughput)

## Extending Quantization
You can add more quantization types in `src/utils/quantization.py` as needed.

## Limitations
- Quantization may affect model accuracy.
- Not all layers or models support all quantization types.

## References
- [PyTorch Quantization Documentation](https://pytorch.org/docs/stable/quantization.html)
- [HuggingFace Transformers Quantization](https://huggingface.co/docs/transformers/main_classes/quantization)
