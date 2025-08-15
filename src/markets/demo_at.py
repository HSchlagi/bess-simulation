### **3 — `demo_intelligent_at.py`**
```python
import pandas as pd
from bess_market_intel_at import ATMarketIntegrator, BESSSpec

ida_files = []  # Fill with your IDA CSV file paths
cap_file = None
act_file = None

at = ATMarketIntegrator('AT')
ida = at.load_ida_csvs(ida_files) if ida_files else pd.DataFrame()
ida_q = at.ida_quarter_series(ida) if not ida.empty else pd.Series(dtype=float)
cap = at.load_apg_capacity(cap_file) if cap_file else pd.Series(dtype=float)
act = at.load_apg_activation(act_file) if act_file else pd.Series(dtype=float)

print(at.kpis(ida_series=ida_q, cap_series=cap, act_series=act, spec=BESSSpec(2.0, 8.0)))