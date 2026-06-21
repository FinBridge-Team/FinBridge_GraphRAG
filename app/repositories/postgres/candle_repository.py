from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session_factory
from app.domain.candle import Candle
from app.repositories.postgres.models.candle import CandleModel


class CandleRepository:
    source = "yfinance"
    interval = "1m"

    def __init__(self, session: AsyncSession | None = None) -> None:
        self.session = session

    async def get_latest_candles(
        self,
        *,
        symbol: list[str] | str | None = None,
    ) -> list[Candle]:
        statement = (
            self._base_query(symbol)
            .distinct(CandleModel.symbol)
            .order_by(CandleModel.symbol, CandleModel.candle_time.desc())
        )
        return await self._fetch_candles(statement)

    def _base_query(self, symbol: list[str] | str | None = None) -> select:
        statement = select(CandleModel).where(
            CandleModel.source == self.source,
            CandleModel.interval == self.interval,
        )
        if symbol is not None:
            statement = statement.where(CandleModel.symbol.in_(self._normalize_symbol(symbol)))
        return statement

    @staticmethod
    def _normalize_symbol(symbol: list[str] | str) -> list[str]:
        if isinstance(symbol, str):
            symbol = [symbol]
        normalized_symbols = [s.upper().strip() for s in symbol if s.strip()]
        if not normalized_symbols:
            raise ValueError("symbol must contain at least one non-empty symbol")
        return normalized_symbols

    async def _fetch_candles(self, statement) -> list[Candle]:
        if self.session is not None:
            result = await self.session.scalars(statement)
            return [Candle.model_validate(row) for row in result.all()]

        session_factory = get_session_factory()
        async with session_factory() as session:
            result = await session.scalars(statement)
            return [Candle.model_validate(row) for row in result.all()]
