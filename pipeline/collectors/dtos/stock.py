from datetime import date

from pydantic import BaseModel, Field


class OhlcvRecord(BaseModel):
    symbol: str
    date: date
    open: float = Field(ge=0)
    high: float = Field(ge=0)
    low: float = Field(ge=0)
    close: float = Field(ge=0)
    volume: int = Field(ge=0)
