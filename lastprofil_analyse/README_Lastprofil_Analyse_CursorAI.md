
# Lastprofil-Analyse Paket für Phoenyra BESS Studio & Cursor AI

Dieses Paket enthält ein **Python-Modul + FastAPI-API** sowie ein **Chart.js-Frontend-Beispiel**,
um elektrische Lastprofile (z. B. für BESS-Simulationen) auszuwerten.

Fokus:
- Einfache Integration in deine Phoenyra / BESS-Simulationssoftware
- Direkte Verwendung mit **Cursor AI** für Erweiterungen
- Saubere Trennung: Backend-Analyse (Python/pandas) + Frontend (Chart.js)

---

## 1. Projektstruktur

```text
lastprofil_analyse/
  main.py                          # FastAPI-App (API)
  requirements.txt
  analysis/
    __init__.py
    loader.py                      # CSV → pandas.DataFrame
    kpi.py                         # Kennzahlen + Lastdauerlinie
  frontend_example_chartjs.html    # Minimal-Frontend mit File-Upload + Chart.js
```

Du kannst diesen Ordner direkt als Projekt in Cursor öffnen.

---

## 2. Installation (lokal)

```bash
cd lastprofil_analyse

# Virtualenv (optional, aber empfohlen)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Abhängigkeiten installieren
pip install -r requirements.txt
```

---

## 3. Start der FastAPI-API

```bash
uvicorn main:app --reload
```

Danach stehen dir zur Verfügung:

- Swagger-UI: `http://localhost:8000/docs`
- Health-Check: `http://localhost:8000/health`

---

## 4. Endpunkt: `/analyze`

**Methode:** `POST`  
**Pfad:** `/analyze`  
**Body:** `multipart/form-data` mit:

- `file`: CSV-Datei mit Lastprofil
- `ts_col`: Name der Zeitspalte (Default: `timestamp`)
- `power_col`: Name der Leistungsspalte (Default: `P_total`)
- `freq`: Zielauflösung, z. B. `15min` oder `60min`
- `sep`: CSV-Trennzeichen (Default: `;`)
- `decimal`: Dezimaltrennzeichen (Default: `,`)
- `max_ldc_points`: maximale Anzahl Punkte in der Lastdauerlinie für das Frontend (Default: `500`)

**Erwartetes CSV-Beispiel:**

```csv
timestamp;P_total
2024-01-01 00:00;12,3
2024-01-01 00:15;11,8
2024-01-01 00:30;10,5
...
```

**Antwort (JSON):**

```jsonc
{
  "kpis": {
    "E_jahr_kWh": 123456.0,
    "P_max_kW": 250.5,
    "P_mean_kW": 45.3,
    "Lastfaktor": 0.18,
    "Benutzungsdauer_h": 492.0
  },
  "ldc": [
    { "hours": 0.25, "P_kW": 250.5 },
    { "hours": 0.50, "P_kW": 247.8 },
    ...
  ]
}
```

---

## 5. Python-Analyse-Layer

### 5.1. `analysis/loader.py`

- Lädt CSV-Rohbytes (z. B. von `UploadFile`)
- Erwartet eine Zeitspalte (`ts_col`) und eine Leistungsspalte (`power_col`)
- Setzt den Zeitindex, sortiert und resampled auf `freq`
- Normiert die Leistungsspalte auf `P` [kW] und klippt negative Werte

Du kannst diese Funktion auch direkt in anderen Modulen nutzen:

```python
from analysis.loader import load_lastprofil_from_bytes

with open("lastprofil.csv", "rb") as f:
    df = load_lastprofil_from_bytes(f.read(), ts_col="timestamp", power_col="P_total")
```

### 5.2. `analysis/kpi.py`

- `calc_basic_kpis(df)`:
  - Jahresenergie `E_jahr_kWh`
  - Maximale Leistung `P_max_kW`
  - Mittlere Leistung `P_mean_kW`
  - Lastfaktor
  - Benutzungsdauer in Stunden

- `load_duration_curve(df)`:
  - Erzeugt eine Lastdauerlinie (Load Duration Curve):
    - sortierte Leistungen absteigend
    - zugehörige Stunden (x-Achse) als kumulierte Zeit

---

## 6. Frontend: `frontend_example_chartjs.html`

Diese Datei ist ein **Minimal-Beispiel**, wie du:

1. Eine CSV-Datei per File-Upload auswählst
2. Die API `/analyze` auf `http://localhost:8000` aufrufst
3. KPIs als Text + Balkenchart (Chart.js) darstellst
4. Die Lastdauerlinie als Liniendiagramm (Chart.js) renderst

### Verwendung

- Stelle sicher, dass die API läuft (`uvicorn main:app --reload`)
- Öffne `frontend_example_chartjs.html` lokal im Browser
- Wähle ein CSV-Lastprofil aus
- Ergebnis: KPIs + Lastdauerlinie werden direkt visualisiert

Du kannst dieses HTML:

- in dein eigenes Frontend übernehmen
- in ein Flask/Jinja-Template integrieren
- oder als Referenz für eine React/Next.js-Implementierung verwenden

---

## 7. Integration in deine BESS-Simulationssoftware

Typische Integrationspfade:

### 7.1. Internes EMS / Phoenyra Backend

- FastAPI-Endpunkt `/analyze` direkt in dein EMS-Backend übernehmen
- Weitere Endpunkte ergänzen, z. B.:
  - `/analyze-with-pv`
  - `/bess-sizing-from-profile`
  - `/peak-shaving-simulation`

### 7.2. n8n-Workflow

- HTTP Request Node → `POST /analyze` mit CSV aus Datei/Storage
- Response-KPIs in DB schreiben (PostgreSQL/ClickHouse)
- Report-Generierung (PDF, Excel) automatisieren

### 7.3. Cursor AI Erweiterung

Beispiel-Prompt für Cursor:

> *„Erweitere `main.py` um einen Endpunkt `/bess-sizing`, der aus dem Lastprofil und einer gegebenen maximalen Netzanschlussleistung den benötigten BESS-Energieinhalt [kWh] und die maximale Lade-/Entladeleistung [kW] berechnet. Verwende dazu die bestehende Lastdauerlinie aus `analysis.kpi.load_duration_curve`.“*

Cursor kann auf dieser Basis:

- zusätzliche Analysefunktionen einbauen
- neue API-Endpunkte erzeugen
- Tests generieren

---

## 8. Nächste sinnvolle Erweiterungen

Vorschläge, die du mit Cursor AI direkt auf diesem Paket aufsetzen kannst:

1. **Peak-Shaving-Simulation**
   - Parameter: `P_limit`, `bess_power_kW`, `bess_capacity_kWh`
   - Ausgabe: Reduzierte Spitzenleistung, BESS-Auslastung, Zyklenzahl

2. **PV+Lastprofil-Kombination**
   - Zweite Zeitreihe (PV), Bildung von Residuallast
   - KPIs vor/nach PV/BESS-Einsatz

3. **Tarif- und Kostenanalyse**
   - Hinterlegung von Energie- und Leistungspreisen
   - Berechnung von Jahreskosten mit/ohne BESS/Peak-Shaving

4. **Export-Funktionen**
   - Export von KPIs und LDC als CSV/Excel
   - PDF-Report mit Diagrammen für Projekt-Dokumentationen

---

## 9. Kurzfassung: Wie du startest

1. Zip entpacken → Projekt `lastprofil_analyse` in Cursor öffnen  
2. `requirements.txt` installieren  
3. `uvicorn main:app --reload` starten  
4. `frontend_example_chartjs.html` im Browser öffnen  
5. Lastprofil-CSV hochladen → KPIs & Lastdauerlinie direkt sehen  
6. Danach mit Cursor AI weitere Endpunkte und BESS-Funktionen ergänzen

Viel Spaß beim Integrieren in Phoenyra / BESS Studio!
