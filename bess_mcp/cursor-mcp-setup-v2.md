# cursor-mcp-setup-v2.md

**Neu**: `sim_run_dispatch` ist an eure echte Simulation ankoppelbar (ENV).

## Beispiele für Cursor-Prompts
- „Hole `prices_get_awattar` für `{{TODAY}}` und speichere die Kurve in die DB `spot`.“
- „Rufe `read_pv_load` für 2025-05-01 auf und berechne Eigenverbrauch/Autarkie.“
- „Starte `sim_run_dispatch` mit `{ "capacity_mwh": 0.2, "cycles_limit_per_day": 1.1, "price_spread_eur_mwh": 95 }`
  und gib KPIs als Tabelle aus. Entscheide danach einen Modus und sende `bess_set_mode`.“

## Dispatch anbinden
- Code in `app/` legen und `.env` (Module/Func) setzen. Kein weiterer Glue-Code nötig.
