from sqlalchemy import Column, Float, String, Integer
from app.core.databases import Base

class PortfolioRiskLimit(Base):
    __tablename__ = "portfolio_risk_limits"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    portfolio_id = Column(String, unique=True, index=True, nullable=False)
    max_loss_limit = Column(Float, nullable=False)    # e.g., -200000.0 (Max allowable negative PV)
    max_delta_limit = Column(Float, nullable=True)    # e.g., 500000.0 (Max Delta exposure)