"""
pipeline.collectors.stock_data_collector 단위 테스트

yfinance 네트워크 호출을 mock해 오프라인 환경에서도 동작한다.
"""

from __future__ import annotations

import datetime
from unittest.mock import patch

import pandas as pd
import pytest

from pipeline.collectors.stock_data_collector import collect_ohlcv, collect_ohlcvs
from pipeline.collectors.dtos.stock import OhlcvRecord
from pipeline.exceptions import StockDataCollectionError


def _make_ohlcv_df(rows: list[dict]) -> pd.DataFrame:
    """테스트용 OHLCV DataFrame을 생성한다."""
    index = pd.to_datetime([r["date"] for r in rows], utc=True)
    df = pd.DataFrame(
        {
            "Open": [r["open"] for r in rows],
            "High": [r["high"] for r in rows],
            "Low": [r["low"] for r in rows],
            "Close": [r["close"] for r in rows],
            "Volume": [r["volume"] for r in rows],
        },
        index=index,
    )
    return df


SAMPLE_ROW = {
    "date": "2024-01-02",
    "open": 185.12,
    "high": 186.74,
    "low": 184.50,
    "close": 185.85,
    "volume": 45_000_000,
}


@pytest.fixture
def mock_ticker_history():
    """_ticker_history를 mock하는 픽스처."""
    with patch(
        "pipeline.collectors.stock_data_collector._ticker_history"
    ) as mock_fn:
        yield mock_fn


class TestCollectOhlcv:
    def test_returns_ohlcv_records(self, mock_ticker_history):
        """정상 데이터가 반환되면 OhlcvRecord 리스트를 돌려준다."""
        mock_ticker_history.return_value = _make_ohlcv_df([SAMPLE_ROW])

        result = collect_ohlcv("AAPL", period="1d", interval="1d")

        assert len(result) == 1
        record = result[0]
        assert isinstance(record, OhlcvRecord)
        assert record.symbol == "AAPL"
        assert record.date == datetime.date(2024, 1, 2)
        assert record.open == pytest.approx(185.12, rel=1e-4)
        assert record.high == pytest.approx(186.74, rel=1e-4)
        assert record.low == pytest.approx(184.50, rel=1e-4)
        assert record.close == pytest.approx(185.85, rel=1e-4)
        assert record.volume == 45_000_000

    def test_multiple_rows(self, mock_ticker_history):
        """복수 행이 있으면 순서대로 모두 반환된다."""
        rows = [
            {**SAMPLE_ROW, "date": "2024-01-02"},
            {**SAMPLE_ROW, "date": "2024-01-03", "close": 186.00},
            {**SAMPLE_ROW, "date": "2024-01-04", "close": 187.50},
        ]
        mock_ticker_history.return_value = _make_ohlcv_df(rows)

        result = collect_ohlcv("AAPL", period="5d", interval="1d")

        assert len(result) == 3
        assert result[0].date == datetime.date(2024, 1, 2)
        assert result[2].close == pytest.approx(187.50, rel=1e-4)

    def test_empty_dataframe_raises(self, mock_ticker_history):
        """빈 DataFrame이 반환되면 StockDataCollectionError를 발생시킨다."""
        mock_ticker_history.return_value = pd.DataFrame()

        with pytest.raises(StockDataCollectionError, match="수집된 데이터가 없습니다"):
            collect_ohlcv("INVALID_TICKER", period="1d", interval="1d")

    def test_none_dataframe_raises(self, mock_ticker_history):
        """None이 반환되면 StockDataCollectionError를 발생시킨다."""
        mock_ticker_history.return_value = None

        with pytest.raises(StockDataCollectionError):
            collect_ohlcv("INVALID_TICKER", period="1d", interval="1d")

    def test_fetch_exception_raises(self, mock_ticker_history):
        """yfinance 호출 중 예외가 발생하면 StockDataCollectionError로 감싸 재발생한다."""
        mock_ticker_history.side_effect = RuntimeError("network error")

        with pytest.raises(StockDataCollectionError, match="yfinance 데이터 조회 실패"):
            collect_ohlcv("AAPL", period="1d", interval="1d")

    def test_passes_correct_args_to_ticker(self, mock_ticker_history):
        """symbol, period, interval이 _ticker_history에 올바르게 전달된다."""
        mock_ticker_history.return_value = _make_ohlcv_df([SAMPLE_ROW])

        collect_ohlcv("TSLA", period="5d", interval="1h")

        mock_ticker_history.assert_called_once_with(
            symbol="TSLA", period="5d", interval="1h"
        )

    def test_volume_is_int(self, mock_ticker_history):
        """volume 필드는 정수여야 한다."""
        mock_ticker_history.return_value = _make_ohlcv_df([SAMPLE_ROW])

        result = collect_ohlcv("AAPL")

        assert isinstance(result[0].volume, int)


class TestCollectOhlcvMulti:
    def test_returns_all_symbols(self, mock_ticker_history):
        """모든 심볼이 성공하면 심볼별 딕셔너리를 반환한다."""
        mock_ticker_history.return_value = _make_ohlcv_df([SAMPLE_ROW])

        result = collect_ohlcvs(["AAPL", "TSLA", "MSFT"])

        assert set(result.keys()) == {"AAPL", "TSLA", "MSFT"}
        assert all(isinstance(r, OhlcvRecord) for records in result.values() for r in records)

    def test_partial_failure_excludes_failed_symbol(self, mock_ticker_history):
        """일부 심볼이 실패해도 성공한 심볼의 결과는 반환한다."""
        def side_effect(symbol, period, interval):
            if symbol == "INVALID":
                return pd.DataFrame()
            return _make_ohlcv_df([SAMPLE_ROW])

        mock_ticker_history.side_effect = side_effect

        result = collect_ohlcvs(["AAPL", "INVALID", "TSLA"])

        assert "AAPL" in result
        assert "TSLA" in result
        assert "INVALID" not in result

    def test_all_failed_raises(self, mock_ticker_history):
        """모든 심볼이 실패하면 StockDataCollectionError를 발생시킨다."""
        mock_ticker_history.return_value = pd.DataFrame()

        with pytest.raises(StockDataCollectionError, match="모든 심볼 수집 실패"):
            collect_ohlcvs(["INVALID1", "INVALID2"])

    def test_parallel_call_count(self, mock_ticker_history):
        """심볼 수만큼 _ticker_history가 호출된다."""
        mock_ticker_history.return_value = _make_ohlcv_df([SAMPLE_ROW])

        collect_ohlcvs(["AAPL", "TSLA", "MSFT"])

        assert mock_ticker_history.call_count == 3
