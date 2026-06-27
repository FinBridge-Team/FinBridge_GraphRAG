"""pytest 공통 fixture."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def async_client() -> AsyncClient:
    """FastAPI 앱을 대상으로 하는 비동기 HTTP 클라이언트."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
