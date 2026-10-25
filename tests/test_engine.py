import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    """Ensure the app is running."""
    response = client.get("/")
    assert response.status_code in [200, 404]

def test_book_and_price_option_trade():
    """Test booking an option trade and verifying live Black-Scholes pricing and Greeks."""
    unique_id = f"TRD-OPT-{uuid.uuid4().hex[:6]}"
    trade_payload = {
        "trade_id": unique_id,
        "portfolio_id": "PORT_TEST_DESK",
        "instrument_type": "OPTION",
        "currency_pair": "EURUSD",
        "notional": 500000.0,
        "strike_rate": 1.0900,
        "option_type": "CALL",
        "maturity_date": "2027-10-25T00:00:00"
    }

    response = client.post("/api/v1/trades/", json=trade_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["trade_id"] == unique_id

    pricing_response = client.get(f"/api/v1/pricing/trade/{unique_id}")
    assert pricing_response.status_code == 200
    pricing_data = pricing_response.json()
    
    assert "present_value" in pricing_data
    assert "greeks" in pricing_data
    assert "delta" in pricing_data["greeks"]