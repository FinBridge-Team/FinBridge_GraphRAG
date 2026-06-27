"""주가·재무 조회 라우터.

모든 엔드포인트는 읽기(GET) 전용입니다.
prefix /api/v1 은 main.py 에서 등록 시 적용됩니다.
"""

from __future__ import annotations

from datetime import date
from typing import Annotated, Literal

import structlog
from fastapi import APIRouter, Depends, Query

from app.apis.dependencies import StockServiceDep
from app.apis.dtos.common import DateRangeParams, Page, PaginationParams
from app.apis.dtos.stock import (
    DividendResponse,
    FinancialStatementResponse,
    MetricResponse,
    PriceResponse,
    SecurityResponse,
)

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/stocks", tags=["stocks"])


# ──────────────────────────────────────────────────────────────────────
# 종목 마스터
# ──────────────────────────────────────────────────────────────────────


@router.get(
    "",
    response_model=Page[SecurityResponse],
    summary="종목 목록 조회",
    description=(
        "종목 목록을 조회합니다. 이름/심볼 검색, 섹터·거래소 필터, 페이지네이션을 지원합니다."
    ),
    responses={422: {"description": "잘못된 쿼리 파라미터"}},
)
async def list_stocks(
    service: StockServiceDep,
    pagination: Annotated[PaginationParams, Depends()],
    search: str | None = Query(default=None, description="심볼 또는 회사명 부분 검색"),
    sector: str | None = Query(default=None, description="섹터 필터 (예: Technology)"),
    exchange: str | None = Query(default=None, description="거래소 필터 (예: NASDAQ, KRX)"),
) -> Page[SecurityResponse]:
    return await service.list_securities(
        search=search,
        sector=sector,
        exchange=exchange,
        limit=pagination.limit,
        offset=pagination.offset,
    )


@router.get(
    "/{symbol}",
    response_model=SecurityResponse,
    summary="종목 프로필 조회",
    description="단일 종목의 기업 프로필(거래소·섹터·시가총액 등)을 반환합니다.",
    responses={
        404: {"description": "해당 심볼의 종목이 존재하지 않습니다"},
    },
)
async def get_stock(symbol: str, service: StockServiceDep) -> SecurityResponse:
    return await service.get_security(symbol)


# ──────────────────────────────────────────────────────────────────────
# 주가(OHLCV)
# ──────────────────────────────────────────────────────────────────────


@router.get(
    "/{symbol}/prices",
    response_model=Page[PriceResponse],
    summary="주가 시계열 조회",
    description=(
        "일봉(OHLCV) 주가 데이터를 반환합니다. "
        "`from`/`to` 날짜 범위, 정렬 방향, 페이지네이션을 지원합니다."
    ),
    responses={
        404: {"description": "해당 심볼의 종목이 존재하지 않습니다"},
        422: {"description": "잘못된 쿼리 파라미터"},
    },
)
async def get_prices(
    symbol: str,
    service: StockServiceDep,
    date_range: Annotated[DateRangeParams, Depends()],
    pagination: Annotated[PaginationParams, Depends()],
    order: Literal["asc", "desc"] = Query(default="desc", description="날짜 정렬 방향"),
) -> Page[PriceResponse]:
    return await service.get_prices(
        symbol=symbol,
        from_date=date_range.from_date,
        to_date=date_range.to_date,
        order=order,
        limit=pagination.limit,
        offset=pagination.offset,
    )


@router.get(
    "/{symbol}/prices/latest",
    response_model=PriceResponse,
    summary="최신 주가 조회",
    description="가장 최근 거래일의 OHLCV 봉 데이터 1건을 반환합니다.",
    responses={
        404: {"description": "해당 심볼의 종목 또는 주가 데이터가 존재하지 않습니다"},
    },
)
async def get_latest_price(symbol: str, service: StockServiceDep) -> PriceResponse:
    return await service.get_latest_price(symbol)


# ──────────────────────────────────────────────────────────────────────
# 재무제표
# ──────────────────────────────────────────────────────────────────────


@router.get(
    "/{symbol}/financials",
    response_model=list[FinancialStatementResponse],
    summary="재무제표 조회",
    description=(
        "손익계산서(income)·재무상태표(balance)·현금흐름표(cashflow)를 반환합니다. "
        "`statement` 미지정 시 전체, `period`(annual|quarterly) 필터 가능."
    ),
    responses={
        404: {"description": "해당 심볼의 종목이 존재하지 않습니다"},
        422: {"description": "잘못된 쿼리 파라미터"},
    },
)
async def get_financials(
    symbol: str,
    service: StockServiceDep,
    date_range: Annotated[DateRangeParams, Depends()],
    statement: Literal["income", "balance", "cashflow"] | None = Query(
        default=None, description="재무제표 종류"
    ),
    period: Literal["annual", "quarterly"] | None = Query(
        default=None, description="기간 종류 (annual | quarterly)"
    ),
) -> list[FinancialStatementResponse]:
    return await service.get_financials(
        symbol=symbol,
        statement_type=statement,
        period_type=period,
        from_date=date_range.from_date,
        to_date=date_range.to_date,
    )


# ──────────────────────────────────────────────────────────────────────
# 배당
# ──────────────────────────────────────────────────────────────────────


@router.get(
    "/{symbol}/dividends",
    response_model=Page[DividendResponse],
    summary="배당 이력 조회",
    description="배당락일 기준 배당 이력을 반환합니다. 날짜 범위·페이지네이션 지원.",
    responses={
        404: {"description": "해당 심볼의 종목이 존재하지 않습니다"},
        422: {"description": "잘못된 쿼리 파라미터"},
    },
)
async def get_dividends(
    symbol: str,
    service: StockServiceDep,
    date_range: Annotated[DateRangeParams, Depends()],
    pagination: Annotated[PaginationParams, Depends()],
) -> Page[DividendResponse]:
    return await service.get_dividends(
        symbol=symbol,
        from_date=date_range.from_date,
        to_date=date_range.to_date,
        limit=pagination.limit,
        offset=pagination.offset,
    )


# ──────────────────────────────────────────────────────────────────────
# 주요지표
# ──────────────────────────────────────────────────────────────────────


@router.get(
    "/{symbol}/metrics",
    response_model=MetricResponse,
    summary="주요 밸류에이션 지표 조회",
    description=(
        "PER·PBR·EPS·배당수익률·시가총액 등 밸류에이션 지표를 반환합니다. "
        "`as_of` 미지정 시 최신 기준입니다."
    ),
    responses={
        404: {"description": "해당 심볼의 종목 또는 지표 데이터가 존재하지 않습니다"},
        422: {"description": "잘못된 쿼리 파라미터"},
    },
)
async def get_metrics(
    symbol: str,
    service: StockServiceDep,
    as_of: date | None = Query(default=None, description="기준일 (YYYY-MM-DD), 미지정 시 최신"),
) -> MetricResponse:
    return await service.get_metrics(symbol=symbol, as_of=as_of)
