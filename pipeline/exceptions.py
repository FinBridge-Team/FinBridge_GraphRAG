"""pipeline 패키지 공통 예외 클래스."""


class StockDataCollectionError(RuntimeError):
    """주가 데이터 수집 실패 시 발생하는 예외."""
