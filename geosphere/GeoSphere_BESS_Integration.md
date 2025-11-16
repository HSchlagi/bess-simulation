# GeoSphere-Windintegration für Phoenyra BESS Simulation
**Ziel:**  
Dieses Dokument beschreibt, wie du Windzeitreihen von **GeoSphere Austria (dataset.api.hub.geosphere.at)** automatisiert mit **Python** abrufst, in eine **15‑Minuten-Windleistungszeitreihe** umrechnest und diese als Input in deine **Phoenyra BESS Engine** integrierst.

Fokus:
- Python-Script als **Engine-Baustein**
- Saubere JSON/CSV-Schnittstelle
- Kompatibel mit **Cursor AI** (Code-Generierung & Refactoring)

---

## 1. Architektur-Übersicht

### 1.1 Komponenten

1. **GeoSphere Dataset API**
   - Quelle für Winddaten (z. B. 10‑Minuten-Mittelwerte)
   - Endpunkte-Typ: `station/historical/<resource_id>`
2. **Python-Modul `geosphere_wind_engine.py`**
   - Holt Daten von GeoSphere (HTTP GET)
   - Wandelt sie in eine **Hubhöhen-Windzeitreihe** um
   - Mapped Windgeschwindigkeit → Turbinen-Power-Curve
   - Berechnet 15‑Min-Energie [kWh]
   - Gibt Ergebnis als **DataFrame**, CSV oder JSON aus
3. **Phoenyra BESS Engine**
   - Nimmt PV, Last, Preise + **Windleistung** (kW/kWh)
   - Rechnet SOC, Arbitrage, Peak Shaving etc.
4. **n8n / Flask / Frontend**
   - Orchestriert den Aufruf der Engine
   - Visualisiert Ergebnisse, erzeugt Reports

### 1.2 Datenfluss (hochlevel)

1. Input (Config JSON):
   - GeoSphere Dataset (`resource_id`)
   - `station_id` (ZAMG/GeoSphere-Station)
   - Zeitraum (`start`, `end`)
   - Hubhöhe, Roughness-Exponent, Turbinenparameter
2. Python-Script:
   - GeoSphere API → Rohdaten (10 min oder 60 min)
   - Auf Hubhöhe hochrechnen
   - Power-Curve anwenden
   - Verluste berücksichtigen
   - Auf 15 min resamplen (falls nötig)
3. Output:
   - CSV/JSON mit Spalten: `timestamp`, `v_hub`, `P_wind_kW`, `E_wind_15min_kWh`
   - Übergabe an BESS Engine

---

## 2. GeoSphere Dataset API – Basics für das Script

### 2.1 Grundstruktur der URL

Schema:
```text
https://dataset.api.hub.geosphere.at/v1/station/historical/<resource_id>
    ?parameters=<PARAMS>
    &station_ids=<STATION_ID>
    &start=<ISO8601>
    &end=<ISO8601>
    &format=csv
```

Typische Beispiele für `<resource_id>` (station/historical):
- `tawes-v1-10min`   → TAWES-10‑Minuten-Daten (aktuellere Rohdaten)
- `klima-v2-10min`   → qualitätskontrollierte 10‑Minuten-Daten (Beispiel)
- `klima-v2-1h`      → Stundendaten

**Parameter (Beispiele, abhängig vom Datensatz):**
- `FF` → Windgeschwindigkeit Mittelwert [m/s]
- `DD` → Windrichtung [°]
- ggf. weitere Parameter (Temperatur etc.)

> Hinweis: Die exakten Kürzel stehen in der jeweiligen Dataset-Dokumentation (GeoSphere Data Hub).

---

## 3. Python-Engine – Struktur

Wir bauen ein eigenständiges Modul, z. B.:

```text
phoenyra_engine/
  geosphere_wind_engine.py
  config_example.json
  ...
```

### 3.1 Abhängigkeiten

Minimal:
- `requests`
- `pandas`
- `numpy`

Optional:
- `python-dateutil` für Datumsparsing

In `requirements.txt`:
```text
requests
pandas
numpy
python-dateutil
```

---

## 4. Konfigurationsdatei (JSON)

Für flexible Nutzung (versch. Standorte / Turbinen / Zeiträume) bietet sich eine JSON-Config an, z. B. `config_wind_geosphere.json`:

```json
{
  "geosphere": {
    "base_url": "https://dataset.api.hub.geosphere.at/v1",
    "resource_id": "tawes-v1-10min",
    "station_id": "11035",
    "parameters": ["FF"],
    "start": "2024-01-01T00:00:00Z",
    "end": "2024-12-31T23:50:00Z"
  },
  "wind_turbine": {
    "hub_height_m": 120.0,
    "alpha": 0.18,
    "rated_power_kw": 4200.0,
    "loss_factor_total": 0.15
  },
  "time_resolution": {
    "target_freq": "15min"
  },
  "output": {
    "csv_path": "wind_timeseries_15min.csv",
    "json_path": "wind_timeseries_15min.json"
  }
}
```

Erläuterung:
- `resource_id`: der Datensatz (z. B. 10‑Minuten-Stationen)
- `station_id`: GeoSphere-Station (z. B. Wien/Hohe Warte etc.)
- `parameters`: wir nutzen primär `FF` (Mittelwindgeschwindigkeit)
- `target_freq`: Ziel-Raster für BESS-Engine (`15min`)

---

## 5. Power-Curve-Definition

Wir definieren eine Power-Curve als einfache Liste von Stützpunkten (m/s → kW):

```python
POWER_CURVE = [
    (0.0, 0.0),
    (3.0, 0.0),
    (4.0, 150.0),
    (5.0, 300.0),
    (6.0, 600.0),
    (7.0, 1000.0),
    (8.0, 1600.0),
    (9.0, 2300.0),
    (10.0, 3000.0),
    (11.0, 3600.0),
    (12.0, 4000.0),
    (13.0, 4200.0),
    (14.0, 4200.0),
    (25.0, 0.0)
]
```

Interpolation erfolgt linear zwischen jeweils zwei Punkten.

**Hinweis:** In der Praxis solltest du hier die echte Hersteller-Power-Curve verwenden.

---

## 6. Python-Code: `geosphere_wind_engine.py` (Grundversion)

> Du kannst diesen Code 1:1 in Cursor AI einfügen und weiterentwickeln.

```python
import json
import io
from dataclasses import dataclass
from typing import List, Tuple, Dict, Any

import requests
import pandas as pd
import numpy as np


POWER_CURVE: List[Tuple[float, float]] = [
    (0.0, 0.0),
    (3.0, 0.0),
    (4.0, 150.0),
    (5.0, 300.0),
    (6.0, 600.0),
    (7.0, 1000.0),
    (8.0, 1600.0),
    (9.0, 2300.0),
    (10.0, 3000.0),
    (11.0, 3600.0),
    (12.0, 4000.0),
    (13.0, 4200.0),
    (14.0, 4200.0),
    (25.0, 0.0)
]


@dataclass
class GeoSphereConfig:
    base_url: str
    resource_id: str
    station_id: str
    parameters: List[str]
    start: str
    end: str


@dataclass
class WindTurbineConfig:
    hub_height_m: float
    alpha: float
    rated_power_kw: float
    loss_factor_total: float  # z.B. 0.15 für 15 % Verluste


@dataclass
class TimeResolutionConfig:
    target_freq: str  # z.B. "15min"


@dataclass
class OutputConfig:
    csv_path: str
    json_path: str


def load_config(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def interpolate_power(v: float, curve: List[Tuple[float, float]]) -> float:
    """Einfache lineare Interpolation der Power-Curve."""
    if v <= curve[0][0] or v >= curve[-1][0]:
        # Unterhalb min oder oberhalb max -> 0 kW (cut-in / cut-out simple)
        return 0.0

    for (v1, p1), (v2, p2) in zip(curve[:-1], curve[1:]):
        if v1 <= v <= v2:
            if v2 == v1:
                return p1
            f = (v - v1) / (v2 - v1)
            return p1 + f * (p2 - p1)

    # Fallback
    return 0.0


def fetch_geosphere_wind_df(cfg: GeoSphereConfig) -> pd.DataFrame:
    params_str = ",".join(cfg.parameters)
    url = (
        f"{cfg.base_url}/station/historical/{cfg.resource_id}"
        f"?parameters={params_str}"
        f"&station_ids={cfg.station_id}"
        f"&start={cfg.start}"
        f"&end={cfg.end}"
        f"&format=csv"
    )

    resp = requests.get(url, timeout=60)
    resp.raise_for_status()

    # CSV als Text → DataFrame
    csv_data = resp.text
    df = pd.read_csv(io.StringIO(csv_data))

    # Annahme: Es gibt eine Zeitspalte, z.B. "date" oder "datetime" oder ähnlich.
    # -> Hier musst du ggf. anhand des echten Dataset-Schemas anpassen!
    time_col_candidates = [c for c in df.columns if "time" in c.lower() or "date" in c.lower()]
    if not time_col_candidates:
        raise ValueError("Keine Zeitspalte gefunden. Bitte Dataset-Schema prüfen.")

    time_col = time_col_candidates[0]
    df[time_col] = pd.to_datetime(df[time_col])
    df = df.set_index(time_col).sort_index()

    return df


def compute_hub_height_wind(
    df: pd.DataFrame,
    v_col: str,
    hub_height_m: float,
    alpha: float,
    ref_height_m: float = 10.0
) -> pd.DataFrame:
    """Rechnet Windgeschwindigkeit von Referenzhöhe auf Hubhöhe hoch."""
    df = df.copy()
    df["v_hub"] = df[v_col] * (hub_height_m / ref_height_m) ** alpha
    return df


def apply_power_curve(df: pd.DataFrame, loss_factor_total: float) -> pd.DataFrame:
    df = df.copy()
    df["P_raw_kW"] = df["v_hub"].apply(lambda v: interpolate_power(v, POWER_CURVE))
    df["P_net_kW"] = df["P_raw_kW"] * (1.0 - loss_factor_total)
    return df


def resample_to_target(df: pd.DataFrame, target_freq: str) -> pd.DataFrame:
    """Resampling auf 15min o.ä., hier mit Mittelwert der Leistung."""
    # Wir gehen davon aus, dass P_net_kW ein zeitliches Mittel ist -> Mittelwert beim Resampling.
    df_res = df.resample(target_freq).mean()
    return df_res


def compute_energy_15min(df: pd.DataFrame, target_freq: str) -> pd.DataFrame:
    df = df.copy()
    # Dauer in Stunden aus target_freq ableiten, für "15min" = 0.25h
    # Vereinfachung: Pandas offset -> Minuten extrahieren
    if target_freq.endswith("min"):
        minutes = int(target_freq.replace("min", ""))
        hours = minutes / 60.0
    else:
        # fallback, z.B. "1H"
        if target_freq.upper().endswith("H"):
            hours = float(target_freq.upper().replace("H", ""))
        else:
            raise ValueError(f"Unsupported target_freq: {target_freq}")

    df["E_kWh"] = df["P_net_kW"] * hours
    return df


def run_wind_pipeline(config_path: str) -> pd.DataFrame:
    cfg_raw = load_config(config_path)

    geo_cfg = GeoSphereConfig(
        base_url=cfg_raw["geosphere"]["base_url"],
        resource_id=cfg_raw["geosphere"]["resource_id"],
        station_id=cfg_raw["geosphere"]["station_id"],
        parameters=cfg_raw["geosphere"]["parameters"],
        start=cfg_raw["geosphere"]["start"],
        end=cfg_raw["geosphere"]["end"]
    )

    wt_cfg = WindTurbineConfig(
        hub_height_m=cfg_raw["wind_turbine"]["hub_height_m"],
        alpha=cfg_raw["wind_turbine"]["alpha"],
        rated_power_kw=cfg_raw["wind_turbine"]["rated_power_kw"],
        loss_factor_total=cfg_raw["wind_turbine"]["loss_factor_total"]
    )

    tr_cfg = TimeResolutionConfig(
        target_freq=cfg_raw["time_resolution"]["target_freq"]
    )

    out_cfg = OutputConfig(
        csv_path=cfg_raw["output"]["csv_path"],
        json_path=cfg_raw["output"]["json_path"]
    )

    # 1) Daten von GeoSphere holen
    df_raw = fetch_geosphere_wind_df(geo_cfg)

    # Hier anpassen: Welche Spalte enthält die Windgeschwindigkeit (FF)?
    # Annahme: Spalte heißt exakt "FF"
    v_col = "FF"
    if v_col not in df_raw.columns:
        # Fallback: Spalte suchen, in der "FF" vorkommt
        matches = [c for c in df_raw.columns if "FF" in c]
        if not matches:
            raise ValueError("Spalte für Windgeschwindigkeit (FF) nicht gefunden.")
        v_col = matches[0]

    # 2) Auf Hubhöhe hochrechnen
    df_hub = compute_hub_height_wind(df_raw, v_col, wt_cfg.hub_height_m, wt_cfg.alpha)

    # 3) Power-Curve anwenden
    df_pow = apply_power_curve(df_hub, wt_cfg.loss_factor_total)

    # 4) Auf Zielzeitraster (z.B. 15min) resamplen
    df_res = resample_to_target(df_pow, tr_cfg.target_freq)

    # 5) Energie berechnen
    df_energy = compute_energy_15min(df_res, tr_cfg.target_freq)

    # 6) Optional: Clip auf Nennleistung (falls nötig)
    df_energy["P_net_kW"] = np.minimum(df_energy["P_net_kW"], wt_cfg.rated_power_kw)

    # 7) Ausgabe speichern
    df_out = df_energy[["v_hub", "P_net_kW", "E_kWh"]].copy()
    df_out.index.name = "timestamp"

    df_out.to_csv(out_cfg.csv_path)
    df_out.to_json(out_cfg.json_path, orient="table", date_format="iso")

    return df_out


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="GeoSphere Wind → 15min Timeseries for Phoenyra BESS")
    parser.add_argument(
        "--config",
        type=str,
        default="config_wind_geosphere.json",
        help="Pfad zur Konfigurationsdatei (JSON)"
    )
    args = parser.parse_args()

    df = run_wind_pipeline(args.config)
    print(df.head())
```

> **Wichtig:** Die echte Spaltenstruktur der GeoSphere-CSV musst du im Code ggf. anpassen (z. B. Name der Zeitspalte, Windspalte). Cursor AI kann dir beim Mapping helfen, sobald du ein Beispiel-CSV in das Projekt legst.

---

## 7. Schnittstelle zur Phoenyra BESS Engine

Die BESS Engine soll idealerweise **nicht** direkt GeoSphere kennen, sondern nur eine generische Zeitreihe „Windleistung“.

### 7.1 Output-Schema (CSV/JSON)

CSV (Beispiel `wind_timeseries_15min.csv`):

```text
timestamp,v_hub,P_net_kW,E_kWh
2024-01-01T00:00:00Z,7.23,1500.23,375.06
2024-01-01T00:15:00Z,6.95,1420.11,355.03
...
```

- `P_net_kW` → Windleistung im 15‑Minuten-Mittel (nach Verlusten)
- `E_kWh` → Energie im 15‑Minuten-Intervall
- `v_hub` → Windgeschwindigkeit auf Hubhöhe (für Analysen / QC)

### 7.2 Einbindung in BESS-Dispatch

In der BESS-Sim hast du typischerweise:

- `P_pv_kW(t)`
- `P_load_kW(t)`
- optional: `P_hydro_kW(t)`
- jetzt neu: `P_wind_kW(t)`

Nettoleistung am Netzanschlusspunkt ohne BESS:

```text
P_net_no_bess(t) = P_pv_kW(t) + P_wind_kW(t) + P_hydro_kW(t) - P_load_kW(t)
```

Der BESS-Algorithmus entscheidet:
- Überschuss → BESS lädt
- Defizit → BESS entlädt
- Optionale Marktlogik (Arbitrage nach Preiszeitreihe)

---

## 8. Anbindung an n8n (Option)

### 8.1 n8n-Workflow-Idee

1. **HTTP Request Node** (optional)
   - Prüft GeoSphere-Verfügbarkeit (Ping)
2. **Execute Command / Python Node**
   - Führt `python geosphere_wind_engine.py --config config_wind_geosphere.json` aus
3. **Read Binary File Node**
   - Liest `wind_timeseries_15min.csv`
4. **Spreadsheet File Node**
   - Wandelt CSV in Items
5. **Merge Node**
   - Verknüpft Wind-Items mit PV-/Last-/Preis-Items (auf Basis `timestamp`)
6. Weiter in deine **BESS-Engine** / Python-Dispatch-Berechnung.

> Du kannst die Python-Engine auch als HTTP-Service (FastAPI/Flask) deployen und aus n8n per HTTP aufrufen; das ist langfristig sauberer.

---

## 9. Typische Anpassungspunkte für Cursor AI

Wenn du dieses Dokument in Cursor als Referenz benutzt, kannst du die KI gezielt folgende Aufgaben erledigen lassen:

1. **Dataset-Schema-Mapping:**
   - „Lese diese GeoSphere-CSV und passe `fetch_geosphere_wind_df` so an, dass Zeit- und Windspalte korrekt erkannt werden.“
2. **Power-Curve-Austausch:**
   - „Ersetze `POWER_CURVE` durch die echte Power-Curve aus dieser Hersteller-CSV.“
3. **Fehlerbehandlung erweitern:**
   - Timeout-Retry, Logging, Rate-Limit-Handling.
4. **FastAPI-Wrapper:**
   - „Baue eine FastAPI, die `run_wind_pipeline` per POST-Request (JSON-Config) anstößt und das Ergebnis als JSON zurückgibt.“
5. **Integration in bestehenden Phoenyra BESS-Kern:**
   - „Lies die BESS-Engine-Datei und integriere `P_wind_kW` als zusätzlichen Input-Stream.“

---

## 10. Nächste Ausbaustufen

- Mehrere Stationen (z. B. Mittelwert oder best-case / worst-case Szenarien)
- Kombination aus **Stationsdaten + globalem Windatlas** für Plausibilitätscheck
- Einbau eines **Unsicherheitsmodells** (z. B. ±10 % Windgeschwindigkeit → Sensitivität Ertrag)
- Spezielle Szenarien:
  - „Sturmjahr“ vs. „Flautejahr“
  - „2030‑Klima­szenario“ mit veränderten Windmustern

---

Dieses Dokument ist so aufgebaut, dass du es in **Cursor AI** als zentrale Referenz für die *GeoSphere‑Wind → BESS Engine*-Integration nutzen kannst.  
Du kannst einzelne Codeblöcke direkt herausziehen, refactoren und mit deinen bestehenden Phoenyra‑Modulen verbinden.
