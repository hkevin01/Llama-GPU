#!/usr/bin/env python3
"""
Mock API Server for LLaMA-GPU Chat Interface Testing
Provides WebSocket and HTTP streaming endpoints for testing the real-time chat
"""

import asyncio
import json
import logging
import os
import sys
import time
import traceback
from typing import AsyncGenerator

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("mock_api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

logger.info("Creating FastAPI application...")
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
    await websocket.accept()

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)

            if message_data.get("type") == "chat":
                user_message = message_data.get("message", "")

                # Send acknowledgment
                await websocket.send_text(json.dumps({
                    "type": "start",
                    "message": "Starting response generation..."
                }))

                # Stream response
                async for token in mock_llama.generate_response(user_message):
                    await websocket.send_text(json.dumps({
                        "type": "token",
                        "content": token
                    }))

                    # Send metrics periodically
                    if len(token.strip()) > 0:
                        await websocket.send_text(json.dumps({
                            "type": "metrics",
                            "metrics": {
                                # Simulate GPU usage between 65-95%
                                "gpu_usage": 65 + (time.time() % 30),
                                "tokens_per_sec": 15.2
                            }
                        }))

                # Send completion signal
                await websocket.send_text(json.dumps({
                    "type": "complete"
                }))

    except WebSocketDisconnect:
        print("WebSocket client disconnected")


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


if __name__ == "__main__":
    import socket
    import sys
    from contextlib import closing

    import uvicorn

    try:
        def find_free_port():
            with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
                s.bind(('', 0))
                s.listen(1)
                port = s.getsockname()[1]
                return port

        port = find_free_port()
        print(f"🚀 Starting on port {port}...")
        uvicorn.run(app, host="0.0.0.0", port=port)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
