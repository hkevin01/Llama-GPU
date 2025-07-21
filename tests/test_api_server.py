import logging
import os
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from src.api_server import app

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

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def auth_headers():
    return {"Authorization": f"Bearer {API_KEY}"}

def test_completions(client):
    payload = {
        "prompt": "Hello, world!",
        "max_tokens": 8,
        "model_name": None,
        "stream": False
    }
    headers = auth_headers()
    logger.info(f"Request: POST /v1/completions {payload}")
    response = client.post("/v1/completions", json=payload, headers=headers)
    logger.info(f"Response: {response.status_code} {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert "choices" in data
    assert "text" in data["choices"][0]

def test_completions_stream(client):
    payload = {
        "prompt": "Hello, world!",
        "max_tokens": 8,
        "model_name": None,
        "stream": True
    }
    headers = auth_headers()
    logger.info(f"Request: POST /v1/completions (stream) {payload}")
    response = client.post("/v1/completions", json=payload, headers=headers)
    logger.info(f"Streaming Response: {response.status_code} {response.text}")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert len(response.text.strip()) > 0

def test_chat_completions(client):
    payload = {
        "messages": [
            {"role": "user", "content": "What is the capital of France?"}
        ],
        "max_tokens": 8,
        "model_name": None,
        "stream": False
    }
    headers = auth_headers()
    logger.info(f"Request: POST /v1/chat/completions {payload}")
    response = client.post("/v1/chat/completions", json=payload, headers=headers)
    logger.info(f"Response: {response.status_code} {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert "choices" in data
    assert "message" in data["choices"][0]
    assert "content" in data["choices"][0]["message"]

def test_chat_completions_stream(client):
    payload = {
        "messages": [
            {"role": "user", "content": "What is the capital of France?"}
        ],
        "max_tokens": 8,
        "model_name": None,
        "stream": True
    }
    headers = auth_headers()
    logger.info(f"Request: POST /v1/chat/completions (stream) {payload}")
    response = client.post("/v1/chat/completions", json=payload, headers=headers)
    logger.info(f"Streaming Response: {response.status_code} {response.text}")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert len(response.text.strip()) > 0

def test_model_load(client):
    payload = {
        "model_name": "llama-base",
        "revision": None
    }
    headers = auth_headers()
    logger.info(f"Request: POST /v1/models/load {payload}")
    response = client.post("/v1/models/load", json=payload, headers=headers)
    logger.info(f"Response: {response.status_code} {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "loaded"
    assert data["model_name"] == "llama-base"

def test_monitor_queues(client):
    headers = auth_headers()
    logger.info(f"Request: GET /v1/monitor/queues")
    response = client.get("/v1/monitor/queues", headers=headers)
    logger.info(f"Response: {response.status_code} {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert "completion_queues" in data
    assert "chat_queues" in data

def test_monitor_batches(client):
    headers = auth_headers()
    logger.info(f"Request: GET /v1/monitor/batches")
    response = client.get("/v1/monitor/batches", headers=headers)
    logger.info(f"Response: {response.status_code} {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert "batch_stats" in data
    assert "active_workers" in data

def test_monitor_workers(client):
    headers = auth_headers()
    logger.info(f"Request: GET /v1/monitor/workers")
    response = client.get("/v1/monitor/workers", headers=headers)
    logger.info(f"Response: {response.status_code} {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert "workers" in data
    assert "total_workers" in data

def test_invalid_api_key(client):
    payload = {"prompt": "test", "max_tokens": 8, "model_name": None, "stream": False}
    headers = {"Authorization": "Bearer invalid-key"}
    logger.info(f"Request: POST /v1/completions (invalid key) {payload}")
    response = client.post("/v1/completions", json=payload, headers=headers)
    logger.info(f"Response: {response.status_code} {response.text}")
    assert response.status_code == 401

def test_rate_limit(client):
    payload = {"prompt": "test", "max_tokens": 8, "model_name": None, "stream": False}
    headers = auth_headers()
    logger.info(f"Request: POST /v1/completions (rate limit test) {payload}")
    responses = []
    for _ in range(65):
        response = client.post("/v1/completions", json=payload, headers=headers)
        responses.append(response)
        if response.status_code == 429:
            break
    logger.info(f"Rate limit responses: {[r.status_code for r in responses]}")
    assert any(r.status_code == 429 for r in responses) 