from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.databases import get_db
from app.models.trade import Trade
from app.schemas.trade import TradeCreate, TradeResponse

router = APIRouter(prefix="/trades", tags=["Trade Booking & Portfolio"])


@router.post("/", response_model=TradeResponse, status_code=status.HTTP_201_CREATED)
def book_trade(trade_in: TradeCreate, db: Session = Depends(get_db)):
    """Book a new financial trade into PostgreSQL."""
    existing = db.query(Trade).filter(Trade.trade_id == trade_in.trade_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Trade with ID '{trade_in.trade_id}' already exists.",
        )

    db_trade = Trade(**trade_in.dict())
    db.add(db_trade)
    db.commit()
    db.refresh(db_trade)
    return db_trade


@router.get("/", response_model=list[TradeResponse])
def list_trades(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve a list of all booked trades from PostgreSQL."""
    trades = db.query(Trade).offset(skip).limit(limit).all()
    return trades


@router.get("/{trade_id}", response_model=TradeResponse)
def get_trade_by_id(trade_id: str, db: Session = Depends(get_db)) :
    """Retrieve a specific trade by its unique trade_id string."""
    trade = db.query(Trade).filter(Trade.trade_id == trade_id).first()
    if not trade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trade '{trade_id}' not found.",
        )
    return trade