# --- Add this function to your existing economics.py ---
import pandas as pd
from src.intraday_arbitrage import (
    theoretical_revenue, spread_based_revenue, thresholds_based_revenue, _ensure_price_kwh
)

def intraday_revenue(cfg, E_kWh, P_kW, DoD, eta_rt):
    """Compute arbitrage revenue according to cfg['intraday'].
       Returns EUR for the price series period (or per year for theoretical)."""
    intr = cfg.get("intraday", {})
    prices_csv = intr.get("prices_csv")
    mode = intr.get("mode", "threshold")

    prices = None
    if prices_csv:
        prices_df = pd.read_csv(f"data/{prices_csv}")
        prices = _ensure_price_kwh(prices_df)

    if mode == "theoretical":
        return theoretical_revenue(E_kWh, DoD, eta_rt,
                                   intr["delta_p_eur_per_kWh"],
                                   intr["cycles_per_day"],
                                   days=365)
    elif mode == "spread":
        if prices is None: return 0.0
        rev, _ = spread_based_revenue(prices, E_KWh=E_kWh, DoD=DoD, P_kW=P_kW,
                                      eta_rt=eta_rt, cycles_cap_per_day=intr.get("cycles_per_day_cap", 1.0))
        return rev
    elif mode == "threshold":
        if prices is None: return 0.0
        rev, _ = thresholds_based_revenue(prices, E_kWh, DoD, P_kW, eta_rt,
            intr["buy_threshold_eur_per_MWh"]/1000.0,
            intr["sell_threshold_eur_per_MWh"]/1000.0,
            intr.get("cycles_per_day_cap", 1.0))
        return rev
    else:
        return 0.0
