#!/usr/bin/env python3
"""
Mock API Server for LLaMA-GPU C    logger.warning(f"ROCm backend import failed: {e}")


# Determine and log the backend being used
if HAS_CUDA:
    BACKEND = "cuda"
elif HAS_ROCM:
    BACKEND = "rocm"
else:
    BACKEND = "cpu"

if not HAS_CUDA and not HAS_ROCM:
    logger.warning("⚠️  No GPU acceleration available, running in CPU mode")
    logger.info("For GPU acceleration:")
    logger.info("  • NVIDIA: Install CUDA and run "
                "'pip install cudf-cu11 numba'")
    logger.info("  • AMD: Install ROCm and run 'pip install torch "
               "--index-url https://download.pytorch.org/whl/rocm5.4.2'")

logger.info("Creating FastAPI application...")


def create_app():erface Testing
Provides WebSocket and HTTP streaming endpoints for testing the real-time chat
"""

import argparse
import asyncio
import json
import logging
import os
import socket
import sys
import time
import traceback
from contextlib import closing
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

# Configure logging first
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("mock_api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import GPU backends with improved error handling
# For AMD/ROCm systems, check ROCm first
try:
    from utils.rocm_backend import HAS_AMD_GPU, HAS_ROCM, rocm_backend
    if HAS_ROCM and rocm_backend.available:
        logger.info("✅ ROCm backend available and initialized")
    elif HAS_AMD_GPU:
        logger.info("⚠️  AMD GPU detected but ROCm not properly configured")
        logger.info("💡 This system appears to have AMD GPU hardware")
        logger.info("🔧 Consider installing ROCm-enabled PyTorch for "
                    "acceleration")
    else:
        logger.info("ℹ️  No AMD GPU detected - ROCm disabled")
except ImportError as e:
    HAS_ROCM = False
    HAS_AMD_GPU = False
    logger.warning(f"ROCm backend import failed: {e}")

try:
    from utils.cuda_processor import HAS_CUDA, HAS_NVIDIA_GPU, cuda_processor
    if HAS_CUDA:
        logger.info("✅ CUDA processor available and initialized")
    elif HAS_NVIDIA_GPU:
        logger.info("⚠️  NVIDIA GPU detected but CUDA not properly configured")
    else:
        logger.info("ℹ️  No NVIDIA GPU detected - CUDA disabled")
except ImportError as e:
    HAS_CUDA = False
    HAS_NVIDIA_GPU = False
    logger.warning(f"CUDA processor import failed: {e}")
    logger.warning("ROCm backend not available")

if not HAS_CUDA and not HAS_ROCM:
    logger.warning("No GPU acceleration available, running in CPU mode")

logger.info("Creating FastAPI application...")


def create_app():
    """Create and configure the FastAPI application."""
    app = FastAPI(title="LLaMA-GPU Mock API", version="1.0.0")

    # Add CORS middleware
    logger.info("Configuring CORS middleware...")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


# Create the application instance
app = create_app()

@app.get("/health")
def health_check():
    """Health check endpoint for the mock API server"""
    logger.info("Processing health check request")
    return {"status": "ok", "server": "mock", "timestamp": time.time()}


class MockLLaMA:
    """Mock LLaMA model for testing streaming responses"""

    def __init__(self):
        self.responses = {
            "python": """Python is a versatile programming language
                great for beginners and experts alike.

Here are some key features:
- Easy to read syntax
- Large standard library
- Great for web development, data science, and AI
- Cross-platform compatibility

Would you like to learn about specific Python topics?""",

            "function": """Here's how to create a function in Python:

```python
def greet(name):
    return f"Hello, {name}!"

# Call the function
message = greet("World")
print(message)  # Output: Hello, World!
```

Functions can also have:
- Multiple parameters
- Default values
- Return multiple values
- Documentation strings""",

            "default": """I'm a LLaMA GPU accelerated model!
                I can help you with:

• Programming questions (Python, JavaScript, etc.)
• Code explanations and debugging
• Best practices and algorithms
• Data science and AI concepts

What would you like to learn about today?"""
        }

    async def generate_response(
        self, message: str
    ) -> AsyncGenerator[str, None]:
        """Generate a mock response token by token"""
        try:
            # Lower case message for simple keyword matching
            message = message.lower()

            # Choose response based on keywords
            if "python" in message:
                response = self.responses["python"]
            elif "function" in message:
                response = self.responses["function"]
            else:
                response = self.responses["default"]

            # Stream the response token by token
            words = response.split()
            for i, word in enumerate(words):
                # Add space before all words except the first
                if i > 0:
                    yield " "
                # Stream each word
                yield word
                # Add newline if it was in the original response
                if "\n" in response.split(word, 1)[1][:2]:
                    yield "\n"
                # Simulate thinking
                await asyncio.sleep(0.1)

        except (KeyError, ValueError, TypeError) as e:
            print(f"Error generating response: {e}")
            yield "I apologize, but I encountered an error. Please try again."


# Initialize mock model
mock_llama = MockLLaMA()


@app.websocket("/v1/stream")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time chat streaming"""
    try:
        await websocket.accept()
        logger.info("New WebSocket connection established")

        while True:
            try:
                # Receive message from client
                data = await websocket.receive_json()
                message_type = data.get('type', '')
                logger.info(f"Received message type: {message_type}")

                if message_type == 'message':
                    user_message = data.get('content', '')
                    logger.info(f"Processing message: {user_message[:50]}...")

                    # Send start signal
                    await websocket.send_json({
                        "type": "start",
                        "timestamp": time.time(),
                        "model": "llama-mock"
                    })

                    # Stream the response with metrics
                    token_count = 0
                    async for token in mock_llama.generate_response(user_message):
                        # Check if connection is still open
                        if websocket.client_state.DISCONNECTED:
                            break

                        await websocket.send_json({
                            "type": "token",
                            "content": token,
                            "timestamp": time.time()
                        })

                        token_count += 1

                        # Send metrics every few tokens
                        if token_count % 5 == 0:
                            await websocket.send_json({
                                "type": "metrics",
                                "metrics": {
                                    "gpuUsage": min(95, 45 + (time.time() % 50)),
                                    "tokensPerSecond": 12.5 + (time.time() % 8),
                                    "responseTime": int((time.time() % 2) * 1000 + 200)
                                }
                            })

                    # Send completion message
                    if not websocket.client_state.DISCONNECTED:
                        await websocket.send_json({
                            "type": "end",
                            "timestamp": time.time(),
                            "totalTokens": token_count
                        })

                elif message_type == 'stop':
                    logger.info("Stop generation requested")
                    await websocket.send_json({
                        "type": "end",
                        "timestamp": time.time(),
                        "reason": "stopped"
                    })

                else:
                    logger.warning(f"Unknown message type: {message_type}")
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Unknown message type: {message_type}"
                    })

            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON received: {e}")
                if not websocket.client_state.DISCONNECTED:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Invalid JSON format"
                    })
            except WebSocketDisconnect:
                logger.info("Client disconnected normally")
                break
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                if not websocket.client_state.DISCONNECTED:
                    try:
                        await websocket.send_json({
                            "type": "error",
                            "message": f"Server error: {str(e)}"
                        })
                    except Exception:
                        # Connection is probably closed, break the loop
                        break

    except WebSocketDisconnect:
        logger.info("WebSocket connection closed by client")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        logger.info("WebSocket connection cleanup completed")


@app.post("/v1/chat/completions")
async def chat_completions(request_data: dict):
    """HTTP streaming endpoint compatible with OpenAI API"""

    async def generate_sse():
        """Generate Server-Sent Events for streaming"""
        messages = request_data.get("messages", [])
        if messages:
            user_message = messages[-1].get("content", "")

            # Stream response
            async for token in mock_llama.generate_response(user_message):
                chunk = {
                    "id": f"chatcmpl-{int(time.time())}",
                    "object": "chat.completion.chunk",
                    "created": int(time.time()),
                    "model": "llama-base",
                    "choices": [{
                        "index": 0,
                        "delta": {"content": token},
                        "finish_reason": None
                    }]
                }

                yield f"data: {json.dumps(chunk)}\n\n"

            # Send completion
            final_chunk = {
                "id": f"chatcmpl-{int(time.time())}",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": "llama-base",
                "choices": [{
                    "index": 0,
                    "delta": {},
                    "finish_reason": "stop"
                }]
            }

            yield f"data: {json.dumps(final_chunk)}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate_sse(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@app.get("/v1/monitor/gpu-status")
async def gpu_status():
    """Get current GPU status"""
    return {
        "gpu_available": True,
        "gpu_name": "AMD Radeon RX 7900 XT",
        "memory_used": 8.2,
        "memory_total": 24.0,
        "utilization": 65,
        "temperature": 72
    }

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "LLaMA-GPU Mock API",
        "version": "1.0.0",
        "endpoints": {
            "websocket": "/v1/stream",
            "chat": "/v1/chat/completions",
            "gpu_status": "/v1/monitor/gpu-status",
            "health": "/health"
        },
        "description": "Mock API server for testing LLaMA-GPU chat interface"
    }


def find_free_port(start_port=8000, max_port=8020):
    """Find a free port in range."""
    for port in range(start_port, max_port + 1):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        with closing(sock):
            try:
                sock.bind(('127.0.0.1', port))
                return port
            except socket.error:
                continue
    return None


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Mock API Server for LLaMA-GPU')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=None, help='Port to bind to')
    parser.add_argument('--backend', choices=['cuda', 'rocm', 'cpu'], default='auto',
                       help='Backend to use (auto will detect available)')
    args = parser.parse_args()

    try:
        # Determine port
        if args.port:
            port = args.port
        else:
            port = find_free_port()
            if not port:
                logger.error("No available ports found in range 8000-8020")
                sys.exit(1)

        # Log backend selection with AMD/ROCm priority
        if args.backend == 'auto':
            if HAS_ROCM and rocm_backend.available:
                logger.info("🚀 Using ROCm backend (AMD GPU acceleration)")
                BACKEND = "rocm"
            elif HAS_CUDA:
                logger.info("🚀 Using CUDA backend (NVIDIA GPU acceleration)")
                BACKEND = "cuda"
            else:
                logger.info("🚀 Using CPU backend (no GPU acceleration)")
                BACKEND = "cpu"
                if HAS_AMD_GPU or HAS_NVIDIA_GPU:
                    logger.info("💡 GPU hardware detected but not configured")
                    logger.info("📖 Check troubleshooting in README.md")
        else:
            logger.info(f"🚀 Using {args.backend} backend (forced)")
            BACKEND = args.backend

        logger.info(f"🚀 Starting server on 0.0.0.0:{port}...")

        uvicorn.run(
            app,
            host=args.host,
            port=port,
            log_level="info",
            access_log=True
        )
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)
