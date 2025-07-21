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

---

For detailed benchmarking instructions, see `scripts/benchmark.py` and the project README.
