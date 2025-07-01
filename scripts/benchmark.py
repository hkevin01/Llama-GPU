import time
from llama_gpu import LlamaGPU

def benchmark(model_path, input_text, n=10):
    llama = LlamaGPU(model_path=model_path, prefer_gpu=True)
    times = []
    for _ in range(n):
        start = time.time()
        _ = llama.infer(input_text)
        times.append(time.time() - start)
    print(f"Average inference time over {n} runs: {sum(times)/n:.4f} seconds")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python benchmark.py <model_path> <input_text>")
        exit(1)
    benchmark(sys.argv[1], sys.argv[2])
