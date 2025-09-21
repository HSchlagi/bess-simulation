"""Example dispatch adapter.

Replace run_dispatch() with your real engine. The MCP server will import this
function based on ENV: DISPATCH_MODULE / DISPATCH_FUNC.
"""
from typing import Dict, Any

def run_dispatch(params: Dict[str, Any]) -> Dict[str, Any]:
    # Example KPIs based on dummy params
    price_spread = params.get("price_spread_eur_mwh", 80)
    cycles_limit = params.get("cycles_limit_per_day", 1.0)
    capacity_mwh = params.get("capacity_mwh", 0.1)

    profit = 0.35 * price_spread * cycles_limit * capacity_mwh
    return {
        "profit_eur": round(profit, 2),
        "cycles_per_day": cycles_limit,
        "notes": "Demo adapter — replace with real dispatch engine"
    }
