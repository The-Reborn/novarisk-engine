from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.trade import InstrumentType


class TradeCreate(BaseModel):
    trade_id: str
    portfolio_id: str
    instrument_type: InstrumentType
    notional: float
    currency_pair: str
    strike_rate: float
    option_type: Optional[str] = None
    maturity_date: datetime
    counterparty: Optional[str] = None

class TradeResponse(TradeCreate):
    id: int
    trade_date: datetime
    
    class Config:
        from_attributes = True