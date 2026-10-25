from datetime import datetime
from sqlalchemy.orm import Session
from app.core.databases import mongodb, connect_to_mongo
from app.models.trade import Trade
from app.models.risk import PortfolioRiskLimit  # <-- From PostgreSQL limits model
from app.services.pricing import price_trade
from app.services.market_data import get_market_rate


async def run_portfolio_risk_simulation(portfolio_id: str, db: Session) -> dict:
    """
    Simulates a risk report for a portfolio, checks against risk limits,
    generates alerts if breached, and saves the rich JSON report to MongoDB.
    """
    if mongodb.db is None:
        connect_to_mongo()

    # 1. Fetch trades from PostgreSQL
    trades = db.query(Trade).filter(Trade.portfolio_id == portfolio_id).all()
    if not trades:
        raise ValueError(f"No trades found for portfolio '{portfolio_id}'")

    # 2. Calculate base portfolio PV & total Delta
    base_pv = 0.0
    total_delta = 0.0
    priced_trades = []
    
    for trade in trades:
        valuation = price_trade(trade)
        pv = valuation["present_value"]
        base_pv += pv
        
        # Aggregate Delta if it's an option
        greeks = valuation.get("greeks", {})
        if "delta" in greeks:
            total_delta += greeks["delta"] * trade.notional

        priced_trades.append(valuation)

    # 3. Simulate Stress Scenarios (FX market shocks)
    shocks = [-0.02, -0.01, 0.0, 0.01, 0.02]
    scenarios = []
    
    for shock in shocks:
        shocked_pv = 0.0
        for trade in trades:
            ticker = f"FX:{trade.currency_pair}"
            try:
                base_spot = get_market_rate(ticker)
            except ValueError:
                base_spot = trade.strike_rate
            
            shocked_spot = base_spot * (1 + shock)
            trade_shocked_pv = trade.notional * (shocked_spot - trade.strike_rate)
            shocked_pv += trade_shocked_pv

        scenarios.append({
            "scenario_name": f"FX_SHOCK_{int(shock * 100)}PCT",
            "market_shock_applied": shock,
            "portfolio_pv": round(shocked_pv, 2)
        })

    pvs = [s["portfolio_pv"] for s in scenarios]
    var_95 = round(base_pv - min(pvs), 2)

    # 4. Check PostgreSQL Risk Limits & Generate Alerts
    limit_record = db.query(PortfolioRiskLimit).filter(PortfolioRiskLimit.portfolio_id == portfolio_id).first()
    alerts = []
    status = "HEALTHY"

    if limit_record:
        if base_pv < limit_record.max_loss_limit:
            status = "BREACH"
            alerts.append({
                "alert_type": "MAX_LOSS_BREACH",
                "severity": "HIGH",
                "message": f"Portfolio {portfolio_id} PV ({base_pv}) breached max loss limit ({limit_record.max_loss_limit})."
            })

        if limit_record.max_delta_limit and abs(total_delta) > limit_record.max_delta_limit:
            status = "BREACH"
            alerts.append({
                "alert_type": "MAX_DELTA_BREACH",
                "severity": "MEDIUM",
                "message": f"Portfolio {portfolio_id} absolute Delta ({total_delta}) breached limit ({limit_record.max_delta_limit})."
            })

    # 5. Construct MongoDB Report Document (including alerts & risk status)
    report_data = {
        "report_id": f"RPT-{portfolio_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "portfolio_id": portfolio_id,
        "portfolio_status": status,
        "total_trades_analyzed": len(trades),
        "base_portfolio_pv": round(base_pv, 2),
        "total_delta_exposure": round(total_delta, 2),
        "value_at_risk_95": var_95,
        "alerts": alerts,
        "scenarios": scenarios,
        "created_at": datetime.utcnow()
    }

    # Insert into MongoDB collection 'risk_reports'
    db_mongo = mongodb.db
    await db_mongo.risk_reports.insert_one(report_data)
    
    report_data.pop("_id", None)
    return report_data