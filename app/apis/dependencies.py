"""FastAPI 의존성 주입 설정.

⚠️  DB 교체 지점:
    현재는 StubStockRepository(메모리 stub)를 사용합니다.
    DB 담당자가 PostgresStockRepository 를 구현하면
    아래 get_stock_service() 의 repo 인스턴스만 교체하면 됩니다.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from app.repositories.postgres.stub_stock_repository import StubStockRepository
from app.services.stock_service import StockService


def get_stock_service() -> StockService:
    """StockService 인스턴스를 제공합니다.

    ── DB 교체 방법 ──────────────────────────────────────────────────
    from app.repositories.postgres.postgres_stock_repository import PostgresStockRepository
    repo = PostgresStockRepository(session=...)  # DB 세션 주입
    return StockService(repo=repo)
    ──────────────────────────────────────────────────────────────────
    """
    repo = StubStockRepository()
    return StockService(repo=repo)


# 라우터에서 Annotated 타입으로 간결하게 사용할 수 있도록 별칭 제공
StockServiceDep = Annotated[StockService, Depends(get_stock_service)]
