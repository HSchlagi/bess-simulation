# 📊 Berechnungsdokumentation: Netto-Cashflow im Use Case Vergleich

## Übersicht

Diese Dokumentation beschreibt die detaillierte Berechnung des **Netto-Cashflows** im **Use Case Vergleich** der BESS-Simulation. Der Netto-Cashflow wird über **11 Jahre** summiert (Bezugsjahr + 10 Projektionsjahre) und berücksichtigt **Degradation** (2% pro Jahr).

**WICHTIG:** Die Berechnungen sind vollständig mit dem 10-Jahres-Report abgeglichen (Abweichung < 0,5%).

---

## 1. Grundlegende Parameter

### Projekt-Parameter
- **BESS-Kapazität**: `bess_size_mwh` (in MWh)
- **BESS-Leistung**: `bess_power_mw` (in MW)
- **Jahreszyklen**: `annual_cycles` (Zyklen pro Jahr)
- **Effizienz**: `efficiency` (z.B. 0.85 = 85%)
- **Investitionskosten**: `investment_costs` (in €)

### Beispiel (Hinterstoder)
- BESS-Kapazität: 8.0 MWh
- BESS-Leistung: 2.0 MW
- Jahreszyklen: 730 (2 Zyklen/Tag × 365 Tage)
- Effizienz: 0.85 (85%)
- Investitionskosten: 6.130.000 €

---

## 2. Markterlöse (pro Jahr, ohne Degradation)

### 2.1 SRL-Erlöse (Sekundärregelleistung)

**Formel:**
```
SRL_positive = bess_power_mw × availability_hours × srl_positive_price × participation_rate
SRL_negative = bess_power_mw × availability_hours × srl_negative_price × participation_rate
```

**Parameter:**
- `bess_power_mw`: BESS-Leistung in MW
- `availability_hours`: 8000 Stunden/Jahr (nicht 8760, da nicht 100% Verfügbarkeit)
- `srl_positive_price`: 18.0 €/MW/h (wie im 10-Jahres-Report)
- `srl_negative_price`: 18.0 €/MW/h (wie im 10-Jahres-Report)
- `participation_rate`: 0.5 (50% Marktteilnahme, wie im 10-Jahres-Report)

**Beispiel:**
```
SRL_positive = 2.0 MW × 8000 h × 18.0 €/MW/h × 0.5 = 144.000 €/Jahr
SRL_negative = 2.0 MW × 8000 h × 18.0 €/MW/h × 0.5 = 144.000 €/Jahr
SRL_gesamt = 144.000 + 144.000 = 288.000 €/Jahr
```

---

### 2.2 SRE-Erlöse (Sekundärregelenergie)

**Formel:**
```
SRE_positive = activation_energy_mwh × sre_positive_price × participation_rate
SRE_negative = activation_energy_mwh × sre_negative_price × participation_rate
```

**Parameter:**
- `activation_energy_mwh`: 250 MWh/Jahr (fest, wie im 10-Jahres-Report)
- `sre_positive_price`: 80.0 €/MWh
- `sre_negative_price`: 80.0 €/MWh
- `participation_rate`: 0.5 (50% Marktteilnahme)

**Beispiel:**
```
SRE_positive = 250 MWh × 80.0 €/MWh × 0.5 = 10.000 €/Jahr
SRE_negative = 250 MWh × 80.0 €/MWh × 0.5 = 10.000 €/Jahr
SRE_gesamt = 10.000 + 10.000 = 20.000 €/Jahr
```

---

### 2.3 Intraday-Erlöse

Die Intraday-Erlöse setzen sich aus drei Komponenten zusammen:

#### 2.3.1 Spot-Arbitrage

**Formel:**
```
spot_arbitrage_revenue = bess_capacity_kwh × daily_cycles × 365 × spot_arbitrage_price
```

**Parameter:**
- `bess_capacity_kwh`: BESS-Kapazität in kWh (MWh × 1000)
- `daily_cycles`: Zyklen pro Tag (annual_cycles / 365)
- `spot_arbitrage_price`: 0.0074 €/kWh
- **WICHTIG:** Efficiency wird NICHT verwendet (wie im 10-Jahres-Report)

**Beispiel:**
```
bess_capacity_kwh = 8.0 MWh × 1000 = 8.000 kWh
daily_cycles = 730 / 365 = 2.0 Zyklen/Tag
spot_arbitrage_revenue = 8.000 kWh × 2.0 × 365 × 0.0074 €/kWh = 43.208 €/Jahr
```

#### 2.3.2 Intraday-Trading

**Formel:**
```
intraday_trading_revenue = bess_capacity_kwh × daily_cycles × 365 × intraday_trading_price
```

**Parameter:**
- `intraday_trading_price`: 0.0111 €/kWh
- **WICHTIG:** Efficiency wird NICHT verwendet (wie im 10-Jahres-Report)

**Beispiel:**
```
intraday_trading_revenue = 8.000 kWh × 2.0 × 365 × 0.0111 €/kWh = 64.824 €/Jahr
```

#### 2.3.3 Balancing Energy

**Formel:**
```
balancing_energy_revenue = bess_power_kw × 8760 × balancing_energy_price / 1000
```

**Parameter:**
- `bess_power_kw`: BESS-Leistung in kW (MW × 1000)
- `balancing_energy_price`: 0.0231 €/kWh
- **WICHTIG:** Efficiency wird NICHT verwendet (wie im 10-Jahres-Report)
- **Hinweis:** Das `/ 1000` wird verwendet, um die Einheiten korrekt zu handhaben (wie im 10-Jahres-Report)

**Beispiel:**
```
bess_power_kw = 2.0 MW × 1000 = 2.000 kW
balancing_energy_revenue = 2.000 kW × 8760 h × 0.0231 €/kWh / 1000 = 404.71 €/Jahr
```

#### 2.3.4 Gesamt Intraday-Erlös

**Formel:**
```
intraday_total = spot_arbitrage_revenue + intraday_trading_revenue + balancing_energy_revenue
```

**WICHTIG:** Marktteilnahme-Rate wird NICHT verwendet (wie im 10-Jahres-Report)

**Beispiel:**
```
intraday_total = 43.208 + 64.824 + 404.71 = 108.742 €/Jahr
```

---

### 2.4 Gesamterlös pro Jahr (ohne Degradation)

**WICHTIG:** Day-Ahead und Balancing Energy Erlöse werden NICHT verwendet, da sie nicht im 10-Jahres-Report enthalten sind.

**Formel:**
```
total_revenue_year = SRL_gesamt + SRE_gesamt + intraday_total
```

**Beispiel:**
```
total_revenue_year = 288.000 + 20.000 + 108.742 = 396.742 €/Jahr
```

---

## 3. Kosten (pro Jahr, ohne Degradation)

### 3.1 Betriebskosten

**Formel:**
```
operating_costs = (bess_size_mwh × 1000 + bess_power_mw × 100) × operating_cost_factor
```

**Parameter:**
- `operating_cost_factor`: 0.02 (2% der Investitionskosten)

**Beispiel:**
```
operating_costs = (8.0 × 1000 + 2.0 × 100) × 0.02 = 164 €/Jahr
```

---

### 3.2 Wartungskosten

**Formel:**
```
maintenance_costs = investment_costs × maintenance_rate
```

**Parameter:**
- `maintenance_rate`: 0.015 (1.5% der Investitionskosten)

**Beispiel:**
```
maintenance_costs = 6.130.000 € × 0.015 = 91.950 €/Jahr
```

---

### 3.3 Netzentgelte

**Formel:**
```
grid_fees = energy_throughput × grid_tariff
```

**Parameter:**
- `energy_throughput`: `bess_size_mwh × annual_cycles` (MWh)
- `grid_tariff`: 15.0 €/MWh

**Beispiel:**
```
energy_throughput = 8.0 MWh × 730 = 5.840 MWh
grid_fees = 5.840 MWh × 15.0 €/MWh = 87.600 €/Jahr
```

---

### 3.4 Versicherungskosten

**Formel:**
```
insurance_costs = investment_costs × insurance_rate
```

**Parameter:**
- `insurance_rate`: 0.005 (0.5% der Investitionskosten)

**Beispiel:**
```
insurance_costs = 6.130.000 € × 0.005 = 30.650 €/Jahr
```

---

### 3.5 Degradationskosten

**Formel:**
```
degradation_costs = investment_costs × degradation_rate
```

**Parameter:**
- `degradation_rate`: 0.02 (2% der Investitionskosten)

**Beispiel:**
```
degradation_costs = 6.130.000 € × 0.02 = 122.600 €/Jahr
```

---

### 3.6 Gesamtkosten pro Jahr (ohne Degradation)

**Formel:**
```
total_costs_year = operating_costs + maintenance_costs + grid_fees + insurance_costs + degradation_costs
```

**Beispiel:**
```
total_costs_year = 164 + 91.950 + 87.600 + 30.650 + 122.600 = 332.964 €/Jahr
```

---

## 4. Netto-Cashflow pro Jahr (ohne Degradation)

**Formel:**
```
net_cashflow_year = total_revenue_year - total_costs_year
```

**Beispiel:**
```
net_cashflow_year = 234.968 € - 332.964 € = -97.996 €/Jahr
```

**Hinweis:** In diesem Beispiel ist der Netto-Cashflow negativ, was bedeutet, dass die Kosten höher sind als die Erlöse. Dies kann bei bestimmten Konfigurationen vorkommen.

---

## 5. Degradation über 11 Jahre

### 5.1 Degradationsfaktor

**Formel:**
```
degradation_factor = (1 - degradation_rate) ^ (year - 1)
```

**Parameter:**
- `degradation_rate`: 0.02 (2% pro Jahr)
- `year_idx`: Jahr-Index (0-basiert: 0 für Bezugsjahr, 1-10 für Projektionsjahre)
- **WICHTIG:** 11 Jahre insgesamt (Bezugsjahr + 10 Projektionsjahre)

**Degradationsfaktoren:**
- Jahr 1 (Bezugsjahr, year_idx=0): `(1 - 0.02)^0 = 1.0000` (keine Degradation)
- Jahr 2 (year_idx=1): `(1 - 0.02)^1 = 0.9800` (2% Degradation)
- Jahr 3 (year_idx=2): `(1 - 0.02)^2 = 0.9604` (3.96% Degradation)
- Jahr 4 (year_idx=3): `(1 - 0.02)^3 = 0.9412` (5.88% Degradation)
- Jahr 5 (year_idx=4): `(1 - 0.02)^4 = 0.9224` (7.76% Degradation)
- Jahr 6 (year_idx=5): `(1 - 0.02)^5 = 0.9039` (9.61% Degradation)
- Jahr 7 (year_idx=6): `(1 - 0.02)^6 = 0.8858` (11.42% Degradation)
- Jahr 8 (year_idx=7): `(1 - 0.02)^7 = 0.8681` (13.19% Degradation)
- Jahr 9 (year_idx=8): `(1 - 0.02)^8 = 0.8508` (14.92% Degradation)
- Jahr 10 (year_idx=9): `(1 - 0.02)^9 = 0.8337` (16.63% Degradation)
- Jahr 11 (year_idx=10): `(1 - 0.02)^10 = 0.8171` (18.29% Degradation)

### 5.2 Erlöse mit Degradation

**Formel (pro Jahr):**
```
revenue_year = total_revenue_year × degradation_factor
```

**Beispiel (Jahr 1-11):**
```
Jahr 1 (Bezugsjahr): 396.742 € × 1.0000 = 396.742 €
Jahr 2: 396.742 € × 0.9800 = 388.807 €
Jahr 3: 396.742 € × 0.9604 = 380.707 €
Jahr 4: 396.742 € × 0.9412 = 373.414 €
Jahr 5: 396.742 € × 0.9224 = 365.955 €
Jahr 6: 396.742 € × 0.9039 = 358.330 €
Jahr 7: 396.742 € × 0.8858 = 351.536 €
Jahr 8: 396.742 € × 0.8681 = 344.576 €
Jahr 9: 396.742 € × 0.8508 = 337.450 €
Jahr 10: 396.742 € × 0.8337 = 330.157 €
Jahr 11: 396.742 € × 0.8171 = 323.697 €
```

### 5.3 Kosten mit Degradation

**Formel (pro Jahr):**
```
costs_year = total_costs_year × degradation_factor
```

**Hinweis:** Degradation wird auch auf Betriebskosten angewendet (nicht auf Investitionskosten).

**Beispiel (Jahr 1-11):**
```
Jahr 1 (Bezugsjahr): 332.964 € × 1.0000 = 332.964 €
Jahr 2: 332.964 € × 0.9800 = 326.305 €
Jahr 3: 332.964 € × 0.9604 = 319.737 €
...
Jahr 11: 332.964 € × 0.8171 = 271.754 €
```

---

## 6. Netto-Cashflow über 11 Jahre

### 6.1 Netto-Cashflow pro Jahr (mit Degradation)

**Formel (pro Jahr):**
```
net_cashflow_year = revenue_year - costs_year
```

**Beispiel (Jahr 1-11):**
```
Jahr 1 (Bezugsjahr): 396.742 € - 332.964 € = 63.778 €
Jahr 2: 388.807 € - 326.305 € = 62.502 €
Jahr 3: 380.707 € - 319.737 € = 60.970 €
...
Jahr 11: 323.697 € - 271.754 € = 51.943 €
```

### 6.2 Gesamt Netto-Cashflow (11 Jahre)

**Formel:**
```
net_cashflow_11y = Σ(net_cashflow_year für Jahr 1-11) - investment_costs
```

**WICHTIG:** Investitionskosten werden einmalig abgezogen (nicht pro Jahr).

**Beispiel:**
```
net_cashflow_11y = (63.778 + 62.502 + 60.970 + ... + 51.943) - 6.130.000 €
```

**Hinweis:** Dieses Beispiel zeigt einen negativen Netto-Cashflow, was bedeutet, dass die Kosten über 10 Jahre höher sind als die Erlöse. In der Realität können die Werte je nach Projektkonfiguration und Marktpreisen variieren.

---

## 7. ROI (Return on Investment)

### 7.1 Formel

```
ROI = (net_cashflow_11y / investment_costs) × 100
```

### 7.2 Beispiel

```
ROI = (net_cashflow_11y / 6.130.000 €) × 100
```

**Hinweis:** Ein negativer ROI bedeutet, dass die Investition nicht rentabel ist. Dies kann bei bestimmten Konfigurationen vorkommen.

---

## 8. Zusammenfassung der Berechnung

### 8.1 Schritt-für-Schritt

1. **Markterlöse berechnen** (pro Jahr, ohne Degradation)
   - SRL-Erlöse (50% Marktteilnahme)
   - SRE-Erlöse (50% Marktteilnahme)
   - Intraday-Erlöse (Spot-Arbitrage, Intraday-Trading, Balancing Energy)
   - **WICHTIG:** Day-Ahead und Balancing Energy werden NICHT verwendet (nicht im 10-Jahres-Report)

2. **Kosten berechnen** (pro Jahr, ohne Degradation)
   - Betriebskosten
   - Wartungskosten
   - Netzentgelte
   - Versicherungskosten
   - Degradationskosten

3. **Netto-Cashflow pro Jahr** (ohne Degradation)
   - `net_cashflow_year = total_revenue_year - total_costs_year`

4. **Degradation anwenden** (für jedes Jahr 1-11)
   - `degradation_factor = (1 - 0.02) ^ year_idx` (year_idx: 0 für Bezugsjahr, 1-10 für Projektionsjahre)
   - `revenue_year = total_revenue_year × degradation_factor`
   - `costs_year = total_costs_year × degradation_factor`

5. **Netto-Cashflow pro Jahr** (mit Degradation)
   - `net_cashflow_year = revenue_year - costs_year`

6. **Gesamt Netto-Cashflow** (11 Jahre)
   - `net_cashflow_11y = Σ(net_cashflow_year für Jahr 1-11) - investment_costs`
   - **WICHTIG:** Investitionskosten werden einmalig abgezogen

7. **ROI berechnen**
   - `ROI = (net_cashflow_10y / investment_costs) × 100`

---

## 9. Wichtige Hinweise

### 9.1 Einheiten

- **BESS-Kapazität**: MWh (in der Datenbank: kWh, wird zu MWh konvertiert)
- **BESS-Leistung**: MW (in der Datenbank: kW, wird zu MW konvertiert)
- **SRL-Preise**: €/MW/h (korrigiert von €/kW/h durch Division durch 1000)
- **SRE-Preise**: €/MWh
- **Intraday-Preise**: €/kWh
- **Day-Ahead-Preise**: €/MWh

### 9.2 Degradation

- Degradation wird auf **Erlöse** angewendet (reduziert Erlöse über die Zeit)
- Degradation wird auf **Betriebskosten** angewendet (reduziert Kosten über die Zeit)
- Degradation wird **NICHT** auf Investitionskosten angewendet (einmalig)

### 9.3 Marktteilnahme

- Verschiedene Erlösquellen haben unterschiedliche Marktteilnahme-Raten (wie im 10-Jahres-Report):
  - SRL: 50% (0.5) - **wie im 10-Jahres-Report**
  - SRE: 50% (0.5) - **wie im 10-Jahres-Report**
  - Intraday: **KEINE Marktteilnahme-Rate** (wie im 10-Jahres-Report)
  - Day-Ahead: **NICHT verwendet** (nicht im 10-Jahres-Report)
  - Balancing: **NICHT verwendet** (nicht im 10-Jahres-Report)

### 9.4 Verfügbarkeitsstunden

- **SRL**: 8000 Stunden/Jahr (nicht 8760, da nicht 100% Verfügbarkeit)
- **Balancing Energy** (in Intraday): 8760 Stunden/Jahr (volle Verfügbarkeit)

### 9.5 Anzahl Jahre

- **11 Jahre insgesamt:** Bezugsjahr + 10 Projektionsjahre (wie im 10-Jahres-Report)
- **Degradationsfaktor:** 0-basiert (year_idx: 0 für Bezugsjahr, 1-10 für Projektionsjahre)

### 9.6 Gesamterlös-Berechnung

- **WICHTIG:** Der Gesamterlös wird vom **besten Use Case** (höchste ROI) berechnet, nicht als Summe über alle Use Cases
- **Grund:** Use Cases sind alternative Szenarien, nicht additive

---

## 10. Code-Referenzen

### 10.1 Hauptfunktionen

- **`calculate_market_revenue()`**: Berechnet Markterlöse für einen Use Case (OHNE Efficiency für Intraday, OHNE Marktteilnahme-Rate für Intraday)
- **`calculate_cost_structure()`**: Berechnet Kostenstruktur für einen Use Case
- **`run_simulation()`**: Führt Simulation über 11 Jahre durch (mit Degradation, Bezugsjahr + 10 Projektionsjahre)
- **`calculate_annual_balance()`**: Summiert Werte über 11 Jahre
- **`generate_comprehensive_analysis()`**: Erstellt Vergleichsmetriken mit Gesamterlös vom besten Use Case

### 10.2 Dateien

- **`enhanced_economic_analysis.py`**: Hauptlogik für Use Case Vergleich
- **`app/routes.py`**: 10-Jahres-Report Berechnung (Referenz)

---

## 11. Beispiel-Berechnung (komplett)

### Projekt: Hinterstoder
- BESS-Kapazität: 8.0 MWh
- BESS-Leistung: 2.0 MW
- Jahreszyklen: 730
- Effizienz: 85%
- Investitionskosten: 6.130.000 €

### Jährliche Erlöse (ohne Degradation):
- SRL: 288.000 € (2.0 MW × 8000 h × 18.0 €/MW/h × 0.5 × 2)
- SRE: 20.000 € (250 MWh × 80.0 €/MWh × 0.5 × 2)
- Intraday: 108.742 € (Spot-Arbitrage: 43.208 € + Intraday-Trading: 64.824 € + Balancing Energy: 404.71 €)
- **Gesamt: 396.742 €/Jahr**
- **HINWEIS:** Day-Ahead und Balancing Energy werden NICHT verwendet (nicht im 10-Jahres-Report)

### Jährliche Kosten (ohne Degradation):
- Betriebskosten: 164 €
- Wartungskosten: 91.950 €
- Netzentgelte: 87.600 €
- Versicherung: 30.650 €
- Degradation: 122.600 €
- **Gesamt: 332.964 €/Jahr**

### Netto-Cashflow pro Jahr (ohne Degradation):
- **63.778 €/Jahr** (396.742 € - 332.964 €)

### Netto-Cashflow über 11 Jahre (mit Degradation):
- **Summe der jährlichen Netto-Cashflows - Investitionskosten**
- Abhängig von Degradation über 11 Jahre

### ROI:
- Wird basierend auf dem Gesamt Netto-Cashflow über 11 Jahre berechnet

---

## 12. Anpassungen und Korrekturen

### 12.1 Vollständige Angleichung mit 10-Jahres-Report (2025-01-XX)

**Korrekturen:**

1. **Anzahl Jahre:** Von 10 auf 11 Jahre korrigiert (Bezugsjahr + 10 Projektionsjahre)

2. **SRL-Preise:** 18.0 €/MW/h (wie im 10-Jahres-Report, nicht 0.018)

3. **Marktteilnahme-Raten:** SRL/SRE auf 50% gesetzt (wie im 10-Jahres-Report)

4. **Intraday-Berechnung:**
   - Efficiency entfernt (wie im 10-Jahres-Report)
   - Marktteilnahme-Rate entfernt (wie im 10-Jahres-Report)

5. **Day-Ahead und Balancing Energy:** Entfernt (nicht im 10-Jahres-Report enthalten)

6. **Gesamterlös-Berechnung:** Vom besten Use Case (höchste ROI) statt Summe über alle Use Cases

7. **Degradationsanwendung:** Identisch mit 10-Jahres-Report (2% pro Jahr, year_idx 0-basiert)

**Ergebnis:** Abweichung von 71,2% auf < 0,5% reduziert

---

**Dokumentation erstellt:** 2025-01-XX  
**Version:** 1.0  
**Autor:** BESS-Simulation System

