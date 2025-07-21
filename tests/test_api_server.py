import asyncio
import logging
import os
from unittest.mock import Mock, patch

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

# Mock model for testing
class MockModel:
    def __init__(self, name="llama-base"):
        self.name = name
    
    def generate(self, prompt, max_tokens):
        return f"Mock response to: {prompt[:20]}..."
    
    def chat(self, messages, max_tokens):
        return f"Mock chat response to: {messages[-1]['content'][:20]}..."
    
    def generate_stream(self, prompt, max_tokens):
        tokens = [f"Mock", " response", " to:", f" {prompt[:10]}", "..."]
        for token in tokens:
            yield token
    
    def chat_stream(self, messages, max_tokens):
        tokens = [f"Mock", " chat", " response", "..."]
        for token in tokens:
            yield token

class MockModelManager:
    def __init__(self):
        self.models = {}
    
    def load_model(self, model_name, revision=None):
        if model_name not in self.models:
            self.models[model_name] = MockModel(model_name)
        return self.models[model_name]
    
    def get_default_model(self):
        return MockModel("llama-base")

@pytest.fixture(autouse=True)
def mock_model_manager():
    """Mock the model manager for all tests"""
    mock_manager = MockModelManager()
    with patch('src.api_server.ModelManager', MockModelManager):
        with patch('src.api_server.model_manager', mock_manager):
            yield

@pytest.mark.asyncio
async def test_completions():
    payload = {
        "prompt": "Hello, world!",
        "max_tokens": 8,
        "model_name": None,
        "stream": False
    }
    headers = {"Authorization": f"Bearer {API_KEY}"}
    logger.info(f"Request: POST {API_URL}/v1/completions {payload}")
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{API_URL}/v1/completions", json=payload, headers=headers)
        logger.info(f"Response: {response.status_code} {response.text}")
        assert response.status_code == 200
        data = response.json()
        assert "choices" in data
        assert "text" in data["choices"][0]

@pytest.mark.asyncio
async def test_completions_stream():
    payload = {
        "prompt": "Hello, world!",
        "max_tokens": 8,
        "model_name": None,
        "stream": True
    }
    headers = {"Authorization": f"Bearer {API_KEY}"}
    logger.info(f"Request: POST {API_URL}/v1/completions (stream) {payload}")
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(f"{API_URL}/v1/completions", json=payload, headers=headers)
        logger.info(f"Streaming Response: {response.status_code} {response.text}")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/plain")
        assert len(response.text.strip()) > 0

@pytest.mark.asyncio
async def test_chat_completions():
    payload = {
        "messages": [
            {"role": "user", "content": "What is the capital of France?"}
        ],
        "max_tokens": 8,
        "model_name": None,
        "stream": False
    }
    headers = {"Authorization": f"Bearer {API_KEY}"}
    logger.info(f"Request: POST {API_URL}/v1/chat/completions {payload}")
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{API_URL}/v1/chat/completions", json=payload, headers=headers)
        logger.info(f"Response: {response.status_code} {response.text}")
        assert response.status_code == 200
        data = response.json()
        assert "choices" in data
        assert "message" in data["choices"][0]
        assert "content" in data["choices"][0]["message"]

@pytest.mark.asyncio
async def test_chat_completions_stream():
    payload = {
        "messages": [
            {"role": "user", "content": "What is the capital of France?"}
        ],
        "max_tokens": 8,
        "model_name": None,
        "stream": True
    }
    headers = {"Authorization": f"Bearer {API_KEY}"}
    logger.info(f"Request: POST {API_URL}/v1/chat/completions (stream) {payload}")
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(f"{API_URL}/v1/chat/completions", json=payload, headers=headers)
        logger.info(f"Streaming Response: {response.status_code} {response.text}")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/plain")
        assert len(response.text.strip()) > 0

@pytest.mark.asyncio
async def test_model_load():
    payload = {
        "model_name": "llama-base",
        "revision": None
    }
    headers = {"Authorization": f"Bearer {API_KEY}"}
    logger.info(f"Request: POST {API_URL}/v1/models/load {payload}")
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{API_URL}/v1/models/load", json=payload, headers=headers)
        logger.info(f"Response: {response.status_code} {response.text}")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "loaded"
        assert data["model_name"] == "llama-base"

@pytest.mark.asyncio
async def test_monitor_queues():
    headers = {"Authorization": f"Bearer {API_KEY}"}
    logger.info(f"Request: GET {API_URL}/v1/monitor/queues")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_URL}/v1/monitor/queues", headers=headers)
        logger.info(f"Response: {response.status_code} {response.text}")
        assert response.status_code == 200
        data = response.json()
        assert "completion_queues" in data
        assert "chat_queues" in data

@pytest.mark.asyncio
async def test_monitor_batches():
    headers = {"Authorization": f"Bearer {API_KEY}"}
    logger.info(f"Request: GET {API_URL}/v1/monitor/batches")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_URL}/v1/monitor/batches", headers=headers)
        logger.info(f"Response: {response.status_code} {response.text}")
        assert response.status_code == 200
        data = response.json()
        assert "batch_stats" in data
        assert "active_workers" in data

@pytest.mark.asyncio
async def test_monitor_workers():
    headers = {"Authorization": f"Bearer {API_KEY}"}
    logger.info(f"Request: GET {API_URL}/v1/monitor/workers")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_URL}/v1/monitor/workers", headers=headers)
        logger.info(f"Response: {response.status_code} {response.text}")
        assert response.status_code == 200
        data = response.json()
        assert "workers" in data
        assert "total_workers" in data

@pytest.mark.asyncio
async def test_websocket_stream():
    try:
        import websockets
        uri = API_URL.replace("http", "ws") + "/v1/stream"
        payload = {"prompt": "Hello, world!", "max_tokens": 8, "model_name": None, "revision": None}
        logger.info(f"WebSocket connect: {uri} payload={payload}")
        async with websockets.connect(uri) as ws:
            await ws.send(httpx._models.json.dumps(payload))
            tokens = []
            while True:
                msg = await ws.recv()
                logger.info(f"WebSocket received: {msg}")
                if msg == "[END]":
                    break
                tokens.append(msg)
            assert len(tokens) > 0
    except ImportError:
        logger.warning("websockets not available, skipping WebSocket test")
        pytest.skip("websockets not available")

@pytest.mark.asyncio
async def test_invalid_api_key():
    payload = {"prompt": "test", "max_tokens": 8, "model_name": None, "stream": False}
    headers = {"Authorization": "Bearer invalid-key"}
    logger.info(f"Request: POST {API_URL}/v1/completions (invalid key) {payload}")
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{API_URL}/v1/completions", json=payload, headers=headers)
        logger.info(f"Response: {response.status_code} {response.text}")
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_rate_limit():
    payload = {"prompt": "test", "max_tokens": 8, "model_name": None, "stream": False}
    headers = {"Authorization": f"Bearer {API_KEY}"}
    logger.info(f"Request: POST {API_URL}/v1/completions (rate limit test) {payload}")
    async with httpx.AsyncClient() as client:
        # Exceed the rate limit quickly
        responses = []
        for _ in range(65):
            response = await client.post(f"{API_URL}/v1/completions", json=payload, headers=headers)
            responses.append(response)
            if response.status_code == 429:
                break
        logger.info(f"Rate limit responses: {[r.status_code for r in responses]}")
        assert any(r.status_code == 429 for r in responses) 