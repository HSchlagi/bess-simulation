"""
Intraday-Arbitrage Module für BESS-Simulation
============================================

Dieses Paket enthält Module für Intraday-Handel mit Batteriespeichern.
"""

from .arbitrage import (
    theoretical_revenue,
    spread_based_revenue,
    thresholds_based_revenue,
    daily_cycles_power_cap,
    _ensure_price_kwh
)

__all__ = [
    'theoretical_revenue',
    'spread_based_revenue', 
    'thresholds_based_revenue',
    'daily_cycles_power_cap',
    '_ensure_price_kwh'
]
