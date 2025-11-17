# BESS-Simulation – Erweiterte Roadmap (2025)
Hierarchische und priorisierte Übersicht aller neuen Punkte für die Erweiterung eures Phoenyra BESS Studio Systems.

---

## 1. **Top-Priorität – sofort integrieren**
Diese Punkte bringen den größten wirtschaftlichen Nutzen und verbessern die Realitätsnähe eurer Simulation massiv.

### 1.1 Regulierungs- & Netzrestriktionen (hoher wirtschaftlicher Einfluss)
**Warum wichtig:** Neue nationale & EU-weite Grid-Regeln können die Erlöse eines Speichers um bis zu 40–50 % beeinflussen.  
**Was simulieren:**
- Ramp‑Rate Limits (z.B. max. 10 % pro Minute)
- Exportlimits je nach Netzebene (NE5/NE6/NE7)
- 100‑h‑Regel (EEG / DE) → stundenweise Einspeisebegrenzung
- Begrenzung Einspeiseleistung am Netzanschlusspunkt
- Hüllkurvenregelungen (APG, ENTSO‑E Vorgaben)

**Excel/Algorithmus:**
- Neue Parameterfelder: `Max_Discharge_kW`, `Max_Charge_kW`, `RampRate_%`, `ExportLimit_kW`
- Bei jeder 15-Minuten-Periode: Leistung = MIN(geplanter Wert, Restriktionen)
- Kennzahlen:
  - „Erlösverlust durch Netzrestriktionen“
  - „Theoretischer vs. realer Arbitragegewinn“

---

## 2. **Essentiell – innerhalb der nächsten Wochen**
Diese Features verbessern die technische Tiefe und die Ergebnisqualität erheblich.

### 2.1 Batterie-Degradation (Kapazitätsverlust über Zeit)
**Warum wichtig:** Realistische Langzeit-Wirtschaftlichkeit.
**Zu simulieren:**
- Cycle Count (Full Cycle Equivalent)
- DoD-Abhängige Alterung
- Temperaturfaktor (optional)
- Kapazitätsverlust pro Jahr
- Lebensdauer bis 80 % SoH

**Excel:**
- Tabelle „Degradation“:  
  `Cycle_Number`, `DoD`, `Efficiency`, `Cap_Loss_kWh`
- Formel: `Cap_t+1 = Cap_t - f(Cycles, DoD, Temp)`

### 2.2 Second-Life-Batterien (Economy-Szenario)
**Warum wichtig:** Niedrige CAPEX, aber höhere Degradation.
**Zu simulieren:**
- Startkapazität: 70–85 %
- Lebensdauer 3–7 Jahre
- Kostenvorteil 40–60 %

**Dashboard-Kennzahlen:**
- CAPEX/kWh Vergleich
- LCOE BESS Vergleich
- TCO über 10–15 Jahre

---

## 3. **Wirtschaftlich sehr stark – Integration empfohlen**
Verbessert Erträge und Optimierungsfunktionen im Handel & im Zyklenbetrieb.

### 3.1 Co‑Location PV + BESS
**Warum wichtig:** Reduziert Netzkosten & erhöht Eigenverbrauch/Export.
**Simulation:**
- Gemeinsamer Netzverknüpfungspunkt
- Kürzungs-Vermeidung bei PV („curtailment avoidance“)
- Peak-Shaving pv‑geführt

**Excel:**
- „Curtailment‑Losses“ berechnen
- Kennzahl: „PV‑Mehrproduktion durch BESS (%/kWh)“

### 3.2 Optimierte Regelstrategien (PSO, Smart Dispatch)
**Warum wichtig:** +5–15 % Mehrertrag möglich.
**Strategien:**
- Particle Swarm Optimization
- Cluster‑Based Dispatch
- Multi-Objective Optimierung (Ertrag + Degradation minimieren)
- Zyklenoptimierung, um Battery Health zu schützen

**Implementierung (Pseudo‑Code):**
```
price = Price[t]
soc = SOC[t]

IF price < low_threshold:
    charge()
ELSE IF price > high_threshold:
    discharge()
ELSE:
    idle()
```

Erweitert zu:
```
Optimize:
  maximize(Revenue - DegradationPenalty)
  subject to: SOCmin < SOC < SOCmax
```

---

## 4. **Trading & Marktintegration – mittlere Priorität**
Wichtig, um euer Arbitrage‑Modell weiter zu professionalisieren.

### 4.1 Extrempreis-Szenarien (negative Preise, Peaks)
**Warum wichtig:** Arbitrage wird damit deutlich realistischer.
**Simulation:**
- Negative Preise → Voll-Ladung
- Positive Peaks → Voll-Entladung
- Zyklenbegrenzung berücksichtigen

### 4.2 Intraday-Preisverteilung (Volatility-Modell)
**Parameter:**
- Volatility Index
- Spread Width
- Reaktionsgeschwindigkeit (BESS Response Time)

---

## 5. **Langfristig – Zukunftstechnologien & Nachhaltigkeit**
Für Roadmap 2026+, aber jetzt schon vorbereiten.

### 5.1 LDES – Long Duration Energy Storage
**Simulation für:**
- 6–12 h Entladezeit
- Neue Batterietechnologien (Na‑Ion, Zn‑Ion, Flow)
- Andere Effizienzkennlinien

### 5.2 Nachhaltigkeit & Recycling
**Neue Kennzahlen:**
- CO₂‑Ersparnis pro kWh throughput
- Recyclingquote
- Materialkostenmodell

---

## 6. **n8n‑Integration – Workflow-Schablone**
So integrierst du alle Datenpunkte in n8n.

### 6.1 Inputs
- PV-Daten (PVGIS)
- Verbrauch
- Intraday-Preise (aWATTar, EPEX)
- Netzrestriktionen
- Degradationsmodell

### 6.2 Kern-Workflow
1. **Load Data Node** (Excel/CSV)
2. **Degradation Module** (Function Node)
3. **Dispatch Optimizer** (LangChain / Python Node)
4. **Restrictions Handler** (Function Node)
5. **Economics Engine** (Excel Node oder Python)
6. **Dashboard Output** (Grafana/HTML/PDF)

### 6.3 Output
- PDF Report
- Excel Dashboard
- JSON für API
- Grafiken (SOC, Powerflow, Revenue)

---

## 7. **Priorisierte ToDo-Liste**
### **Stufe 1 – sofort**
1. Netzrestriktionen einbauen  
2. Degradation-Modell  
3. Second-Life-Szenario

### **Stufe 2 – in den nächsten Wochen**
4. Co‑Location PV+BESS  
5. Optimierte Regelstrategien  
6. Extrempreis‑Szenarien

### **Stufe 3 – Zukunft**
7. LDES Modell  
8. Nachhaltigkeit/CO₂ Kennzahlen  

---

## 8. **Datei erstellt für Cursor AI**
Diese `.md` Datei ist so formatiert, dass Cursor AI sie sofort für Code‑Generierung, Workflow‑Design und Implementierungs‑Workflows verwenden kann.

Viel Erfolg beim Implementieren!
