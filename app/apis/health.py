"""헬스체크 라우터."""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    version: str


@router.get("/health", response_model=HealthResponse, summary="헬스체크")
async def health() -> HealthResponse:
    """서비스 상태를 반환합니다."""
    from app.core.config import get_settings

    settings = get_settings()
    return HealthResponse(status="ok", version=settings.app_version)
