"""주가·재무 API 통합 테스트.

conftest.py 의 async_client fixture를 사용합니다.
Stub 데이터(AAPL, 005930.KS)를 기반으로 각 엔드포인트의 응답 형식, 상태 코드,
페이지네이션, 날짜 필터, 404 처리를 검증합니다.
"""

from __future__ import annotations

from httpx import AsyncClient

# ──────────────────────────────────────────────────────────────────────
# 헬스체크
# ──────────────────────────────────────────────────────────────────────


async def test_health(async_client: AsyncClient) -> None:
    res = await async_client.get("/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert "version" in body


# ──────────────────────────────────────────────────────────────────────
# 종목 마스터
# ──────────────────────────────────────────────────────────────────────


async def test_list_stocks(async_client: AsyncClient) -> None:
    res = await async_client.get("/api/v1/stocks")
    assert res.status_code == 200
    body = res.json()
    assert "items" in body
    assert body["total"] >= 2


async def test_list_stocks_search(async_client: AsyncClient) -> None:
    res = await async_client.get("/api/v1/stocks", params={"search": "apple"})
    assert res.status_code == 200
    body = res.json()
    assert body["total"] >= 1
    assert any("AAPL" in item["symbol"] for item in body["items"])


async def test_list_stocks_pagination(async_client: AsyncClient) -> None:
    res = await async_client.get("/api/v1/stocks", params={"limit": 1, "offset": 0})
    assert res.status_code == 200
    body = res.json()
    assert len(body["items"]) == 1
    assert body["limit"] == 1


async def test_get_stock_found(async_client: AsyncClient) -> None:
    res = await async_client.get("/api/v1/stocks/AAPL")
    assert res.status_code == 200
    body = res.json()
    assert body["symbol"] == "AAPL"
    assert body["exchange"] == "NASDAQ"


async def test_get_stock_not_found(async_client: AsyncClient) -> None:
    res = await async_client.get("/api/v1/stocks/INVALID_XYZ")
    assert res.status_code == 404
    body = res.json()
    assert body["status"] == 404
    assert "INVALID_XYZ" in body["identifier"]


# ──────────────────────────────────────────────────────────────────────
# 주가(OHLCV)
# ──────────────────────────────────────────────────────────────────────


async def test_get_prices(async_client: AsyncClient) -> None:
    res = await async_client.get("/api/v1/stocks/AAPL/prices")
    assert res.status_code == 200
    body = res.json()
    assert body["total"] > 0
    assert all(item["symbol"] == "AAPL" for item in body["items"])


async def test_get_prices_date_range(async_client: AsyncClient) -> None:
    res = await async_client.get(
        "/api/v1/stocks/AAPL/prices",
        params={"from": "2024-01-03", "to": "2024-01-04"},
    )
    assert res.status_code == 200
    body = res.json()
    for item in body["items"]:
        assert "2024-01-03" <= item["date"] <= "2024-01-04"


async def test_get_prices_not_found(async_client: AsyncClient) -> None:
    res = await async_client.get("/api/v1/stocks/NOEXIST/prices")
    assert res.status_code == 404


async def test_get_latest_price(async_client: AsyncClient) -> None:
    res = await async_client.get("/api/v1/stocks/AAPL/prices/latest")
    assert res.status_code == 200
    body = res.json()
    assert body["symbol"] == "AAPL"
    assert body["date"] == "2024-01-08"


async def test_get_latest_price_not_found(async_client: AsyncClient) -> None:
    res = await async_client.get("/api/v1/stocks/NOEXIST/prices/latest")
    assert res.status_code == 404


# ──────────────────────────────────────────────────────────────────────
# 재무제표
# ──────────────────────────────────────────────────────────────────────


async def test_get_financials_all(async_client: AsyncClient) -> None:
    res = await async_client.get("/api/v1/stocks/AAPL/financials")
    assert res.status_code == 200
    body = res.json()
    assert len(body) >= 3


async def test_get_financials_income(async_client: AsyncClient) -> None:
    res = await async_client.get(
        "/api/v1/stocks/AAPL/financials", params={"statement": "income"}
    )
    assert res.status_code == 200
    body = res.json()
    assert all(item["statement_type"] == "income" for item in body)


async def test_get_financials_invalid_statement(async_client: AsyncClient) -> None:
    res = await async_client.get(
        "/api/v1/stocks/AAPL/financials", params={"statement": "invalid"}
    )
    assert res.status_code == 422


async def test_get_financials_not_found(async_client: AsyncClient) -> None:
    res = await async_client.get("/api/v1/stocks/NOEXIST/financials")
    assert res.status_code == 404


# ──────────────────────────────────────────────────────────────────────
# 배당
# ──────────────────────────────────────────────────────────────────────


async def test_get_dividends(async_client: AsyncClient) -> None:
    res = await async_client.get("/api/v1/stocks/AAPL/dividends")
    assert res.status_code == 200
    body = res.json()
    assert body["total"] >= 4


async def test_get_dividends_date_filter(async_client: AsyncClient) -> None:
    res = await async_client.get(
        "/api/v1/stocks/AAPL/dividends",
        params={"from": "2024-01-01"},
    )
    assert res.status_code == 200
    body = res.json()
    for item in body["items"]:
        assert item["ex_date"] >= "2024-01-01"


async def test_get_dividends_not_found(async_client: AsyncClient) -> None:
    res = await async_client.get("/api/v1/stocks/NOEXIST/dividends")
    assert res.status_code == 404


# ──────────────────────────────────────────────────────────────────────
# 주요지표
# ──────────────────────────────────────────────────────────────────────


async def test_get_metrics(async_client: AsyncClient) -> None:
    res = await async_client.get("/api/v1/stocks/AAPL/metrics")
    assert res.status_code == 200
    body = res.json()
    assert body["symbol"] == "AAPL"
    assert body["per"] is not None


async def test_get_metrics_not_found(async_client: AsyncClient) -> None:
    res = await async_client.get("/api/v1/stocks/NOEXIST/metrics")
    assert res.status_code == 404
