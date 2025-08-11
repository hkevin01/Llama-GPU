import pytest
from httpx import ASGITransport, AsyncClient

from src.api_server import app


@pytest.mark.anyio
async def test_healthz() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        res = await ac.get("/healthz")
        assert res.status_code == 200
        assert res.json()["status"] == "ok"


@pytest.mark.anyio
async def test_completions_basic() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        res = await ac.post(
            "/v1/completions",
            json={"prompt": "Hello", "max_tokens": 8, "temperature": 0.1},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["object"] == "text_completion"
        assert isinstance(data["choices"], list) and data["choices"]
