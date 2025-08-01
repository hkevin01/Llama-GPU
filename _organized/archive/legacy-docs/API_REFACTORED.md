# API Documentation

## Document Information

- **Project**: LLaMA GPU
- **API Version**: v1.0
- **Last Updated**: August 1, 2025
- **Base URL**: `http://localhost:5000/api/v1`

## Table of Contents

- [1. Introduction](#1-introduction)
- [2. Authentication](#2-authentication)
- [3. Core Inference API](#3-core-inference-api)
- [4. Model Management API](#4-model-management-api)
- [5. Plugin Management API](#5-plugin-management-api)
- [6. System Monitoring API](#6-system-monitoring-api)
- [7. WebSocket API](#7-websocket-api)
- [8. Error Handling](#8-error-handling)
- [9. Rate Limiting](#9-rate-limiting)
- [10. SDK Examples](#10-sdk-examples)

## 1. Introduction

### 1.1 Overview

The LLaMA GPU API provides programmatic access to high-performance GPU-accelerated inference capabilities. The API supports both synchronous and asynchronous operations, batch processing, and real-time monitoring.

### 1.2 API Design Principles

- **RESTful**: Standard HTTP methods and status codes
- **JSON-First**: All requests and responses use JSON format
- **Stateless**: Each request contains all necessary information
- **Versioned**: Backward compatibility through API versioning
- **Documented**: OpenAPI 3.0 specification available

### 1.3 Base Configuration

**Default Endpoints:**
- **REST API**: `http://localhost:5000/api/v1`
- **WebSocket**: `ws://localhost:5000/socket.io`
- **Dashboard**: `http://localhost:5000`
- **Health Check**: `http://localhost:5000/health`

**Content Type:** `application/json`
**API Version Header:** `X-API-Version: 1.0`

## 2. Authentication

### 2.1 API Key Authentication

**Header Format:**
```http
Authorization: Bearer <api_key>
X-API-Key: <api_key>
```

**Example:**
```bash
curl -H "Authorization: Bearer your_api_key_here" \
     -H "Content-Type: application/json" \
     http://localhost:5000/api/v1/infer
```

### 2.2 Session Authentication

**Web Dashboard Login:**
```http
POST /api/v1/auth/login
Content-Type: application/json

{
    "username": "admin",
    "password": "your_password"
}
```

**Response:**
```json
{
    "success": true,
    "token": "jwt_token_here",
    "expires_in": 3600,
    "user": {
        "id": "admin",
        "role": "administrator",
        "permissions": ["read", "write", "admin"]
    }
}
```

### 2.3 Role-Based Access

**Permission Levels:**
- `read`: View system status and monitoring data
- `write`: Execute inference operations
- `admin`: Full system administration access

## 3. Core Inference API

### 3.1 Single Inference

#### `POST /api/v1/infer`

Execute inference on a single input.

**Request Body:**
```json
{
    "text": "Explain the concept of machine learning",
    "model": "llama2-7b",
    "max_tokens": 150,
    "temperature": 0.7,
    "top_p": 0.9,
    "stream": false
}
```

**Response:**
```json
{
    "success": true,
    "result": {
        "generated_text": "Machine learning is a subset of artificial intelligence...",
        "tokens_generated": 142,
        "inference_time": 0.85,
        "model_used": "llama2-7b",
        "backend": "cuda"
    },
    "metadata": {
        "request_id": "req_12345",
        "timestamp": "2025-01-01T12:00:00Z",
        "processing_time": 0.87
    }
}
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `text` | string | ✓ | - | Input text for inference |
| `model` | string | - | "default" | Model identifier |
| `max_tokens` | integer | - | 100 | Maximum tokens to generate |
| `temperature` | float | - | 1.0 | Sampling temperature (0.1-2.0) |
| `top_p` | float | - | 1.0 | Nucleus sampling parameter |
| `stream` | boolean | - | false | Enable streaming response |

### 3.2 Batch Inference

#### `POST /api/v1/batch_infer`

Process multiple inputs in a single request.

**Request Body:**
```json
{
    "inputs": [
        {
            "id": "req_1",
            "text": "What is artificial intelligence?",
            "max_tokens": 100
        },
        {
            "id": "req_2",
            "text": "Explain neural networks",
            "max_tokens": 150
        }
    ],
    "model": "llama2-7b",
    "temperature": 0.7
}
```

**Response:**
```json
{
    "success": true,
    "results": [
        {
            "id": "req_1",
            "generated_text": "Artificial intelligence (AI) refers to...",
            "tokens_generated": 95,
            "inference_time": 0.45
        },
        {
            "id": "req_2",
            "generated_text": "Neural networks are computational models...",
            "tokens_generated": 148,
            "inference_time": 0.67
        }
    ],
    "metadata": {
        "batch_id": "batch_12345",
        "total_processing_time": 1.23,
        "items_processed": 2,
        "backend": "cuda"
    }
}
```

### 3.3 Streaming Inference

#### `POST /api/v1/stream_infer`

Stream inference results as they are generated.

**Request Body:**
```json
{
    "text": "Write a story about space exploration",
    "model": "llama2-7b",
    "max_tokens": 200,
    "stream": true
}
```

**Response Format (Server-Sent Events):**
```
data: {"token": "Space", "position": 0, "is_complete": false}
data: {"token": " exploration", "position": 1, "is_complete": false}
...
data: {"token": ".", "position": 45, "is_complete": true, "final_text": "Complete generated text..."}
```

**cURL Example:**
```bash
curl -N -H "Authorization: Bearer your_api_key" \
     -H "Content-Type: application/json" \
     -d '{"text": "Tell me about AI", "stream": true}' \
     http://localhost:5000/api/v1/stream_infer
```

## 4. Model Management API

### 4.1 List Available Models

#### `GET /api/v1/models`

Retrieve information about available models.

**Response:**
```json
{
    "success": true,
    "models": [
        {
            "id": "llama2-7b",
            "name": "LLaMA 2 7B",
            "size": "7B",
            "type": "chat",
            "loaded": true,
            "memory_usage": "6.5GB",
            "backend": "cuda",
            "capabilities": ["text-generation", "chat"]
        },
        {
            "id": "llama2-13b",
            "name": "LLaMA 2 13B",
            "size": "13B",
            "type": "instruct",
            "loaded": false,
            "estimated_memory": "12.8GB",
            "capabilities": ["text-generation", "instruct"]
        }
    ],
    "total_models": 2,
    "loaded_models": 1
}
```

### 4.2 Load Model

#### `POST /api/v1/models/{model_id}/load`

Load a specific model into memory.

**Request Body:**
```json
{
    "backend": "cuda",
    "quantization": "fp16",
    "max_memory": "80%"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Model loaded successfully",
    "model": {
        "id": "llama2-13b",
        "loaded": true,
        "backend": "cuda",
        "memory_usage": "12.1GB",
        "load_time": 15.3
    }
}
```

### 4.3 Unload Model

#### `DELETE /api/v1/models/{model_id}/unload`

Remove a model from memory.

**Response:**
```json
{
    "success": true,
    "message": "Model unloaded successfully",
    "freed_memory": "12.1GB"
}
```

### 4.4 Model Information

#### `GET /api/v1/models/{model_id}`

Get detailed information about a specific model.

**Response:**
```json
{
    "success": true,
    "model": {
        "id": "llama2-7b",
        "name": "LLaMA 2 7B",
        "architecture": "LlamaForCausalLM",
        "parameters": 6738415616,
        "vocab_size": 32000,
        "context_length": 4096,
        "loaded": true,
        "backend": "cuda",
        "quantization": "fp16",
        "memory_usage": "6.5GB",
        "performance": {
            "tokens_per_second": 45.2,
            "avg_latency": 0.78,
            "total_requests": 1250
        }
    }
}
```

## 5. Plugin Management API

### 5.1 List Plugins

#### `GET /api/v1/plugins`

Retrieve information about available and loaded plugins.

**Response:**
```json
{
    "success": true,
    "plugins": [
        {
            "id": "model_adapter_v1",
            "name": "Model Adapter",
            "version": "1.0.0",
            "status": "loaded",
            "category": "preprocessing",
            "author": "LLaMA GPU Team",
            "description": "Adapts model inputs for optimal performance"
        },
        {
            "id": "response_filter",
            "name": "Response Filter",
            "version": "0.9.2",
            "status": "available",
            "category": "postprocessing",
            "author": "Community",
            "description": "Filters and validates model responses"
        }
    ],
    "total_plugins": 2,
    "loaded_plugins": 1
}
```

### 5.2 Load Plugin

#### `POST /api/v1/plugins/{plugin_id}/load`

Load and activate a plugin.

**Request Body:**
```json
{
    "config": {
        "enabled": true,
        "priority": 10,
        "settings": {
            "custom_param": "value"
        }
    }
}
```

**Response:**
```json
{
    "success": true,
    "message": "Plugin loaded successfully",
    "plugin": {
        "id": "response_filter",
        "status": "loaded",
        "load_time": 0.15,
        "config": {
            "enabled": true,
            "priority": 10
        }
    }
}
```

### 5.3 Unload Plugin

#### `DELETE /api/v1/plugins/{plugin_id}/unload`

Unload and deactivate a plugin.

**Response:**
```json
{
    "success": true,
    "message": "Plugin unloaded successfully",
    "plugin_id": "response_filter"
}
```

### 5.4 Plugin Configuration

#### `PUT /api/v1/plugins/{plugin_id}/config`

Update plugin configuration.

**Request Body:**
```json
{
    "config": {
        "enabled": true,
        "priority": 15,
        "settings": {
            "custom_param": "new_value",
            "additional_param": true
        }
    }
}
```

**Response:**
```json
{
    "success": true,
    "message": "Plugin configuration updated",
    "config": {
        "enabled": true,
        "priority": 15,
        "settings": {
            "custom_param": "new_value",
            "additional_param": true
        }
    }
}
```

## 6. System Monitoring API

### 6.1 System Status

#### `GET /api/v1/system/status`

Get overall system health and status.

**Response:**
```json
{
    "success": true,
    "status": "healthy",
    "uptime": 86400,
    "version": "1.0.0",
    "system": {
        "cpu_usage": 45.2,
        "memory_usage": 67.8,
        "disk_usage": 34.1,
        "gpu_count": 2,
        "gpu_usage": [89.1, 76.3],
        "gpu_memory": [78.5, 65.2]
    },
    "services": {
        "inference_engine": "running",
        "plugin_manager": "running",
        "web_dashboard": "running",
        "websocket_server": "running"
    },
    "statistics": {
        "total_requests": 15432,
        "successful_requests": 15401,
        "error_rate": 0.002,
        "avg_response_time": 0.85,
        "requests_per_minute": 42.3
    }
}
```

### 6.2 GPU Metrics

#### `GET /api/v1/system/gpu`

Get detailed GPU information and metrics.

**Response:**
```json
{
    "success": true,
    "gpu_count": 2,
    "gpus": [
        {
            "id": 0,
            "name": "NVIDIA RTX 4090",
            "driver_version": "535.104.12",
            "cuda_version": "12.2",
            "memory_total": 24576,
            "memory_used": 19276,
            "memory_free": 5300,
            "utilization": 89,
            "temperature": 72,
            "power_usage": 380,
            "power_limit": 450
        },
        {
            "id": 1,
            "name": "NVIDIA RTX 4090",
            "driver_version": "535.104.12",
            "cuda_version": "12.2",
            "memory_total": 24576,
            "memory_used": 16032,
            "memory_free": 8544,
            "utilization": 76,
            "temperature": 68,
            "power_usage": 340,
            "power_limit": 450
        }
    ]
}
```

### 6.3 Performance Metrics

#### `GET /api/v1/system/metrics`

Get detailed performance metrics.

**Query Parameters:**
- `timeframe`: `1h`, `6h`, `24h`, `7d` (default: `1h`)
- `granularity`: `1m`, `5m`, `15m`, `1h` (default: `5m`)

**Response:**
```json
{
    "success": true,
    "timeframe": "1h",
    "granularity": "5m",
    "metrics": {
        "timestamps": ["2025-01-01T11:00:00Z", "2025-01-01T11:05:00Z", "..."],
        "request_rate": [42.1, 38.7, 45.2, "..."],
        "response_time": [0.85, 0.92, 0.78, "..."],
        "error_rate": [0.001, 0.002, 0.001, "..."],
        "gpu_utilization": [
            [89.1, 76.3],
            [91.2, 78.1],
            [87.5, 74.9]
        ],
        "memory_usage": [67.8, 69.1, 65.4, "..."]
    }
}
```

### 6.4 Logs

#### `GET /api/v1/system/logs`

Retrieve system logs.

**Query Parameters:**
- `level`: `debug`, `info`, `warning`, `error` (default: `info`)
- `limit`: Maximum number of entries (default: 100)
- `since`: ISO timestamp for log filtering

**Response:**
```json
{
    "success": true,
    "logs": [
        {
            "timestamp": "2025-01-01T12:00:00Z",
            "level": "info",
            "component": "inference_engine",
            "message": "Model llama2-7b loaded successfully",
            "metadata": {
                "load_time": 2.3,
                "memory_usage": "6.5GB"
            }
        },
        {
            "timestamp": "2025-01-01T12:01:15Z",
            "level": "warning",
            "component": "plugin_manager",
            "message": "Plugin response_filter took longer than expected",
            "metadata": {
                "execution_time": 0.85,
                "threshold": 0.5
            }
        }
    ],
    "total_entries": 1250,
    "filtered_entries": 2
}
```

## 7. WebSocket API

### 7.1 Connection

Connect to the WebSocket server for real-time updates.

**Connection URL:** `ws://localhost:5000/socket.io`

**Authentication:**
```javascript
const socket = io('http://localhost:5000', {
    auth: {
        token: 'your_api_key_here'
    }
});
```

### 7.2 Event Types

#### System Monitoring Events

**Subscribe to monitoring data:**
```javascript
socket.emit('subscribe', {
    channels: ['system_metrics', 'gpu_metrics', 'inference_stats']
});
```

**Receive system metrics:**
```javascript
socket.on('system_metrics', (data) => {
    console.log('System metrics:', data);
    // {
    //     timestamp: '2025-01-01T12:00:00Z',
    //     cpu_usage: 45.2,
    //     memory_usage: 67.8,
    //     request_rate: 42.3
    // }
});
```

**Receive GPU metrics:**
```javascript
socket.on('gpu_metrics', (data) => {
    console.log('GPU metrics:', data);
    // {
    //     timestamp: '2025-01-01T12:00:00Z',
    //     gpu_id: 0,
    //     utilization: 89.1,
    //     memory_used: 19276,
    //     temperature: 72
    // }
});
```

#### Inference Events

**Subscribe to inference updates:**
```javascript
socket.emit('subscribe', {
    channels: ['inference_events']
});

socket.on('inference_started', (data) => {
    console.log('Inference started:', data.request_id);
});

socket.on('inference_completed', (data) => {
    console.log('Inference completed:', data.request_id, data.result);
});
```

#### Plugin Events

**Subscribe to plugin events:**
```javascript
socket.emit('subscribe', {
    channels: ['plugin_events']
});

socket.on('plugin_loaded', (data) => {
    console.log('Plugin loaded:', data.plugin_id);
});

socket.on('plugin_error', (data) => {
    console.log('Plugin error:', data.plugin_id, data.error);
});
```

### 7.3 Event Data Formats

**System Metrics Event:**
```json
{
    "event": "system_metrics",
    "timestamp": "2025-01-01T12:00:00Z",
    "data": {
        "cpu_usage": 45.2,
        "memory_usage": 67.8,
        "disk_usage": 34.1,
        "network_rx": 1024000,
        "network_tx": 512000,
        "active_requests": 12,
        "request_rate": 42.3
    }
}
```

**Inference Event:**
```json
{
    "event": "inference_completed",
    "timestamp": "2025-01-01T12:00:00Z",
    "data": {
        "request_id": "req_12345",
        "model": "llama2-7b",
        "tokens_generated": 142,
        "inference_time": 0.85,
        "queue_time": 0.02,
        "backend": "cuda"
    }
}
```

## 8. Error Handling

### 8.1 Error Response Format

All API errors follow a consistent format:

```json
{
    "success": false,
    "error": {
        "code": "INVALID_INPUT",
        "message": "Input text exceeds maximum length",
        "details": {
            "max_length": 4096,
            "provided_length": 5200,
            "field": "text"
        }
    },
    "request_id": "req_12345",
    "timestamp": "2025-01-01T12:00:00Z"
}
```

### 8.2 HTTP Status Codes

| Status Code | Meaning | Description |
|-------------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service temporarily unavailable |

### 8.3 Error Codes

| Error Code | Description | HTTP Status |
|------------|-------------|-------------|
| `INVALID_INPUT` | Request validation failed | 400 |
| `MODEL_NOT_FOUND` | Specified model not available | 404 |
| `MODEL_LOAD_FAILED` | Model loading failed | 500 |
| `INFERENCE_FAILED` | Inference execution failed | 500 |
| `PLUGIN_NOT_FOUND` | Plugin not available | 404 |
| `PLUGIN_LOAD_FAILED` | Plugin loading failed | 500 |
| `RATE_LIMIT_EXCEEDED` | Too many requests | 429 |
| `INSUFFICIENT_MEMORY` | Not enough GPU/CPU memory | 503 |
| `BACKEND_UNAVAILABLE` | Requested backend not available | 503 |
| `AUTHENTICATION_FAILED` | Invalid credentials | 401 |
| `PERMISSION_DENIED` | Insufficient permissions | 403 |

### 8.4 Error Handling Examples

**Handle validation errors:**
```python
import requests

response = requests.post('http://localhost:5000/api/v1/infer',
    json={'text': 'x' * 10000},  # Too long
    headers={'Authorization': 'Bearer your_api_key'}
)

if not response.ok:
    error_data = response.json()
    if error_data['error']['code'] == 'INVALID_INPUT':
        print(f"Input too long: {error_data['error']['details']['provided_length']}")
```

**Handle rate limiting:**
```python
import time
import requests

def make_request_with_retry(url, data, headers, max_retries=3):
    for attempt in range(max_retries):
        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 60))
            print(f"Rate limited, waiting {retry_after} seconds...")
            time.sleep(retry_after)
            continue

        return response

    raise Exception("Max retries exceeded")
```

## 9. Rate Limiting

### 9.1 Rate Limit Configuration

**Default Limits:**

| Endpoint | Authenticated | Unauthenticated |
|----------|---------------|-----------------|
| `/api/v1/infer` | 1000/hour | 100/hour |
| `/api/v1/batch_infer` | 100/hour | 10/hour |
| `/api/v1/stream_infer` | 500/hour | 50/hour |
| `/api/v1/system/*` | 6000/hour | 600/hour |
| `/api/v1/models/*` | 1000/hour | 100/hour |
| `/api/v1/plugins/*` | 500/hour | 50/hour |

### 9.2 Rate Limit Headers

**Response Headers:**
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 995
X-RateLimit-Reset: 1672531200
Retry-After: 3600
```

### 9.3 Rate Limit Bypass

**Premium API Keys:**
Premium users receive higher rate limits:
- 10x standard limits for inference endpoints
- 5x standard limits for management endpoints
- Priority queue processing

## 10. SDK Examples

### 10.1 Python SDK

**Installation:**
```bash
pip install llama-gpu-client
```

**Basic Usage:**
```python
from llama_gpu_client import LlamaGPUClient

# Initialize client
client = LlamaGPUClient(
    base_url='http://localhost:5000',
    api_key='your_api_key_here'
)

# Single inference
result = client.infer(
    text="Explain quantum computing",
    model="llama2-7b",
    max_tokens=200
)

print(result.generated_text)
print(f"Generated {result.tokens_generated} tokens in {result.inference_time}s")

# Batch inference
results = client.batch_infer([
    {"text": "What is AI?", "max_tokens": 100},
    {"text": "Explain machine learning", "max_tokens": 150}
])

for result in results:
    print(f"Result {result.id}: {result.generated_text}")

# Streaming inference
for token in client.stream_infer("Write a story", max_tokens=300):
    print(token.text, end='', flush=True)

# Model management
models = client.list_models()
for model in models:
    print(f"{model.name}: {'Loaded' if model.loaded else 'Available'}")

client.load_model("llama2-13b")
client.unload_model("llama2-7b")

# System monitoring
status = client.get_system_status()
print(f"System health: {status.status}")
print(f"GPU usage: {status.gpu_usage}")
```

### 10.2 JavaScript/Node.js SDK

**Installation:**
```bash
npm install llama-gpu-client
```

**Basic Usage:**
```javascript
const { LlamaGPUClient } = require('llama-gpu-client');

// Initialize client
const client = new LlamaGPUClient({
    baseUrl: 'http://localhost:5000',
    apiKey: 'your_api_key_here'
});

// Single inference
async function runInference() {
    try {
        const result = await client.infer({
            text: "Explain artificial intelligence",
            model: "llama2-7b",
            maxTokens: 200
        });

        console.log(result.generatedText);
        console.log(`Generated ${result.tokensGenerated} tokens`);
    } catch (error) {
        console.error('Inference failed:', error.message);
    }
}

// Streaming inference
async function streamInference() {
    const stream = client.streamInfer({
        text: "Write a short story",
        maxTokens: 300
    });

    for await (const token of stream) {
        process.stdout.write(token.text);
    }
}

// WebSocket monitoring
const socket = client.createSocket();

socket.on('connect', () => {
    console.log('Connected to WebSocket');
    socket.emit('subscribe', { channels: ['system_metrics'] });
});

socket.on('system_metrics', (data) => {
    console.log('System metrics:', data);
});

runInference();
```

### 10.3 cURL Examples

**Single Inference:**
```bash
curl -X POST "http://localhost:5000/api/v1/infer" \
     -H "Authorization: Bearer your_api_key" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "Explain machine learning",
       "model": "llama2-7b",
       "max_tokens": 150,
       "temperature": 0.7
     }'
```

**Batch Inference:**
```bash
curl -X POST "http://localhost:5000/api/v1/batch_infer" \
     -H "Authorization: Bearer your_api_key" \
     -H "Content-Type: application/json" \
     -d '{
       "inputs": [
         {"id": "1", "text": "What is AI?", "max_tokens": 100},
         {"id": "2", "text": "Explain neural networks", "max_tokens": 150}
       ],
       "model": "llama2-7b"
     }'
```

**System Status:**
```bash
curl -X GET "http://localhost:5000/api/v1/system/status" \
     -H "Authorization: Bearer your_api_key"
```

**Load Model:**
```bash
curl -X POST "http://localhost:5000/api/v1/models/llama2-13b/load" \
     -H "Authorization: Bearer your_api_key" \
     -H "Content-Type: application/json" \
     -d '{
       "backend": "cuda",
       "quantization": "fp16"
     }'
```

---

**API Status**: ✅ Production Ready
**OpenAPI Spec**: Available at `/api/v1/docs`
**Postman Collection**: Available in `/docs/api/`
**Last Updated**: August 1, 2025
