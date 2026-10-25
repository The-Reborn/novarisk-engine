import uuid
from fastapi.testclient import TestClient
from fastapi import status
from app.main import app

client = TestClient(app)

def test_book_and_get_trade():
    """Test successful booking and retrieval of a trade with a unique ID."""
    unique_id = f"TRD-FX-{uuid.uuid4().hex[:6]}"
    payload = {
        "trade_id": unique_id,
        "portfolio_id": "PORT_FX_DESK",
        "instrument_type": "FX_FORWARD",
        "currency_pair": "GBPUSD",
        "notional": 250000.0,
        "strike_rate": 1.2500,
        "maturity_date": "2027-06-30T00:00:00"
    }
    
    response = client.post("/api/v1/trades/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["trade_id"] == unique_id

    get_response = client.get(f"/api/v1/trades/{unique_id}")
    assert get_response.status_code == status.HTTP_200_OK
    assert get_response.json()["currency_pair"] == "GBPUSD"

def test_duplicate_trade_rejection():
    """Ensure booking a duplicate trade ID returns a 400 Bad Request."""
    unique_id = f"TRD-DUP-{uuid.uuid4().hex[:6]}"
    payload = {
        "trade_id": unique_id,
        "portfolio_id": "PORT_FX_DESK",
        "instrument_type": "FX_FORWARD",
        "currency_pair": "USDJPY",
        "notional": 100000.0,
        "strike_rate": 150.0,
        "maturity_date": "2027-06-30T00:00:00"
    }
    res1 = client.post("/api/v1/trades/", json=payload)
    assert res1.status_code == status.HTTP_201_CREATED

    res2 = client.post("/api/v1/trades/", json=payload)
    assert res2.status_code == status.HTTP_400_BAD_REQUEST

def test_get_nonexistent_trade():
    """Ensure fetching a missing trade returns 404 Not Found."""
    response = client.get("/api/v1/trades/NON-EXISTENT-TRD")
    assert response.status_code == status.HTTP_404_NOT_FOUND