# AT Intraday Auctions (CSV) + APG Regelenergie Loader

- Parses **EPEX SPOT IDA1/IDA2/IDA3** CSVs (licensed data) into a single tidy series.
- Parses **APG** aFRR/FCR/mFRR CSVs (capacity and activation).
- Computes quick KPIs and coarse revenue heuristics; replace with your optimizer.

## Example
```python
from bess_market_intel_at import ATMarketIntegrator, BESSSpec
at = ATMarketIntegrator('AT')
ida = at.load_ida_csvs(['IDA1_AT.csv','IDA2_AT.csv','IDA3_AT.csv'])
ida_q = at.ida_quarter_series(ida)
cap = at.load_apg_capacity('APG_capacity.csv', product_filter='afrr')
act = at.load_apg_activation('APG_activation.csv', product_filter='afrr')
print(at.kpis(ida_series=ida_q, cap_series=cap, act_series=act, spec=BESSSpec(2.0, 8.0)))

