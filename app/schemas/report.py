from datetime import datetime
from pydantic import BaseModel, Field


class ScenarioResult(BaseModel):
    scenario_name: str
    market_shock_applied: float
    portfolio_pv: float


class RiskReportCreate(BaseModel):
    report_id: str = Field(..., example="RPT-2026-10-24-001")
    portfolio_id: str = Field(..., example="PORT_FX_DESK_1")
    total_trades_analyzed: int
    base_portfolio_pv: float
    value_at_risk_95: float
    scenarios: list[ScenarioResult]
    created_at: datetime = Field(default_factory=datetime.utcnow)