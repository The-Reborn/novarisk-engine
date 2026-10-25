from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.databases import get_db, mongodb
from app.models.risk import PortfolioRiskLimit
from app.services.risk_engine import run_portfolio_risk_simulation

router = APIRouter(prefix="/risk", tags=["Risk Management & Alerting"])

class RiskLimitCreate(BaseModel):
    portfolio_id: str
    max_loss_limit: float
    max_delta_limit: float | None = None


@router.post("/limits/", status_code=status.HTTP_201_CREATED)
def set_portfolio_limit(limit_in: RiskLimitCreate, db: Session = Depends(get_db)):
    """Set or update risk limits for a specific portfolio in PostgreSQL."""
    existing = db.query(PortfolioRiskLimit).filter(PortfolioRiskLimit.portfolio_id == limit_in.portfolio_id).first()
    if existing:
        existing.max_loss_limit = limit_in.max_loss_limit
        existing.max_delta_limit = limit_in.max_delta_limit
        db.commit()
        db.refresh(existing)
        return {"message": f"Risk limits updated for portfolio {limit_in.portfolio_id}", "limit": limit_in}

    new_limit = PortfolioRiskLimit(
        portfolio_id=limit_in.portfolio_id,
        max_loss_limit=limit_in.max_loss_limit,
        max_delta_limit=limit_in.max_delta_limit
    )
    db.add(new_limit)
    db.commit()
    return {"message": f"Risk limits created for portfolio {limit_in.portfolio_id}", "limit": limit_in}


@router.post("/simulate/{portfolio_id}")
async def simulate_risk(portfolio_id: str, db: Session = Depends(get_db)):
    """Triggers portfolio stress simulation, evaluates risk limits, and saves report to MongoDB."""
    try:
        report = await run_portfolio_risk_simulation(portfolio_id, db)
        return report
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/alerts/active")
async def get_active_breaches():
    """Retrieves recent portfolio risk reports where a limit breach occurred from MongoDB."""
    if mongodb.db is None:
        from app.core.databases import connect_to_mongo
        connect_to_mongo()
    
    # Query MongoDB for reports marked as BREACH
    breached_reports = await mongodb.db.risk_reports.find(
        {"portfolio_status": "BREACH"}, 
        {"_id": 0}
    ).sort("created_at", -1).limit(10).to_list(length=10)
    
    return {
        "active_breach_count": len(breached_reports),
        "breaches": breached_reports
    }