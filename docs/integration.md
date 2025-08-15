
# BESS Intraday-Arbitrage – Integrationspaket

## Dateien
- `src/intraday_arbitrage.py` – Modul (3 Modi: theoretical, spread, threshold)
- `snippets/economics_patch.py` – Funktion `intraday_revenue(...)` zum Einfügen in `economics.py`
- `snippets/optimize_patch.txt` – Codezeilen für `optimize.py` (Annual Savings erweitern)
- `config/intraday_config_block.yaml` – YAML-Block für `config.yaml`
- `data/prices_intraday.csv` – Beispielpreise (EUR/MWh, stündlich)

## Schritt-für-Schritt
1. Kopiere `src/intraday_arbitrage.py` in dein Repo unter `src/`.
2. Öffne `economics.py` und füge die Funktion aus `snippets/economics_patch.py` hinzu (Imports beachten).
3. Öffne `optimize.py` und erweitere den Sizing-Loop gemäß `snippets/optimize_patch.txt`.
4. Merge den YAML-Block aus `config/intraday_config_block.yaml` in deine `config.yaml`.
5. Lege deine echten Intraday-Preise in `data/prices_intraday.csv` ab (Spalten: `timestamp`, `price_EUR_per_MWh` oder `price_EUR_per_kWh`).
6. Simulation starten. In den Ergebnissen sollte der Arbitrage-Erlös als Teil von `annual_savings` auftauchen.

## Acceptance Tests
- Ohne Preise/Mode=`theoretical`: Summary/NPV ändert sich, wenn `delta_p` oder `cycles_per_day` geändert wird.
- Mit Preisen/Mode=`threshold`: Tageserlöse ≠ 0 an volatileren Tagen; jährliche Savings reagieren auf Schwellen.
- `12*P/E` ist obere Zyklusgrenze/Tag (mit E=8000, P=2000 → 3).

## Hinweise
- `spread` ist Upper-Bound; `threshold` ist konservativer/realistischer.
- Für MILP-basierte Optimierung später gleiche IO-Schnittstellen beibehalten.
