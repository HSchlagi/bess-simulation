
# AT Secondary Market Module (APG primary)

This folder contains `bess_markets_at.py` with:
- APG CSV parsers for aFRR capacity and activation prices
- ENTSO-E balancing wrapper (uses your existing client via callback)
- Revenue calculators for capacity-only and combined capacity+activation
- A default scenario for 2 MW / 8 MWh

## How to use

1. Export aFRR results from https://markt.apg.at (CSV).
2. In your sim:
   ```python
   from bess_markets_at import (
       load_apg_afrr_capacity_prices, load_apg_afrr_activation_prices,
       combined_secondary_market_revenue, BESSSpec, MarketParams
   )
   cap = load_apg_afrr_capacity_prices('apg_afrr_capacity.csv')
   # Collapse to a single Series of EUR/MW per block (choose 'price_eur_per_mw')
   cap_series = cap.set_index('start')['price_eur_per_mw']

   spec = BESSSpec(power_mw=2.0, energy_mwh=8.0)
   params = MarketParams(fcr_price_per_mw_year=70000, afrr_price_per_mw_year=100000)
   rev = combined_secondary_market_revenue(spec, capacity_series_eur_per_mw=cap_series, defaults=params)
   print(rev)
   ```
3. For activation prices (if available), also parse the CSV and pass `activation_prices_eur_per_mwh`:
   ```python
   act = load_apg_afrr_activation_prices('apg_afrr_activation.csv')
   act_series = act.set_index('start')['price_eur_per_mwh']
   rev2 = combined_secondary_market_revenue(spec, cap_series, act_series, activation_share=0.05)
   ```

## ENTSO-E usage
- Provide your entsoe client callback, e.g.:
  ```python
  def cb_fetch(**kw):
      # return a pandas DataFrame with columns ['start','end','product','price','uom']
      return my_entsoe_client.get_balancing_prices(**kw)

  df = load_entsoe_balancing(cb_fetch, zone='AT', product='aFRR_up',
                             start='2024-01-01', end='2024-12-31')
  ```

## Notes
- Column names in APG CSVs vary. The loader tries to auto-map common names; tweak if needed.
- Availability & degradation multipliers reduce revenue to reflect downtime and aging.
- Set `intraday_bonus_eur_year` to 0 if you want pure secondary market revenue.
