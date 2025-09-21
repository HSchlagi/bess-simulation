# BESS MCP Server — v2 (Dispatch-Adapter + aWATTar + PV/Load)

Diese Version bringt:
- **Pluggable Dispatch** via ENV (`DISPATCH_MODULE`/`DISPATCH_FUNC`)
- Tool **`prices_get_awattar(day, country)`** (AT/DE)
- Tool **`read_pv_load(day)`** (erwartet `pv_load`-Tabelle)
- Robustere Docker/ENV Defaults

## Einhängen eurer echten Simulation
1. Lege eine Python-Funktion an, z. B. in `app/my_dispatch.py`:
   ```py
   def run_dispatch(params: dict) -> dict:
       # ... deine Simulation ...
       return {"profit_eur": 123.4, "cycles_per_day": 0.9, "autarky_pct": 63.2}
   ```
2. Setze in `.env`:
   ```
   DISPATCH_MODULE=app.my_dispatch
   DISPATCH_FUNC=run_dispatch
   ```
3. Server neu starten. `sim_run_dispatch` ruft jetzt deine Funktion auf.

## Erwartete Tabellen
- `spot(ts TEXT ISO, price_eur_mwh REAL)`
- `metrics(ts TEXT, key TEXT, value REAL)`  (SOC)
- `pv_load(ts TEXT ISO, pv_kw REAL, load_kw REAL)`

## aWATTar
- ENV `AWATTAR_BASE_URL` wird für AT/DE automatisch gesetzt, oder direkt überschreiben.
- Hinweis: Die API liefert i. d. R. stündliche Daten in 15-min Slots. Prüfe Umrechnungsfaktor.

## Start
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python mcp/server.py
```
In Cursor → **Settings → MCP** als **Command** registrieren (`python mcp/server.py`).

## Sicherheit
- stdio bevorzugen; HTTP nur mit Auth/Firewall. Secrets via ENV.
