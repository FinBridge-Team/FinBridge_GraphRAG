"""StockService 단위 테스트.

StubStockRepository를 직접 주입해 DB 없이 서비스 로직을 검증합니다.
"""

from __future__ import annotations

from datetime import date

import pytest

from app.core.exceptions import EntityNotFoundError
from app.repositories.postgres.stub_stock_repository import StubStockRepository
from app.services.stock_service import StockService


@pytest.fixture
def service() -> StockService:
    return StockService(repo=StubStockRepository())


# ──────────────────────────────────────────────────────────────────────
# 종목 마스터
# ──────────────────────────────────────────────────────────────────────


async def test_list_securities_returns_all(service: StockService) -> None:
    page = await service.list_securities()
    assert page.total >= 2
    symbols = [s.symbol for s in page.items]
    assert "AAPL" in symbols
    assert "005930.KS" in symbols


async def test_list_securities_search(service: StockService) -> None:
    page = await service.list_securities(search="apple")
    assert page.total >= 1
    assert all("apple" in s.name.lower() or "apple" in s.symbol.lower() for s in page.items)


async def test_list_securities_sector_filter(service: StockService) -> None:
    page = await service.list_securities(sector="Technology")
    assert page.total >= 1
    assert all(s.sector == "Technology" for s in page.items)


async def test_list_securities_pagination(service: StockService) -> None:
    page = await service.list_securities(limit=1, offset=0)
    assert len(page.items) == 1
    assert page.limit == 1
    assert page.offset == 0


async def test_get_security_found(service: StockService) -> None:
    security = await service.get_security("AAPL")
    assert security.symbol == "AAPL"
    assert security.exchange == "NASDAQ"


async def test_get_security_not_found(service: StockService) -> None:
    with pytest.raises(EntityNotFoundError) as exc_info:
        await service.get_security("INVALID_XYZ")
    assert exc_info.value.entity == "Security"
    assert "INVALID_XYZ" in exc_info.value.identifier


# ──────────────────────────────────────────────────────────────────────
# 주가(OHLCV)
# ──────────────────────────────────────────────────────────────────────


async def test_get_prices_returns_data(service: StockService) -> None:
    page = await service.get_prices("AAPL")
    assert page.total > 0
    assert all(p.symbol == "AAPL" for p in page.items)


async def test_get_prices_date_range_filter(service: StockService) -> None:
    page = await service.get_prices(
        "AAPL",
        from_date=date(2024, 1, 3),
        to_date=date(2024, 1, 4),
    )
    assert all(date(2024, 1, 3) <= p.date <= date(2024, 1, 4) for p in page.items)


async def test_get_prices_desc_order(service: StockService) -> None:
    page = await service.get_prices("AAPL", order="desc")
    dates = [p.date for p in page.items]
    assert dates == sorted(dates, reverse=True)


async def test_get_prices_symbol_not_found(service: StockService) -> None:
    with pytest.raises(EntityNotFoundError):
        await service.get_prices("NOEXIST")


async def test_get_latest_price(service: StockService) -> None:
    price = await service.get_latest_price("AAPL")
    assert price.symbol == "AAPL"
    assert price.date == date(2024, 1, 8)


async def test_get_latest_price_not_found(service: StockService) -> None:
    with pytest.raises(EntityNotFoundError):
        await service.get_latest_price("NOEXIST")


# ──────────────────────────────────────────────────────────────────────
# 재무제표
# ──────────────────────────────────────────────────────────────────────


async def test_get_financials_all(service: StockService) -> None:
    rows = await service.get_financials("AAPL")
    assert len(rows) >= 3


async def test_get_financials_income_only(service: StockService) -> None:
    rows = await service.get_financials("AAPL", statement_type="income")
    assert all(r.statement_type == "income" for r in rows)


async def test_get_financials_not_found(service: StockService) -> None:
    with pytest.raises(EntityNotFoundError):
        await service.get_financials("NOEXIST")


# ──────────────────────────────────────────────────────────────────────
# 배당
# ──────────────────────────────────────────────────────────────────────


async def test_get_dividends(service: StockService) -> None:
    page = await service.get_dividends("AAPL")
    assert page.total >= 4
    assert all(d.symbol == "AAPL" for d in page.items)


async def test_get_dividends_date_filter(service: StockService) -> None:
    page = await service.get_dividends(
        "AAPL",
        from_date=date(2024, 1, 1),
        to_date=date(2024, 12, 31),
    )
    assert all(d.ex_date >= date(2024, 1, 1) for d in page.items)


async def test_get_dividends_not_found(service: StockService) -> None:
    with pytest.raises(EntityNotFoundError):
        await service.get_dividends("NOEXIST")


# ──────────────────────────────────────────────────────────────────────
# 주요지표
# ──────────────────────────────────────────────────────────────────────


async def test_get_metrics(service: StockService) -> None:
    metrics = await service.get_metrics("AAPL")
    assert metrics.symbol == "AAPL"
    assert metrics.per is not None


async def test_get_metrics_not_found(service: StockService) -> None:
    with pytest.raises(EntityNotFoundError):
        await service.get_metrics("NOEXIST")
