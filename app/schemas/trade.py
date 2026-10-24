from datetime import datetime
from pydantic import BaseModel, Field
from app.models.trade import InstrumentType


class TradeCreate(BaseModel):
    trade_id: str = Field(..., example="TRD-EURUSD-001")
    portfolio_id: str = Field(..., example="PORT_FX_DESK_1")
    instrument_type: InstrumentType = Field(..., example="FX_FORWARD")
    notional: float = Field(..., gt=0, example=1000000.0)
    currency_pair: str = Field(..., example="EURUSD")
    strike_rate: float = Field(..., gt=0, example=1.0820)
    maturity_date: datetime = Field(..., example="2026-12-31T00:00:00")
    counterparty: str | None = Field(None, example="Goldman Sachs")


class TradeResponse(TradeCreate):
    id: int
    trade_date: datetime

    class Config:
        from_attributes = True