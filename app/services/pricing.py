import math
from datetime import datetime
from app.models.trade import Trade, InstrumentType
from app.services.market_data import get_market_rate


def calculate_fx_forward_pv(trade: Trade, spot_rate: float) -> float:
    """
    Simple analytic Present Value (PV) calculation for an FX Forward.
    PV = Notional * (Spot_Rate - Strike_Rate) adjusted or simplified for demonstration.
    For a strict FX Forward: PV = Notional * (Current_Spot - Strike) / (1 + r*T), 
    we will use a clean spot-vs-strike differential model scaled by notional.
    """
    if trade.currency_pair == "EURUSD":
        pv = trade.notional * (spot_rate - trade.strike_rate)
    else:
        pv = trade.notional * (spot_rate - trade.strike_rate)
    
    return round(pv, 2)


def calculate_irs_pv(trade: Trade,) -> float:
    """
    Simplified Interest Rate Swap (IRS) valuation.
    Returns the computed PV and the fetched market floating rate.
    """
    fixed_rate = float(trade.strike_rate)
    
    benchmark_ticker = f"IR:USD_SOFR"
    try:
        market_floating_rate = get_market_rate(benchmark_ticker)
    except ValueError:
        market_floating_rate = 0.045

    # Simple valuation model: receiving fixed, paying floating (or vice versa)
    # If market rates go up, a fixed-rate payer swap loses value.
    rate_differential = fixed_rate - market_floating_rate
    pv = trade.notional * rate_differential * 5.0  # Assumed 5-year tenor scaling factor
    
    return round(pv, 2)


def normal_cdf(x: float) -> float:
    """Standard normal cumulative distribution function using math.erf."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def normal_pdf(x: float) -> float:
    """Standard normal probability density function."""
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def calculate_black_scholes_pv(trade: Trade, spot_rate: float) -> dict:
    """
    Computes European Option Present Value and Greeks using the Black-Scholes model.
    """
    S = spot_rate
    K = float(trade.strike_rate or spot_rate)
    
    # Calculate Time to Maturity (T) in years from now
    if trade.maturity_date:
        delta_seconds = (trade.maturity_date - datetime.utcnow()).total_seconds()
        T = max(delta_seconds / (365.25 * 24 * 3600), 0.0001) # Avoid zero division
    else:
        T = 1.0

    try:
        r = get_market_rate("IR:USD_SOFR")
    except ValueError:
        r = 0.0532

    try:
        sigma = get_market_rate(f"VOL:{trade.currency_pair}")
    except ValueError:
        sigma = 0.15

    is_call = (trade.option_type or "CALL").upper() == "CALL"

    # Black-Scholes d1 and d2 formulas
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)

    if is_call:
        price = S * normal_cdf(d1) - K * math.exp(-r * T) * normal_cdf(d2)
        delta = normal_cdf(d1)
    else:
        price = K * math.exp(-r * T) * normal_cdf(-d2) - S * normal_cdf(-d1)
        delta = normal_cdf(d1) - 1.0

    # Greeks calculation
    gamma = normal_pdf(d1) / (S * sigma * math.sqrt(T))
    vega = S * math.sqrt(T) * normal_pdf(d1) / 100.0  # Scaled for 1% volatility change

    total_pv = round(price * trade.notional, 2)

    return {
        "present_value": total_pv,
        "unit_option_price": round(price, 4),
        "implied_volatility": sigma,
        "risk_free_rate": r,
        "time_to_maturity_years": round(T, 4),
        "greeks": {
            "delta": round(delta, 4),
            "gamma": round(gamma, 4),
            "vega": round(vega, 4)
        }
    }


def price_trade(trade: Trade) -> dict:
    """Dispatches trade pricing based on instrument type using Redis market data."""
    if trade.instrument_type in [InstrumentType.FX_FORWARD, InstrumentType.FX_SPOT]:
        ticker = f"FX:{trade.currency_pair}"
        try:
            spot_rate = get_market_rate(ticker)
        except ValueError:
            spot_rate = trade.strike_rate

        pv = calculate_fx_forward_pv(trade, spot_rate)
        
        return {
            "trade_id": trade.trade_id,
            "instrument_type": trade.instrument_type,
            "currency_pair": trade.currency_pair,
            "notional": trade.notional,
            "strike_rate": trade.strike_rate,
            "live_market_rate": spot_rate,
            "present_value": pv,
            "currency": "USD"
        }

    elif trade.instrument_type == InstrumentType.INTEREST_RATE_SWAP:
        pv = calculate_irs_pv(trade)
        return {
            "trade_id": trade.trade_id,
            "instrument_type": trade.instrument_type,
            "currency_pair": trade.currency_pair or "USD",
            "notional": trade.notional,
            "present_value": pv,
            "currency": "USD"
        }
    
    elif trade.instrument_type == InstrumentType.VANILLA_OPTION:
        ticker = f"FX:{trade.currency_pair}"
        try:
            spot_rate = get_market_rate(ticker)
        except ValueError:
            spot_rate = 1.0850

        bs_result = calculate_black_scholes_pv(trade, spot_rate)
        return {
            "trade_id": trade.trade_id,
            "instrument_type": trade.instrument_type,
            "currency_pair": trade.currency_pair,
            "notional": trade.notional,
            "strike_rate": trade.strike_rate,
            "option_type": trade.option_type,
            "live_market_rate": spot_rate,
            **bs_result,
            "currency": "USD"
        }
    
    raise NotImplementedError(f"Pricing model for {trade.instrument_type} not yet implemented.")