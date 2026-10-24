from fastapi import APIRouter
from app.core.databases import redis_client
from app.services.market_data import (
    initialize_market_cache,
    simulate_market_tick,
    INITIAL_MARKET_DATA,
)

router = APIRouter(prefix="/market", tags=["Market Data & Redis Cache"])


@router.post("/init")
def init_market_data():
    """Initialize Redis with baseline FX and Interest Rate data."""
    return initialize_market_cache()


@router.get("/rates")
def get_all_rates():
    """Fetch all current market rates from the Redis cache."""
    rates = {}
    for key in INITIAL_MARKET_DATA.keys():
        val = redis_client.get(key)
        if val:
            rates[key] = float(val)
    return {"market_data": rates}


@router.post("/tick")
def trigger_market_tick():
    """Simulate a real-time market tick update across all instruments."""
    new_rates = simulate_market_tick()
    return {"message": "Market rates updated via tick simulation", "rates": new_rates}