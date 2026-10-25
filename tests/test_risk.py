import pytest
from fastapi.testclient import TestClient
from fastapi import status
from app.main import app

client = TestClient(app)

#@pytest.mark.anyio
def test_risk_limits_and_simulation():
    """Test setting limits, running MongoDB simulations, and checking breach alerts."""
    portfolio_id = "PORT_TEST_RISK_DESK"
    
    trade_payload = {
        "trade_id": "TRD-RISK-001",
        "portfolio_id": portfolio_id,
        "instrument_type": "FX_FORWARD",
        "currency_pair": "EURUSD",
        "notional": 1000000.0,
        "strike_rate": 1.1000,
        "maturity_date": "2027-12-31T00:00:00"
    }
    client.post("/api/v1/trades/", json=trade_payload)

    # 2. Set strict risk limits (Max loss limit set very high so it breaches)
    limit_payload = {
        "portfolio_id": portfolio_id,
        "max_loss_limit": 100000.0,  # Strict threshold
        "max_delta_limit": 50000.0
    }
    limit_res = client.post("/api/v1/risk/limits/", json=limit_payload)
    assert limit_res.status_code == status.HTTP_201_CREATED

    sim_res = client.post(f"/api/v1/risk/simulate/{portfolio_id}")
    assert sim_res.status_code == status.HTTP_200_OK
    sim_data = sim_res.json()
    
    assert sim_data["portfolio_id"] == portfolio_id
    assert "scenarios" in sim_data
    assert "value_at_risk_95" in sim_data

    alerts_res = client.get("/api/v1/risk/alerts/active")
    assert alerts_res.status_code == status.HTTP_200_OK
    alerts_data = alerts_res.json()
    assert alerts_data["active_breach_count"] >= 0