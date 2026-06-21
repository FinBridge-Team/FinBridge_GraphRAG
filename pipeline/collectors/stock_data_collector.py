"""
주가 데이터 수집기 (Data Collector)

yfinance를 사용해 지정 종목의 OHLCV 시계열 데이터를 수집합니다.

사용 예:
    from pipeline.collectors.stock_data_collector import collect_ohlcv

    records = collect_ohlcv("AAPL", period="1d", interval="1d")
    # [{'symbol': 'AAPL', 'date': '2024-01-02', 'open': 185.0, ...}, ...]
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed

import structlog
import yfinance as yf
from tenacity import retry, stop_after_attempt, wait_exponential

from pipeline.collectors.dtos.stock import OhlcvRecord
from pipeline.exceptions import StockDataCollectionError

logger = structlog.get_logger(__name__)


def _ticker_history(symbol: str, period: str, interval: str):
    """yfinance Ticker.history() 호출을 분리해 테스트에서 mock하기 쉽게 한다."""
    ticker = yf.Ticker(symbol)
    return ticker.history(period=period, interval=interval)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    reraise=True,
)
def collect_ohlcv(
    symbol: str,
    period: str = "1d",
    interval: str = "1d",
) -> list[OhlcvRecord]:
    """지정 종목의 OHLCV 시계열을 수집해 리스트로 반환한다.

    Args:
        symbol:   티커 심볼 (예: "AAPL", "005930.KS").
        period:   조회 기간. yfinance 지원 값 — "1d", "5d", "1mo", "3mo", "1y" 등.
        interval: 데이터 간격. yfinance 지원 값 — "1m", "5m", "1h", "1d", "1wk" 등.
                  (1m 간격은 최근 7일 데이터만 제공)

    Raises:
        StockDataCollectionError: 심볼이 유효하지 않거나 데이터를 가져오지 못한 경우.
    """
    log = logger.bind(symbol=symbol, period=period, interval=interval)
    log.info("stock_data_collection.start")

    try:
        df = _ticker_history(symbol=symbol, period=period, interval=interval)
    except Exception as exc:
        log.error("stock_data_collection.fetch_failed", error=str(exc))
        raise StockDataCollectionError(
            f"yfinance 데이터 조회 실패 — symbol={symbol!r}: {exc}"
        ) from exc

    if df is None or df.empty:
        log.warning("stock_data_collection.empty_result")
        raise StockDataCollectionError(
            f"수집된 데이터가 없습니다 — symbol={symbol!r}, period={period!r}"
        )

    records: list[OhlcvRecord] = []
    for timestamp, row in df.iterrows():
        records.append(
            OhlcvRecord(
                symbol=symbol,
                date=timestamp.date(),
                open=float(row["Open"]),
                high=float(row["High"]),
                low=float(row["Low"]),
                close=float(row["Close"]),
                volume=int(row["Volume"]),
            )
        )

    log.info("stock_data_collection.success", records=len(records))
    return records


def collect_ohlcvs(
    symbols: list[str],
    period: str = "1d",
    interval: str = "1d",
    max_workers: int = 8,
) -> dict[str, list[OhlcvRecord]]:
    """여러 종목의 OHLCV를 병렬로 수집해 심볼별 딕셔너리로 반환한다.

    Args:
        symbols:     티커 심볼 목록.
        period:      조회 기간. collect_ohlcv와 동일.
        interval:    데이터 간격. collect_ohlcv와 동일.
        max_workers: 동시 스레드 수 (기본 8).

    Returns:
        ``{symbol: [OhlcvRecord, ...]}`` 형태. 실패한 심볼은 결과에서 제외된다.

    Raises:
        StockDataCollectionError: 모든 심볼 수집이 실패한 경우.
    """
    log = logger.bind(symbols=symbols, period=period, interval=interval)
    log.info("stock_data_collection_multi.start", count=len(symbols))

    results: dict[str, list[OhlcvRecord]] = {}
    failed: list[str] = []

    with ThreadPoolExecutor(max_workers=min(max_workers, len(symbols))) as executor:
        futures = {
            executor.submit(collect_ohlcv, symbol, period, interval): symbol
            for symbol in symbols
        }
        for future in as_completed(futures):
            symbol = futures[future]
            try:
                results[symbol] = future.result()
            except StockDataCollectionError as exc:
                log.warning("stock_data_collection_multi.symbol_failed", symbol=symbol, error=str(exc))
                failed.append(symbol)

    if failed:
        log.error("stock_data_collection_multi.partial_failure", failed=failed)

    if not results:
        raise StockDataCollectionError(
            f"모든 심볼 수집 실패 — symbols={symbols}"
        )

    log.info("stock_data_collection_multi.success", success=len(results), failed=len(failed))
    return results
