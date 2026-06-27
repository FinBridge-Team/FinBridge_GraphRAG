"""공통 쿼리 파라미터 및 제네릭 페이지 응답 모델."""

from __future__ import annotations

from datetime import date
from typing import Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel, Field

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    """페이지네이션된 응답 래퍼."""

    items: list[T]
    total: int = Field(description="전체 항목 수")
    limit: int = Field(description="페이지 크기")
    offset: int = Field(description="시작 오프셋")


class PaginationParams:
    """공통 페이지네이션 쿼리 파라미터 (FastAPI Depends용)."""

    def __init__(
        self,
        limit: int = Query(default=50, ge=1, le=500, description="반환 최대 건수"),
        offset: int = Query(default=0, ge=0, description="시작 오프셋"),
    ) -> None:
        self.limit = limit
        self.offset = offset


class DateRangeParams:
    """날짜 범위 쿼리 파라미터 (FastAPI Depends용)."""

    def __init__(
        self,
        from_date: date | None = Query(
            default=None, alias="from", description="시작일 (YYYY-MM-DD)"
        ),
        to_date: date | None = Query(
            default=None, alias="to", description="종료일 (YYYY-MM-DD)"
        ),
    ) -> None:
        self.from_date = from_date
        self.to_date = to_date
