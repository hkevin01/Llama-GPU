import logging
import os

import httpx
import pytest

LOG_DIR = os.environ.get("LLAMA_GPU_LOG_DIR", "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "test_api_server.log")
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("test_api_server")

API_URL = os.environ.get("LLAMA_GPU_API_URL", "http://localhost:8000")
API_KEY = os.environ.get("LLAMA_GPU_API_KEY", "test-key")

@pytest.mark.asyncio
async def test_completions():
    payload = {
        "prompt": "Hello, world!",
        "max_tokens": 8,
        "model_name": None,
        "stream": False
    }
    headers = {"x-api-key": API_KEY}
    logger.info(f"Request: POST {API_URL}/v1/completions {payload}")
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{API_URL}/v1/completions", json=payload, headers=headers)
        logger.info(f"Response: {response.status_code} {response.text}")
        assert response.status_code == 200
        data = response.json()
        assert "choices" in data
        assert "text" in data["choices"][0] 