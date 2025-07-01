# Usage Guide: Llama-GPU

## Setup
1. Clone the repository and install dependencies:
   ```bash
   git clone <repo-url>
   cd Llama-GPU
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. (Optional) Install GPU drivers and CUDA/ROCm as needed for your hardware.

## Download Model
Use the provided script to download LLaMA weights:
```bash
./scripts/download_model.sh <model_name> ./models
```

## Run Inference
Example usage from Python:
```python
from llama_gpu import LlamaGPU
llama = LlamaGPU(model_path="./models/<model_name>", prefer_gpu=True)
result = llama.infer("Hello, world!")
print(result)
```

Or from the command line (see `scripts/benchmark.py` for batch runs).

## AWS Setup
- Use `scripts/setup_aws.sh` to prepare an AWS GPU instance.
- Ensure correct drivers and permissions for GPU access.

---
For more details, see the API docs and example scripts.
