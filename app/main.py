"""FinBridge GraphRAG API 엔트리포인트.

docker-compose.yml / Dockerfile 이 기대하는 app.main:app 심볼을 제공합니다.
실행: uvicorn app.main:app --reload
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.apis import health, stocks
from app.core.config import get_settings
from app.core.exceptions import EntityNotFoundError
from app.core.logging import setup_logging

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
    """앱 시작/종료 시 실행되는 라이프사이클 훅."""
    settings = get_settings()
    setup_logging(debug=settings.debug)
    logger.info("finbridge_api.startup", version=settings.app_version)
    yield
    logger.info("finbridge_api.shutdown")


def create_app() -> FastAPI:
    """FastAPI 애플리케이션 팩토리."""
    settings = get_settings()

    application = FastAPI(
        title=settings.app_title,
        version=settings.app_version,
        description=settings.app_description,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # ── 예외 핸들러 ─────────────────────────────────────────────────
    @application.exception_handler(EntityNotFoundError)
    async def entity_not_found_handler(request: Request, exc: EntityNotFoundError) -> JSONResponse:
        """RFC 7807 Problem Details 형식으로 404 응답을 반환합니다."""
        return JSONResponse(
            status_code=404,
            content={
                "type": "https://finbridge.local/errors/not-found",
                "title": "Not Found",
                "status": 404,
                "detail": str(exc),
                "entity": exc.entity,
                "identifier": exc.identifier,
            },
            media_type="application/problem+json",
        )

    # ── 라우터 등록 ──────────────────────────────────────────────────
    application.include_router(health.router)
    application.include_router(stocks.router, prefix="/api/v1")

    return application


app = create_app()
