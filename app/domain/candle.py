from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class Candle(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source: str
    symbol: str
    interval: str
    candle_time: datetime
    open_price: Decimal
    high_price: Decimal
    low_price: Decimal
    close_price: Decimal
    adj_close: Decimal | None = None
    volume: Decimal | None = None
    ingest_time: datetime
    created_at: datetime
    updated_at: datetime
