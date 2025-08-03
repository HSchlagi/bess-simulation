
# 💡 Projektstruktur für Cursor AI: Simulation & Analyse von BESS Use Cases (Hinterstoder)

Dieses Dokument enthält eine Struktur zur Entwicklung eines Simulationsprogramms für die Auswertung von Erlöspotenzialen und Kennzahlen für verschiedene BESS-Szenarien (Use Case 1–x) aus der Präsentation der CyberGrid GmbH.

---

## 🎯 Ziel
Cursor AI soll den nachfolgenden Programmaufbau analysieren und erweitern, um eine praxisnahe, interaktive Simulationsumgebung zur Verfügung zu stellen. Insbesondere soll das System in der Lage sein, Erlöse und Kosten auf Monats- und Jahresbasis darzustellen, Zyklen zu berechnen und zentrale KPIs (Erlöse/MW, €/MWh, Verhältnis) zu vergleichen.

---

## 📦 Projektstruktur

```
bess_simulation/
├── data/
│   └── prices_intraday.csv          # 15min Preisdaten
│   └── lastprofil_uc1.csv           # Lastdaten Use Case 1
│   └── lastprofil_uc2.csv           # Lastdaten Use Case 2
│   └── lastprofil_uc3.csv           # Lastdaten Use Case 3
│
├── models/
│   └── simulation.py                # Datenklasse für Simulation (UC1–UC3)
│   └── market_logic.py              # Regelreserve-, Intraday-Logik
│   └── tariffs.py                   # Netz- & Förderentgelte
│
├── analysis/
│   └── kpi_calculator.py            # Jahresbilanz, Energieneutralität, €/MW/a
│   └── comparison.py                # Use Case 1-3 im Vergleich
│
├── visualizations/
│   └── bar_charts.py                # Monatsbalken Erlöse/Kosten/Zyklen
│   └── sankey_energy_flow.py        # Energieflussdiagramm
│
├── output/
│   └── results_uc1_2024.json
│   └── results_uc2_2024.json
│   └── dashboard.html
│
├── main.py                          # Steuerung der Simulation über CLI/GUI
└── README.md
```

---

## 🧠 Aufgaben für Cursor AI

1. **Analyse der Datenbasis:**
   - Wie können die verschiedenen Erlösarten SRL/E±, SRE±, PRR etc. modelliert werden?
   - Wie lassen sich Zyklenzahlen dynamisch pro Monat berechnen?

2. **Klassendesign:**
   - Erstelle Klassen `BESSUseCase`, `SimulationResult`, `MarketRevenue` und `CostStructure`
   - Jede Klasse soll Methoden zur Berechnung ihrer Kennzahlen besitzen (z. B. `calc_erloes`, `calc_kosten`, `calc_ratio`)

3. **Visualisierung:**
   - Baue Funktionen zur Darstellung der Charts wie in der Präsentation:
     - Monatsbalken Bruttoerlöse
     - Nettoerlöse + Gebühren
     - Vergleich 10Y Ø und Referenzjahr

4. **KPI-Vergleichsfunktion:**
   - Implementiere eine Vergleichsmatrix zwischen Use Case 1–3
   - Nutze `pandas` zur Darstellung als Tabelle und Ausgabe als CSV & HTML

5. **Optional:**
   - Füge Exportfunktion als PDF hinzu
   - Erstelle ein Webfrontend mit Flask oder Streamlit zur Parametereingabe

---

## 📄 Zusätzliche Dokumentation
Die bereitgestellten Grafiken (siehe Upload) visualisieren:
- Monatliche Erlösarten
- Gebührenstruktur nach Kategorie
- Zyklenzahlen pro Monat
- Jahresverläufe
- Summenvergleich (10 Jahre vs. Referenz)

Nutze diese zur Validierung der Simulation.

---

Bitte Cursor AI: Generiere den Startcode für `simulation.py`, `kpi_calculator.py` und `main.py`.
