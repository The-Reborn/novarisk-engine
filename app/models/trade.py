from datetime import datetime
import enum
from sqlalchemy import Column, DateTime, Enum as SQLEnum, Float, Integer, String
from app.core.databases import Base


class InstrumentType(str, enum.Enum):
    FX_FORWARD = "FX_FORWARD"
    INTEREST_RATE_SWAP = "IRS"
    FX_SPOT = "FX_SPOT"
    VANILLA_OPTION = "OPTION"


class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    trade_id = Column(String, unique=True, index=True, nullable=False)
    portfolio_id = Column(String, index=True, nullable=False)
    instrument_type = Column(SQLEnum(InstrumentType), nullable=False)
    notional = Column(Float, nullable=False)
    currency_pair = Column(String, nullable=False)  # e.g., "EURUSD"
    strike_rate = Column(Float, nullable=False)
    trade_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    maturity_date = Column(DateTime, nullable=False)
    counterparty = Column(String, nullable=True)