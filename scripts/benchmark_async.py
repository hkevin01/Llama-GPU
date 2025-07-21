"""Benchmark script for async inference endpoints in Llama-GPU."""

import httpx
import asyncio
import time

API_URL = "http://localhost:8000"

def log_benchmark_result(test_name, result):
    with open('logs/test_output.log', 'a') as f:
        f.write(f"{test_name}: {result}\n")

async def benchmark_infer():
    payload = {"input": "Hello, world!"}
    async with httpx.AsyncClient() as client:
        start = time.time()
        response = await client.post(f"{API_URL}/infer", json=payload)
        duration = time.time() - start
        result = response.json()
        log_benchmark_result('benchmark_infer', f"{result} (Time: {duration:.3f}s)")
        print(f"Infer response: {result} (Time: {duration:.3f}s)")

async def benchmark_batch_infer():
    payload = {"inputs": ["A", "B", "C"], "batch_size": 2}
    async with httpx.AsyncClient() as client:
        start = time.time()
        response = await client.post(f"{API_URL}/batch_infer", json=payload)
        duration = time.time() - start
        result = response.json()
        log_benchmark_result('benchmark_batch_infer', f"{result} (Time: {duration:.3f}s)")
        print(f"Batch response: {result} (Time: {duration:.3f}s)")

async def main():
    await benchmark_infer()
    await benchmark_batch_infer()

if __name__ == "__main__":
    asyncio.run(main())
