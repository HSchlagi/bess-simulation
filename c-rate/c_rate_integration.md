# Cursor-AI Prompt: C-Rate Integration ins BESS-Programm

## Ziel
Baue eine C‑Rate‑Integration in das bestehende BESS‑Programm.

## Anforderungen
1. **Definitionen**
   - `C_rate` [1/h] = maximaler (Dis‑/Charge‑)Strom relativ zur Nennkapazität.
   - Nennenergie `E_nom_kWh` [kWh] → maximale Leistung:
     - `P_dis_max_kW = C_dis_rate * E_nom_kWh`
     - `P_chg_max_kW = C_chg_rate * E_nom_kWh`
   - Optional: SoC‑ und temperaturabhängige Derating‑Faktoren.

2. **Schnittstellen**
   - Neues Modul `bess/crate.py` mit:
     - `compute_power_bounds(...)`
     - `apply_bounds(...)`
     - `derate_factors(...)`
   - Anpassung `bess/battery.py`:
     - nutzt `compute_power_bounds` in `request_power(...)`
   - Konfigurationsschema `config/bess.yaml`

3. **Formeln (Zeitschritt dt)**
   - `P_chg_max = C_chg_rate * E_nom * f_chg(SoC,temp)`
   - `P_dis_max = C_dis_rate * E_nom * f_dis(SoC,temp)`
   - SoC‑Update:
     - Laden: `SoC_{t+1} = SoC_t + (P_set * eta_chg * dt_h)/E_nom`
     - Entladen: `SoC_{t+1} = SoC_t - (P_set/eta_dis * dt_h)/E_nom`

4. **Tests**
   - 1C @ 8 MWh → 8 MW Dis‑Limit, 0.5C Charge → 4 MW.
   - SoC‑Derating, Temperatur‑Derating, SoC‑Update.

5. **Optimierer‑Integration**
   - Für jeden Zeitschritt Bounds: `P_chg_max_t`, `P_dis_max_t`.
   - Nebenbedingungen in LP/QP.

## Lieferobjekte
- Dateien: `bess/crate.py`, `bess/battery.py`, `config/bess.yaml`, `tests/test_crate.py`
- Sauberer, typisierter Python‑Code.
- Keine externen Abhängigkeiten außer `numpy`/`pydantic` (optional).
