"""StockRepository 인터페이스 (Protocol).

이 Protocol이 DB 담당자와의 계약 지점입니다.
DB 담당자는 이 인터페이스를 구현하는 PostgresStockRepository 클래스를 만들고
app/apis/dependencies.py 의 get_stock_service() 에서 주입만 교체하면 됩니다.
"""

from __future__ import annotations

from datetime import date
from typing import Literal, Protocol, runtime_checkable

from app.apis.dtos.stock import (
    DividendResponse,
    FinancialStatementResponse,
    MetricResponse,
    PriceResponse,
    SecurityResponse,
)


@runtime_checkable
class StockRepository(Protocol):
    """주가·재무 데이터 접근 인터페이스."""

    # ─── 종목 마스터 ─────────────────────────────────────────────────

    async def symbol_exists(self, symbol: str) -> bool:
        """심볼이 DB에 존재하는지 확인합니다."""
        ...

    async def get_security(self, symbol: str) -> SecurityResponse | None:
        """단일 종목 프로필을 반환합니다. 없으면 None."""
        ...

    async def list_securities(
        self,
        search: str | None = None,
        sector: str | None = None,
        exchange: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[SecurityResponse], int]:
        """종목 목록과 전체 건수를 반환합니다. (items, total)"""
        ...

    # ─── 주가(OHLCV) ─────────────────────────────────────────────────

    async def get_prices(
        self,
        symbol: str,
        from_date: date | None = None,
        to_date: date | None = None,
        order: Literal["asc", "desc"] = "desc",
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[PriceResponse], int]:
        """주가 시계열과 전체 건수를 반환합니다. (items, total)"""
        ...

    async def get_latest_price(self, symbol: str) -> PriceResponse | None:
        """가장 최근 봉 데이터를 반환합니다. 없으면 None."""
        ...

    # ─── 재무제표 ─────────────────────────────────────────────────────

    async def get_financials(
        self,
        symbol: str,
        statement_type: Literal["income", "balance", "cashflow"] | None = None,
        period_type: Literal["annual", "quarterly"] | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[FinancialStatementResponse]:
        """재무제표 목록을 반환합니다."""
        ...

    # ─── 배당 ─────────────────────────────────────────────────────────

    async def get_dividends(
        self,
        symbol: str,
        from_date: date | None = None,
        to_date: date | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[DividendResponse], int]:
        """배당 이력과 전체 건수를 반환합니다. (items, total)"""
        ...

    # ─── 주요지표 ─────────────────────────────────────────────────────

    async def get_metrics(
        self,
        symbol: str,
        as_of: date | None = None,
    ) -> MetricResponse | None:
        """밸류에이션 지표를 반환합니다. as_of 미지정 시 최신 기준. 없으면 None."""
        ...
