from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from src.api_server import app


def test_websocket_stream_minimal() -> None:
    client = TestClient(app)
    with client.websocket_connect("/v1/stream") as ws:
        ws.send_text("Hello")
        chunks = []
        try:
            while True:
                chunks.append(ws.receive_text())
        except WebSocketDisconnect:
            # Connection closed by server
            pass
        assert any("hello" in c.lower() for c in chunks)
