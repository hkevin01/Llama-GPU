"""Tests for async FastAPI resource monitoring endpoints."""
import httpx
import asyncio

def log_test_result(test_name, result):
    with open('logs/test_output.log', 'a') as f:
        f.write(f"{test_name}: {result}\n")

async def test_monitor_memory():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/monitor/memory")
        result = response.status_code == 200 and "cpu" in response.json()
        log_test_result('test_monitor_memory', result)
        assert result

async def test_monitor_gpu():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/monitor/gpu")
        result = response.status_code == 200 and "gpu" in response.json()
        log_test_result('test_monitor_gpu', result)
        assert result

if __name__ == "__main__":
    asyncio.run(test_monitor_memory())
    asyncio.run(test_monitor_gpu())
