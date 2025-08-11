"""
Intraday-Arbitrage Modul für BESS-Simulation
============================================

Dieses Modul implementiert verschiedene Strategien für Intraday-Handel mit Batteriespeichern:
- theoretical: Theoretische Erlöse basierend auf Preisunterschieden
- spread: Tägliche High-Low Spreads (Upper Bound)
- threshold: Realistische Schwellenwert-basierte Arbitrage

Autor: BESS-Simulation Team
"""

import pandas as pd
import numpy as np
from typing import Tuple, Optional

def _ensure_price_kwh(df: pd.DataFrame) -> pd.Series:
    """
    Akzeptiert EUR/kWh oder EUR/MWh (konvertiert), indexiert nach Zeitstempel.
    
    Args:
        df: DataFrame mit Preis-Spalten
        
    Returns:
        pd.Series: Preis-Serie in EUR/kWh, indexiert nach Zeitstempel
        
    Raises:
        ValueError: Wenn keine gültigen Preis-Spalten gefunden werden
    """
    if "price_EUR_per_kWh" in df.columns:
        s = df["price_EUR_per_kWh"].astype(float)
    elif "price_EUR_per_MWh" in df.columns:
        s = (df["price_EUR_per_MWh"].astype(float) / 1000.0)
    else:
        raise ValueError("Preis-CSV muss price_EUR_per_kWh oder price_EUR_per_MWh enthalten.")
    
    s.index = pd.to_datetime(df["timestamp"])
    return s.sort_index()

def theoretical_revenue(E_kWh: float, DoD: float, eta_rt: float, 
                       delta_p_eur_per_kWh: float, cycles_per_day: float, 
                       days: int = 365) -> float:
    """
    Theoretische Arbitrage-Erlöse: E_use * Δp * cycles/day * days * η_rt
    
    Args:
        E_kWh: Batteriekapazität in kWh
        DoD: Depth of Discharge (0-1)
        eta_rt: Roundtrip-Effizienz (0-1)
        delta_p_eur_per_kWh: Preisunterschied in EUR/kWh
        cycles_per_day: Zyklen pro Tag
        days: Anzahl Tage (Standard: 365)
        
    Returns:
        float: Theoretische Jahreserlöse in EUR
    """
    E_use = E_kWh * DoD
    return float(E_use * delta_p_eur_per_kWh * cycles_per_day * days * eta_rt)

def spread_based_revenue(prices: pd.Series, E_kWh: float, DoD: float, 
                        P_kW: float, eta_rt: float, 
                        cycles_cap_per_day: float = 1.0) -> Tuple[float, pd.DataFrame]:
    """
    Upper-Bound Arbitrage basierend auf täglichen High-Low Spreads
    
    Args:
        prices: Preis-Serie in EUR/kWh
        E_kWh: Batteriekapazität in kWh
        DoD: Depth of Discharge (0-1)
        P_kW: Batterieleistung in kW
        eta_rt: Roundtrip-Effizienz (0-1)
        cycles_cap_per_day: Maximale Zyklen pro Tag
        
    Returns:
        Tuple[float, pd.DataFrame]: (Gesamterlös, Tagesdetails)
    """
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

def thresholds_based_revenue(prices: pd.Series, E_kWh: float, DoD: float, 
                           P_kW: float, eta_rt: float,
                           buy_thr: float, sell_thr: float, 
                           cycles_cap_per_day: float = 1.0) -> Tuple[float, pd.DataFrame]:
    """
    Schwellenwert-Modell: Laden wenn Preis <= buy_thr, Entladen wenn Preis >= sell_thr
    
    Args:
        prices: Preis-Serie in EUR/kWh
        E_kWh: Batteriekapazität in kWh
        DoD: Depth of Discharge (0-1)
        P_kW: Batterieleistung in kW
        eta_rt: Roundtrip-Effizienz (0-1)
        buy_thr: Kauf-Schwellenwert in EUR/kWh
        sell_thr: Verkaufs-Schwellenwert in EUR/kWh
        cycles_cap_per_day: Maximale Zyklen pro Tag
        
    Returns:
        Tuple[float, pd.DataFrame]: (Gesamterlös, Tagesdetails)
    """
    E_use = E_kWh * DoD
    cycles_power_cap = 12.0 * (P_kW / E_kWh) if E_kWh > 0 else 0.0
    cycles_per_day = min(cycles_cap_per_day, cycles_power_cap)
    
    if cycles_per_day <= 0:
        return 0.0, pd.DataFrame()

    if len(prices.index) < 2:
        raise ValueError("Mindestens zwei Preispunkte erforderlich.")
    
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
        
        if e_trade > 0 and len(buy) > 0 and len(sell) > 0:
            buy_avg = buy["price"].mean()
            sell_avg = sell["price"].mean()
            rev = e_trade * max(0.0, sell_avg - buy_avg) * eta_rt
        else:
            buy_avg = float("nan")
            sell_avg = float("nan")
            rev = 0.0
            
        out.append({
            "date": d, 
            "e_trade_kWh": e_trade, 
            "buy_avg": buy_avg, 
            "sell_avg": sell_avg, 
            "rev_day": rev
        })
    
    res = pd.DataFrame(out)
    total = float(res["rev_day"].sum())
    return total, res

def daily_cycles_power_cap(E_kWh: float, P_kW: float) -> float:
    """
    Berechnet die maximale Anzahl Zyklen pro Tag basierend auf Leistungsgrenzen
    
    Args:
        E_kWh: Batteriekapazität in kWh
        P_kW: Batterieleistung in kW
        
    Returns:
        float: Maximale Zyklen pro Tag
    """
    return 12.0 * (P_kW / E_kWh) if E_kWh > 0 else 0.0

