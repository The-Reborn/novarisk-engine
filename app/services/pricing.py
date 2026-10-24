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


def price_trade(trade: Trade) -> dict:
    """Dispatches trade pricing based on instrument type using Redis market data."""
    if trade.instrument_type == InstrumentType.FX_FORWARD or trade.instrument_type == InstrumentType.FX_SPOT:
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
    
    raise NotImplementedError(f"Pricing model for {trade.instrument_type} not yet implemented.")