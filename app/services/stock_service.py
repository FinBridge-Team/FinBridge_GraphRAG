"""StockService — 주가·재무 조회 비즈니스 로직.

Repository 인터페이스를 주입받아 동작하므로 DB 구현과 독립적입니다.
"""

from __future__ import annotations

from datetime import date
from typing import Literal

import structlog

from app.apis.dtos.common import Page
from app.apis.dtos.stock import (
    DividendResponse,
    FinancialStatementResponse,
    MetricResponse,
    PriceResponse,
    SecurityResponse,
)
from app.core.exceptions import EntityNotFoundError
from app.repositories.postgres.stock_repository import StockRepository

logger = structlog.get_logger(__name__)


class StockService:
    """주가·재무 데이터 조회 서비스."""

    def __init__(self, repo: StockRepository) -> None:
        self._repo = repo

    # ──────────────────────────────────────────────────────────────
    # 내부 헬퍼
    # ──────────────────────────────────────────────────────────────

    async def _require_symbol(self, symbol: str) -> None:
        """심볼이 존재하지 않으면 EntityNotFoundError를 발생시킵니다."""
        if not await self._repo.symbol_exists(symbol):
            logger.warning("stock_service.symbol_not_found", symbol=symbol)
            raise EntityNotFoundError("Security", symbol)

    # ──────────────────────────────────────────────────────────────
    # 종목 마스터
    # ──────────────────────────────────────────────────────────────

    async def list_securities(
        self,
        search: str | None = None,
        sector: str | None = None,
        exchange: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Page[SecurityResponse]:
        logger.info("stock_service.list_securities", search=search, sector=sector)
        items, total = await self._repo.list_securities(
            search=search, sector=sector, exchange=exchange, limit=limit, offset=offset
        )
        return Page(items=items, total=total, limit=limit, offset=offset)

    async def get_security(self, symbol: str) -> SecurityResponse:
        logger.info("stock_service.get_security", symbol=symbol)
        await self._require_symbol(symbol)
        security = await self._repo.get_security(symbol)
        if security is None:
            raise EntityNotFoundError("Security", symbol)
        return security

    # ──────────────────────────────────────────────────────────────
    # 주가(OHLCV)
    # ──────────────────────────────────────────────────────────────

    async def get_prices(
        self,
        symbol: str,
        from_date: date | None = None,
        to_date: date | None = None,
        order: Literal["asc", "desc"] = "desc",
        limit: int = 50,
        offset: int = 0,
    ) -> Page[PriceResponse]:
        logger.info("stock_service.get_prices", symbol=symbol)
        await self._require_symbol(symbol)
        items, total = await self._repo.get_prices(
            symbol=symbol,
            from_date=from_date,
            to_date=to_date,
            order=order,
            limit=limit,
            offset=offset,
        )
        return Page(items=items, total=total, limit=limit, offset=offset)

    async def get_latest_price(self, symbol: str) -> PriceResponse:
        logger.info("stock_service.get_latest_price", symbol=symbol)
        await self._require_symbol(symbol)
        price = await self._repo.get_latest_price(symbol)
        if price is None:
            raise EntityNotFoundError("Price", symbol)
        return price

    # ──────────────────────────────────────────────────────────────
    # 재무제표
    # ──────────────────────────────────────────────────────────────

    async def get_financials(
        self,
        symbol: str,
        statement_type: Literal["income", "balance", "cashflow"] | None = None,
        period_type: Literal["annual", "quarterly"] | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[FinancialStatementResponse]:
        logger.info("stock_service.get_financials", symbol=symbol, statement=statement_type)
        await self._require_symbol(symbol)
        return await self._repo.get_financials(
            symbol=symbol,
            statement_type=statement_type,
            period_type=period_type,
            from_date=from_date,
            to_date=to_date,
        )

    # ──────────────────────────────────────────────────────────────
    # 배당
    # ──────────────────────────────────────────────────────────────

    async def get_dividends(
        self,
        symbol: str,
        from_date: date | None = None,
        to_date: date | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Page[DividendResponse]:
        logger.info("stock_service.get_dividends", symbol=symbol)
        await self._require_symbol(symbol)
        items, total = await self._repo.get_dividends(
            symbol=symbol, from_date=from_date, to_date=to_date, limit=limit, offset=offset
        )
        return Page(items=items, total=total, limit=limit, offset=offset)

    # ──────────────────────────────────────────────────────────────
    # 주요지표
    # ──────────────────────────────────────────────────────────────

    async def get_metrics(
        self,
        symbol: str,
        as_of: date | None = None,
    ) -> MetricResponse:
        logger.info("stock_service.get_metrics", symbol=symbol, as_of=as_of)
        await self._require_symbol(symbol)
        metrics = await self._repo.get_metrics(symbol=symbol, as_of=as_of)
        if metrics is None:
            raise EntityNotFoundError("Metrics", symbol)
        return metrics
