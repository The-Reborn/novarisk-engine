from datetime import datetime
from sqlalchemy.orm import Session
from app.core.databases import mongodb, connect_to_mongo
from app.models.trade import Trade
from app.services.pricing import price_trade
from app.services.market_data import get_market_rate


async def run_portfolio_risk_simulation(portfolio_id: str, db: Session) -> dict:
    """
    Simulates a risk report for a portfolio:
    1. Fetches all trades for the portfolio from PostgreSQL.
    2. Computes base PV.
    3. Runs mock market stress scenarios (-2% to +2% FX shocks).
    4. Saves the rich JSON report to MongoDB.
    """

    if mongodb.db is None:
        connect_to_mongo()

    # 1. Fetch trades from PostgreSQL
    trades = db.query(Trade).filter(Trade.portfolio_id == portfolio_id).all()
    if not trades:
        raise ValueError(f"No trades found for portfolio '{portfolio_id}'")

    # 2. Calculate base portfolio PV
    base_pv = 0.0
    priced_trades = []
    for trade in trades:
        valuation = price_trade(trade)
        base_pv += valuation["present_value"]
        priced_trades.append(valuation)

    # 3. Simulate Stress Scenarios (e.g., FX market shocks)
    shocks = [-0.02, -0.01, 0.0, 0.01, 0.02]  # -2% to +2% market shifts
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

            # Simple linear shock re-valuation
            trade_shocked_pv = trade.notional * (shocked_spot - trade.strike_rate)
            shocked_pv += trade_shocked_pv

        scenarios.append({
            "scenario_name": f"FX_SHOCK_{int(shock * 100)}PCT",
            "market_shock_applied": shock,
            "portfolio_pv": round(shocked_pv, 2)
        })

    # Simple mock Value at Risk (VaR 95%) calculation based on scenario spread
    pvs = [s["portfolio_pv"] for s in scenarios]
    var_95 = round(base_pv - min(pvs), 2)  # Downside risk buffer

    # 4. Construct MongoDB Report Document
    report_data = {
        "report_id": f"RPT-{portfolio_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "portfolio_id": portfolio_id,
        "total_trades_analyzed": len(trades),
        "base_portfolio_pv": round(base_pv, 2),
        "value_at_risk_95": var_95,
        "scenarios": scenarios,
        "created_at": datetime.utcnow()
    }

    # Insert into MongoDB collection 'risk_reports'
    db_mongo = mongodb.db
    await db_mongo.risk_reports.insert_one(report_data)
    
    # Remove MongoDB's internal _id field for clean API output
    report_data.pop("_id", None)
    return report_data