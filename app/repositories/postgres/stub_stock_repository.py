"""StockRepository 의 Stub(임시) 구현체.

⚠️  DB 미구현 — 하드코딩된 샘플 데이터를 메모리에서 반환합니다.
    DB 담당자는 이 파일 대신 PostgresStockRepository 를 구현하고
    app/apis/dependencies.py 의 get_stock_service() 주입만 교체하면 됩니다.

샘플 종목: AAPL (Apple Inc.), 005930.KS (Samsung Electronics)
"""

from __future__ import annotations

from datetime import date
from typing import Literal

import structlog

from app.apis.dtos.stock import (
    DividendResponse,
    FinancialStatementResponse,
    MetricResponse,
    PriceResponse,
    SecurityResponse,
)

logger = structlog.get_logger(__name__)

# ──────────────────────────────────────────────────────────────────────
# 샘플 데이터
# ──────────────────────────────────────────────────────────────────────

_SECURITIES: dict[str, SecurityResponse] = {
    "AAPL": SecurityResponse(
        symbol="AAPL",
        name="Apple Inc.",
        exchange="NASDAQ",
        sector="Technology",
        industry="Consumer Electronics",
        currency="USD",
        country="US",
        market_cap=3_000_000_000_000.0,
    ),
    "005930.KS": SecurityResponse(
        symbol="005930.KS",
        name="Samsung Electronics Co., Ltd.",
        exchange="KRX",
        sector="Technology",
        industry="Semiconductors",
        currency="KRW",
        country="KR",
        market_cap=350_000_000_000_000.0,
    ),
}

_PRICES: dict[str, list[PriceResponse]] = {
    "AAPL": [
        PriceResponse(
            symbol="AAPL", date=date(2024, 1, 2),
            open=185.0, high=188.5, low=184.3, close=187.1, volume=52_000_000,
        ),
        PriceResponse(
            symbol="AAPL", date=date(2024, 1, 3),
            open=187.1, high=190.0, low=186.0, close=189.3, volume=48_000_000,
        ),
        PriceResponse(
            symbol="AAPL", date=date(2024, 1, 4),
            open=189.0, high=191.5, low=188.0, close=190.7, volume=45_000_000,
        ),
        PriceResponse(
            symbol="AAPL", date=date(2024, 1, 5),
            open=190.5, high=193.0, low=189.5, close=192.1, volume=47_000_000,
        ),
        PriceResponse(
            symbol="AAPL", date=date(2024, 1, 8),
            open=192.0, high=195.5, low=191.0, close=194.5, volume=55_000_000,
        ),
    ],
    "005930.KS": [
        PriceResponse(
            symbol="005930.KS",
            date=date(2024, 1, 2),
            open=72_800,
            high=73_500,
            low=72_400,
            close=73_100,
            volume=12_000_000,
        ),
        PriceResponse(
            symbol="005930.KS",
            date=date(2024, 1, 3),
            open=73_000,
            high=74_000,
            low=72_800,
            close=73_800,
            volume=11_500_000,
        ),
    ],
}

_FINANCIALS: dict[str, list[FinancialStatementResponse]] = {
    "AAPL": [
        FinancialStatementResponse(
            symbol="AAPL",
            statement_type="income",
            period_type="annual",
            fiscal_date=date(2023, 9, 30),
            line_items={
                "Total Revenue": 383_285_000_000.0,
                "Gross Profit": 169_148_000_000.0,
                "Operating Income": 114_301_000_000.0,
                "Net Income": 96_995_000_000.0,
                "EBITDA": 125_820_000_000.0,
            },
        ),
        FinancialStatementResponse(
            symbol="AAPL",
            statement_type="balance",
            period_type="annual",
            fiscal_date=date(2023, 9, 30),
            line_items={
                "Total Assets": 352_583_000_000.0,
                "Total Liabilities": 290_437_000_000.0,
                "Total Equity": 62_146_000_000.0,
                "Cash And Cash Equivalents": 29_965_000_000.0,
                "Total Debt": 111_088_000_000.0,
            },
        ),
        FinancialStatementResponse(
            symbol="AAPL",
            statement_type="cashflow",
            period_type="annual",
            fiscal_date=date(2023, 9, 30),
            line_items={
                "Operating Cash Flow": 113_040_000_000.0,
                "Capital Expenditure": -10_959_000_000.0,
                "Free Cash Flow": 102_081_000_000.0,
            },
        ),
    ],
    "005930.KS": [
        FinancialStatementResponse(
            symbol="005930.KS",
            statement_type="income",
            period_type="annual",
            fiscal_date=date(2023, 12, 31),
            line_items={
                "Total Revenue": 258_935_000_000_000.0,
                "Gross Profit": 50_090_000_000_000.0,
                "Operating Income": 6_566_000_000_000.0,
                "Net Income": 15_487_000_000_000.0,
            },
        ),
    ],
}

_DIVIDENDS: dict[str, list[DividendResponse]] = {
    "AAPL": [
        DividendResponse(symbol="AAPL", ex_date=date(2024, 2, 9), amount=0.24),
        DividendResponse(symbol="AAPL", ex_date=date(2023, 11, 10), amount=0.24),
        DividendResponse(symbol="AAPL", ex_date=date(2023, 8, 11), amount=0.24),
        DividendResponse(symbol="AAPL", ex_date=date(2023, 5, 12), amount=0.24),
    ],
    "005930.KS": [
        DividendResponse(symbol="005930.KS", ex_date=date(2023, 12, 28), amount=361.0),
    ],
}

_METRICS: dict[str, MetricResponse] = {
    "AAPL": MetricResponse(
        symbol="AAPL",
        as_of_date=date(2024, 1, 8),
        per=29.5,
        pbr=48.3,
        eps=6.56,
        dividend_yield=0.0049,
        market_cap=3_000_000_000_000.0,
    ),
    "005930.KS": MetricResponse(
        symbol="005930.KS",
        as_of_date=date(2024, 1, 3),
        per=22.1,
        pbr=1.3,
        eps=3_344.0,
        dividend_yield=0.0049,
        market_cap=350_000_000_000_000.0,
    ),
}


# ──────────────────────────────────────────────────────────────────────
# Stub 구현
# ──────────────────────────────────────────────────────────────────────


class StubStockRepository:
    """메모리 기반 stub 구현. DB 연결 없이 샘플 객체를 반환합니다."""

    async def symbol_exists(self, symbol: str) -> bool:
        return symbol.upper() in _SECURITIES or symbol in _SECURITIES

    async def get_security(self, symbol: str) -> SecurityResponse | None:
        logger.debug("stub.get_security", symbol=symbol)
        return _SECURITIES.get(symbol) or _SECURITIES.get(symbol.upper())

    async def list_securities(
        self,
        search: str | None = None,
        sector: str | None = None,
        exchange: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[SecurityResponse], int]:
        logger.debug("stub.list_securities", search=search, sector=sector, exchange=exchange)
        items = list(_SECURITIES.values())

        if search:
            s = search.lower()
            items = [
                i for i in items if s in i.symbol.lower() or s in i.name.lower()
            ]
        if sector:
            items = [i for i in items if i.sector and sector.lower() in i.sector.lower()]
        if exchange:
            items = [i for i in items if exchange.lower() in i.exchange.lower()]

        total = len(items)
        return items[offset : offset + limit], total

    async def get_prices(
        self,
        symbol: str,
        from_date: date | None = None,
        to_date: date | None = None,
        order: Literal["asc", "desc"] = "desc",
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[PriceResponse], int]:
        logger.debug("stub.get_prices", symbol=symbol, from_date=from_date, to_date=to_date)
        rows = list(_PRICES.get(symbol, []))

        if from_date:
            rows = [r for r in rows if r.date >= from_date]
        if to_date:
            rows = [r for r in rows if r.date <= to_date]

        rows.sort(key=lambda r: r.date, reverse=(order == "desc"))
        total = len(rows)
        return rows[offset : offset + limit], total

    async def get_latest_price(self, symbol: str) -> PriceResponse | None:
        rows = _PRICES.get(symbol)
        if not rows:
            return None
        return max(rows, key=lambda r: r.date)

    async def get_financials(
        self,
        symbol: str,
        statement_type: Literal["income", "balance", "cashflow"] | None = None,
        period_type: Literal["annual", "quarterly"] | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[FinancialStatementResponse]:
        logger.debug("stub.get_financials", symbol=symbol, statement_type=statement_type)
        rows = list(_FINANCIALS.get(symbol, []))

        if statement_type:
            rows = [r for r in rows if r.statement_type == statement_type]
        if period_type:
            rows = [r for r in rows if r.period_type == period_type]
        if from_date:
            rows = [r for r in rows if r.fiscal_date >= from_date]
        if to_date:
            rows = [r for r in rows if r.fiscal_date <= to_date]

        return rows

    async def get_dividends(
        self,
        symbol: str,
        from_date: date | None = None,
        to_date: date | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[DividendResponse], int]:
        logger.debug("stub.get_dividends", symbol=symbol)
        rows = list(_DIVIDENDS.get(symbol, []))

        if from_date:
            rows = [r for r in rows if r.ex_date >= from_date]
        if to_date:
            rows = [r for r in rows if r.ex_date <= to_date]

        rows.sort(key=lambda r: r.ex_date, reverse=True)
        total = len(rows)
        return rows[offset : offset + limit], total

    async def get_metrics(
        self,
        symbol: str,
        as_of: date | None = None,
    ) -> MetricResponse | None:
        logger.debug("stub.get_metrics", symbol=symbol, as_of=as_of)
        return _METRICS.get(symbol)
