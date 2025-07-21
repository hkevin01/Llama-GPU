# Llama-GPU Benchmarks

This document will summarize and visualize performance benchmarks for LLaMA inference on CPU, CUDA (NVIDIA GPU), and ROCm (AMD GPU) backends, both locally and on AWS GPU instances.

## Benchmark Methodology
- Use `scripts/benchmark.py` to measure average inference time over multiple runs
- Test on various hardware (CPU, NVIDIA GPU, AMD GPU)
- Compare local and AWS GPU instance results

## Results

| Backend      | Hardware         | Avg Inference Time (s) | Notes           |
|--------------|------------------|------------------------|-----------------|
| CPU          | ...              | ...                    | ...             |
| CUDA (GPU)   | ...              | ...                    | ...             |
| ROCm (GPU)   | ...              | ...                    | ...             |
| CUDA (AWS)   | ...              | ...                    | ...             |
| ROCm (AWS)   | ...              | ...                    | ...             |

## Visualizations

*(Add charts/plots here as results are collected)*

## Async API Benchmarking

- Run `scripts/benchmark_async.py` to benchmark async inference endpoints.
- Results are logged to `logs/test_output.log` for review and analysis.
- Includes timing for single and batch inference endpoints.

Example:
```bash
python scripts/benchmark_async.py
```

# Benchmark Documentation

This guide explains how to run and interpret benchmarks for Llama-GPU.

## Running Benchmarks

Use the provided script to benchmark model inference across backends:

```bash
python scripts/benchmark.py --model path/to/model --backend all --output-format json
```

### Options
- `--backend`: cpu, cuda, rocm, or all
- `--batch-size`: Batch size for testing
- `--output-format`: human, csv, or json

## Output
- Performance metrics (latency, throughput)
- GPU vs CPU speedup comparisons
- Token generation rates
- Memory usage statistics
- JSON/CSV export for further analysis

## Usage Examples
See `examples/text_generation.py`, `examples/code_generation.py`, and `examples/conversation_simulation.py` for real-world benchmarking.

---
_Last updated: July 21, 2025_

---

For detailed benchmarking instructions, see `scripts/benchmark.py` and the project README.
