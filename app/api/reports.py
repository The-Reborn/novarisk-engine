from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.databases import get_db, mongodb
from app.services.risk_engine import run_portfolio_risk_simulation

router = APIRouter(prefix="/reports", tags=["Risk Simulation Reports (MongoDB)"])


@router.post("/simulate/{portfolio_id}")
async def generate_risk_report(portfolio_id: str, db: Session = Depends(get_db)):
    """Run a risk simulation on PostgreSQL trades and store the report in MongoDB."""
    try:
        report = await run_portfolio_risk_simulation(portfolio_id, db)
        return {"message": "Risk simulation completed successfully.", "report": report}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{report_id}")
async def get_risk_report(report_id: str):
    """Fetch a stored risk simulation report directly from MongoDB."""
    db_mongo = mongodb.db
    report = await db_mongo.risk_reports.find_one({"report_id": report_id})
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Report '{report_id}' not found.")
    
    report.pop("_id", None)
    return report