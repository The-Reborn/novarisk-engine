import uuid
from fastapi.testclient import TestClient
from fastapi import status
from app.main import app

client = TestClient(app)

def test_price_option_trade():
    """Test Black-Scholes valuation and Greeks for an option trade."""
    trade_id = f"TRD-PRC-OPT-{uuid.uuid4().hex[:6]}"
    payload = {
        "trade_id": trade_id,
        "portfolio_id": "PORT_DERIVATIVES_DESK",
        "instrument_type": "OPTION",
        "currency_pair": "EURUSD",
        "notional": 1000000.0,
        "strike_rate": 1.0900,
        "option_type": "CALL",
        "maturity_date": "2027-10-25T00:00:00"
    }
    client.post("/api/v1/trades/", json=payload)

    response = client.get(f"/api/v1/pricing/trade/{trade_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["present_value"] is not None
    assert "greeks" in data
    assert "delta" in data["greeks"]

def test_price_fx_forward_trade():
    """Test valuation of an FX Forward trade."""
    trade_id = f"TRD-PRC-FX-{uuid.uuid4().hex[:6]}"
    payload = {
        "trade_id": trade_id,
        "portfolio_id": "PORT_FX_DESK",
        "instrument_type": "FX_FORWARD",
        "currency_pair": "EURUSD",
        "notional": 500000.0,
        "strike_rate": 1.0800,
        "maturity_date": "2027-12-31T00:00:00"
    }
    client.post("/api/v1/trades/", json=payload)

    response = client.get(f"/api/v1/pricing/trade/{trade_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "present_value" in data

def test_price_nonexistent_trade():
    """Ensure pricing a non-existent trade returns 404."""
    response = client.get("/api/v1/pricing/trade/MISSING-TRD")
    assert response.status_code == status.HTTP_404_NOT_FOUND