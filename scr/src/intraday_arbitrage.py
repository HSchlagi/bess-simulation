import pandas as pd
import numpy as np

def _ensure_price_kwh(df: pd.DataFrame) -> pd.Series:
    """Accept either EUR/kWh or EUR/MWh (converted), index by timestamp."""
    if "price_EUR_per_kWh" in df.columns:
        s = df["price_EUR_per_kWh"].astype(float)
    elif "price_EUR_per_MWh" in df.columns:
        s = (df["price_EUR_per_MWh"].astype(float) / 1000.0)
    else:
        raise ValueError("Price CSV must have price_EUR_per_kWh or price_EUR_per_MWh.")
    s.index = pd.to_datetime(df["timestamp"])
    return s.sort_index()

def theoretical_revenue(E_kWh, DoD, eta_rt, delta_p_eur_per_kWh, cycles_per_day, days=365):
    """E_use * Δp * cycles/day * days * η_rt."""
    E_use = E_kWh * DoD
    return float(E_use * delta_p_eur_per_kWh * cycles_per_day * days * eta_rt)

def spread_based_revenue(prices: pd.Series, E_kWh, DoD, P_kW, eta_rt, cycles_cap_per_day=1.0):
    """Upper-bound using daily high-low spread."""
    E_use = E_kWh * DoD
    cycles_power_cap = 12.0 * (P_kW / E_kWh) if E_kWh > 0 else 0.0
    cycles_per_day = min(cycles_cap_per_day, cycles_power_cap)
    if cycles_per_day <= 0:
        return 0.0, pd.DataFrame()

    df = prices.to_frame("price")
    df["date"] = df.index.date
    agg = df.groupby("date").agg(daily_max=("price","max"), daily_min=("price","min"))
    agg["spread"] = agg["daily_max"] - agg["daily_min"]
    agg["rev_day"] = E_use * cycles_per_day * agg["spread"] * eta_rt
    return float(agg["rev_day"].sum()), agg

def thresholds_based_revenue(prices: pd.Series, E_kWh, DoD, P_kW, eta_rt,
                             buy_thr, sell_thr, cycles_cap_per_day=1.0):
    """Threshold model: charge if price<=buy_thr, discharge if price>=sell_thr.
       Energy limited by power*time and E_use*cycles_cap. Revenue uses mean buy/sell prices per day.
    """
    E_use = E_kWh * DoD
    cycles_power_cap = 12.0 * (P_kW / E_kWh) if E_kWh > 0 else 0.0
    cycles_per_day = min(cycles_cap_per_day, cycles_power_cap)
    if cycles_per_day <= 0:
        return 0.0, pd.DataFrame()

    if len(prices.index) < 2:
        raise ValueError("Need at least two price points.")
    dt_hours = np.median(np.diff(prices.index.values).astype("timedelta64[m]"))/60.0

    df = prices.to_frame("price")
    df["date"] = df.index.date
    out = []
    for d, g in df.groupby("date"):
        buy = g[g["price"] <= buy_thr]
        sell = g[g["price"] >= sell_thr]
        buy_time_h = len(buy) * dt_hours
        sell_time_h = len(sell) * dt_hours
        e_buy_max = min(buy_time_h * P_kW, E_use * cycles_per_day)
        e_sell_max = min(sell_time_h * P_kW, E_use * cycles_per_day)
        e_trade = min(e_buy_max, e_sell_max)
        if e_trade > 0 and len(buy)>0 and len(sell)>0:
            buy_avg = buy["price"].mean()
            sell_avg = sell["price"].mean()
            rev = e_trade * max(0.0, sell_avg - buy_avg) * eta_rt
        else:
            buy_avg = float("nan"); sell_avg = float("nan"); rev = 0.0
        out.append({"date": d, "e_trade_kWh": e_trade, "buy_avg": buy_avg, "sell_avg": sell_avg, "rev_day": rev})
    res = pd.DataFrame(out)
    total = float(res["rev_day"].sum())
    return total, res

def daily_cycles_power_cap(E_kWh, P_kW):
    return 12.0 * (P_kW / E_kWh) if E_kWh>0 else 0.0
