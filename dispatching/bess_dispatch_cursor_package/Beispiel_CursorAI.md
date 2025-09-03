# BESS-Dispatch – Cursor AI Integration (inkl. Redispatch)

Dieses Paket liefert:
- `bess_dispatch_tool.py` – Excel laden, SoC simulieren, Charts/CSVs exportieren, **15‑Minuten & Mehrtägig**, **Redispatch**.
- `build_excel_from_csv.py` – Erzeugt eine komplette Excel-Arbeitsmappe direkt aus CSV (Basisdaten, Parameter, Simulation, Abrechnung, KPIs, Charts).
- `requirements.txt` – Minimal benötigte Bibliotheken.

## 1) Installation
```bash
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 2) Standardlauf (stündlich)
```bash
python bess_dispatch_tool.py \
  --excel ./BESS_Dispatch_Beispiel.xlsx \
  --outdir ./out \
  --recompute
```

## 3) 15‑Minuten & Mehrtägig
```bash
python bess_dispatch_tool.py \
  --excel ./BESS_Dispatch_Beispiel.xlsx \
  --outdir ./out \
  --recompute \
  --freq_minutes 15 \
  --start "2025-01-01 00:00" \
  --days 3
```

## 4) Redispatch einspielen
**CSV-Felder (flexibel):** `start` (timestamp/hour/slot), `duration_slots` ODER `end`, `power_mw`, `mode` (`delta`|`absolute`), `compensation_eur_mwh` (optional), `reason` (optional).

Beispiel-CSV:
```csv
start,duration_slots,power_mw,mode,compensation_eur_mwh,reason
2025-01-01 18:00,4,1.5,delta,110,Engpass-Sued
2025-01-01 22:00,2,-1.0,delta,90,Engpass-Nord
```

**Ausführen:**
```bash
python bess_dispatch_tool.py \
  --excel ./BESS_Dispatch_Beispiel.xlsx \
  --outdir ./out \
  --recompute \
  --rd_csv ./redispatch_calls.csv \
  --write_excel
```
Outputs:
- `redispatch_calls_normalized.csv`
- `abrechnung_redispatch.csv` (ΔE_out, ΔE_in, ΔCashflow, Compensation, kumuliert)
- `Redispatch_Kumulierte_DeltaCF.png`
- Excel-Sheets **Redispatch_Calls** & **Abrechnung_Redispatch** (bei `--write_excel`)

## 5) CSV → Excel (ohne Vorlage)
```bash
python build_excel_from_csv.py \
  --csv ./input.csv \
  --excel ./BESS_Dispatch_Beispiel_neu.xlsx \
  --cap 8 --pmax_dis 2 --pmax_cha 2 \
  --soc_init 50 --soc_min 5 --soc_max 95 \
  --eta_dis 0.92 --eta_cha 0.92
```

## 6) Datenmodell (Kurzüberblick)
- **Basis**: `hour` oder `timestamp`, `price_eur_mwh`, `dispatch_mw` (+: Entladen, −: Laden)
- **Simulation**: `Dispatch_Feasible_[MW]`, `E_out_to_Grid_[MWh]`, `E_in_from_Grid_[MWh]`, `SoC_[%]`, `Check`
- **Abrechnung**: Einnahmen/Kosten/Cashflow, kumuliert
- **Redispatch**: Δ-Tabellen vs. Baseline + Compensation

## 7) Troubleshooting
- Spaltennamen prüfen (siehe oben). 
- Bei 15‑min Raster unbedingt `--freq_minutes 15` setzen (Δt wird automatisch auf 0.25 h angepasst).
- Redispatch-Calls sollten die Slot‑Dauer widerspiegeln (bei 15‑min = 0.25 h pro Slot).


---

## 10) Länderspezifische Profile (DE/AT)

`--country DE|AT` setzt sinnvolle Defaults:

- **DE (Deutschland, Redispatch 2.0):**
  - `--freq_minutes` **15** (Viertelstunde)
  - `--rd_comp_mode` **market_price** → Entschädigung anhand Marktpreis je Slot (vereinfachter Marktwert-Ansatz)

- **AT (Österreich, APG Redispatch/Countertrading):**
  - `--freq_minutes` **15**
  - `--rd_comp_mode` **flat_csv** → Entschädigung muss als `compensation_eur_mwh` je Slot im RD-CSV kommen

**Alternative Modi:**
- `flat_csv` – nimm `compensation_eur_mwh` aus RD-CSV.
- `market_price` – nutze Basis-Preiszeitreihe je Slot als Referenzpreis.
- `premium` – Basispreis + `--rd_premium` (EUR/MWh), z. B. um Zuschläge abzubilden.

**Beispiele:**  
Deutschland (vereinfachte Marktwert-Entschädigung):
```bash
python bess_dispatch_tool.py --excel ./BESS_Dispatch_Beispiel.xlsx --outdir ./out \
  --recompute --country DE --rd_csv ./redispatch_calls_de.csv --write_excel
```

Österreich (APG – kompensationspreis je Slot vorgeben):
```bash
python bess_dispatch_tool.py --excel ./BESS_Dispatch_Beispiel.xlsx --outdir ./out \
  --recompute --country AT --rd_csv ./redispatch_calls_at.csv --write_excel
```
