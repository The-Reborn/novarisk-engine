from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.databases import get_db
from app.models.trade import Trade
from app.services.pricing import price_trade

router = APIRouter(prefix="/pricing", tags=["Quantitative Pricing Engine"])


@router.get("/trade/{trade_id}")
def get_trade_valuation(trade_id: str, db: Session = Depends(get_db)):
    """Fetch a trade from PostgreSQL, pull live market data from Redis, and compute real-time PV."""
    trade = db.query(Trade).filter(Trade.trade_id == trade_id).first()
    if not trade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trade '{trade_id}' not found.",
        )
    
    try:
        valuation = price_trade(trade)
        return valuation
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pricing calculation failed: {str(e)}",
        )