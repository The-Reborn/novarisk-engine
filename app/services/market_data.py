import random
from app.core.databases import redis_client

INITIAL_MARKET_DATA = {
    "FX:EURUSD": 1.0850,
    "FX:GBPUSD": 1.2640,
    "FX:USDJPY": 151.20,
    "IR:USD_SOFR": 0.0532,
    "IR:EUR_ESTR": 0.0390,
}


def initialize_market_cache():
    """Seeds Redis with baseline market data if not already present."""
    for key, value in INITIAL_MARKET_DATA.items():
        if not redis_client.exists(key):
            redis_client.set(key, value)
    return {"message": "Market data cache initialized successfully."}


def get_market_rate(ticker: str) -> float:
    """Fetches a live market rate from the Redis hot-cache."""
    rate = redis_client.get(ticker)
    if rate is None:
        raise ValueError(f"Ticker {ticker} not found in market data cache.")
    return float(rate)


def simulate_market_tick():
    """Simulates a random market tick movement for testing real-time updates."""
    updated_rates = {}
    for key in INITIAL_MARKET_DATA.keys():
        current_rate = float(redis_client.get(key) or INITIAL_MARKET_DATA[key])
        
        shock = random.uniform(-0.001, 0.001)
        new_rate = round(current_rate * (1 + shock), 4)
        
        redis_client.set(key, new_rate)
        updated_rates[key] = new_rate
        
    return updated_rates