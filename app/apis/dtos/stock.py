"""주가·재무·종목 관련 API 응답 DTO.

기존 pipeline/collectors/dtos/stock.py 의 OhlcvRecord 필드 구조를 API 계약으로 계승합니다.

Note: `from __future__ import annotations` 미사용.
  Pydantic v2에서 `date: date` 처럼 필드명과 타입명이 같으면 "unevaluable type annotation" 오류가
  발생하므로, datetime.date 를 Date 별칭으로 임포트합니다.
"""

from datetime import date as Date  # noqa: N812
from typing import Literal

from pydantic import BaseModel, Field


class SecurityResponse(BaseModel):
    """종목/기업 마스터 정보."""

    symbol: str = Field(description="티커 심볼 (예: AAPL, 005930.KS)")
    name: str = Field(description="회사명")
    exchange: str = Field(description="거래소 (예: NASDAQ, KRX)")
    sector: str | None = Field(default=None, description="섹터")
    industry: str | None = Field(default=None, description="산업")
    currency: str = Field(description="거래 통화 (예: USD, KRW)")
    country: str | None = Field(default=None, description="국가 코드 (예: US, KR)")
    market_cap: float | None = Field(default=None, description="시가총액")

    model_config = {"from_attributes": True}


class PriceResponse(BaseModel):
    """일봉(OHLCV) 주가 데이터.

    pipeline/collectors/dtos/stock.py 의 OhlcvRecord와 동일한 스키마입니다.
    """

    symbol: str = Field(description="티커 심볼")
    date: Date = Field(description="거래일")
    open: float = Field(ge=0, description="시가")
    high: float = Field(ge=0, description="고가")
    low: float = Field(ge=0, description="저가")
    close: float = Field(ge=0, description="종가")
    volume: int = Field(ge=0, description="거래량")

    model_config = {"from_attributes": True}


class FinancialStatementResponse(BaseModel):
    """재무제표 (손익계산서·재무상태표·현금흐름표).

    line_items에 항목명 → 금액(KRW 또는 USD) 딕셔너리로 제공합니다.
    """

    symbol: str = Field(description="티커 심볼")
    statement_type: Literal["income", "balance", "cashflow"] = Field(description="재무제표 종류")
    period_type: Literal["annual", "quarterly"] = Field(description="기간 종류")
    fiscal_date: Date = Field(description="회계 기준일")
    line_items: dict[str, float | None] = Field(description="재무 항목 딕셔너리")

    model_config = {"from_attributes": True}


class DividendResponse(BaseModel):
    """배당 이력."""

    symbol: str = Field(description="티커 심볼")
    ex_date: Date = Field(description="배당락일")
    amount: float = Field(ge=0, description="주당 배당금")

    model_config = {"from_attributes": True}


class MetricResponse(BaseModel):
    """주요 밸류에이션 지표."""

    symbol: str = Field(description="티커 심볼")
    as_of_date: Date = Field(description="기준일")
    per: float | None = Field(default=None, description="주가수익비율(PER)")
    pbr: float | None = Field(default=None, description="주가순자산비율(PBR)")
    eps: float | None = Field(default=None, description="주당순이익(EPS)")
    dividend_yield: float | None = Field(default=None, description="배당수익률 (0~1)")
    market_cap: float | None = Field(default=None, description="시가총액")

    model_config = {"from_attributes": True}
