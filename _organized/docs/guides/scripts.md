# Scripts & Utilities

## Setup Scripts
- `scripts/setup_local.sh`: Set up local Python environment and dependencies
- `scripts/setup_aws.sh`: Set up AWS environment and dependencies

## Model Download
- `scripts/download_model.sh`: Download LLaMA model weights from HuggingFace or Meta

## Monitoring
- `scripts/monitor_resources.py`: Monitor CPU and memory usage during inference

## Logging
- `src/utils/logging.py`: Unified logging utility for all modules

## Usage Example
To download a model and run inference:
```bash
./scripts/download_model.sh <model_name> ./models
python -m src.llama_gpu --model_path ./models/<model_name> --input "Hello, world!"
```

---

For more details, see the README and code comments in each script.
