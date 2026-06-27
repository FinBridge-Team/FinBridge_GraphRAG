"""PostgreSQL 저장소 패키지."""

from app.repositories.postgres.stock_repository import StockRepository
from app.repositories.postgres.stub_stock_repository import StubStockRepository

__all__ = ["StockRepository", "StubStockRepository"]
