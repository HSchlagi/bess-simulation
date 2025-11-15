# 📊 Berechnungsdokumentation: Netto-Cashflow im Use Case Vergleich

## Übersicht

Diese Dokumentation beschreibt die detaillierte Berechnung des **Netto-Cashflows** im **Use Case Vergleich** der BESS-Simulation. Der Netto-Cashflow wird über **10 Jahre** summiert und berücksichtigt **Degradation** (2% pro Jahr).

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
- `srl_positive_price`: 0.018 €/MW/h (korrigiert von 18.0 €/kW/h)
- `srl_negative_price`: 0.018 €/MW/h (korrigiert von 18.0 €/kW/h)
- `participation_rate`: 0.5 (50% Marktteilnahme)

**Beispiel:**
```
SRL_positive = 2.0 MW × 8000 h × 0.018 €/MW/h × 0.5 = 144 €/Jahr
SRL_negative = 2.0 MW × 8000 h × 0.018 €/MW/h × 0.5 = 144 €/Jahr
SRL_gesamt = 144 + 144 = 288 €/Jahr
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
spot_arbitrage_revenue = bess_capacity_kwh × daily_cycles × 365 × spot_arbitrage_price × efficiency
```

**Parameter:**
- `bess_capacity_kwh`: BESS-Kapazität in kWh (MWh × 1000)
- `daily_cycles`: Zyklen pro Tag (annual_cycles / 365)
- `spot_arbitrage_price`: 0.0074 €/kWh
- `efficiency`: 0.85 (85%)

**Beispiel:**
```
bess_capacity_kwh = 8.0 MWh × 1000 = 8.000 kWh
daily_cycles = 730 / 365 = 2.0 Zyklen/Tag
spot_arbitrage_revenue = 8.000 kWh × 2.0 × 365 × 0.0074 €/kWh × 0.85 = 36.773 €/Jahr
```

#### 2.3.2 Intraday-Trading

**Formel:**
```
intraday_trading_revenue = bess_capacity_kwh × daily_cycles × 365 × intraday_trading_price × efficiency
```

**Parameter:**
- `intraday_trading_price`: 0.0111 €/kWh

**Beispiel:**
```
intraday_trading_revenue = 8.000 kWh × 2.0 × 365 × 0.0111 €/kWh × 0.85 = 55.160 €/Jahr
```

#### 2.3.3 Balancing Energy

**Formel:**
```
balancing_energy_revenue = bess_power_kw × 8760 × balancing_energy_price / 1000 × efficiency
```

**Parameter:**
- `bess_power_kw`: BESS-Leistung in kW (MW × 1000)
- `balancing_energy_price`: 0.0231 €/kWh
- `efficiency`: 0.85 (85%)
- **Hinweis:** Das `/ 1000` wird verwendet, um die Einheiten korrekt zu handhaben (wie im 10-Jahres-Report)

**Beispiel:**
```
bess_power_kw = 2.0 MW × 1000 = 2.000 kW
balancing_energy_revenue = 2.000 kW × 8760 h × 0.0231 €/kWh / 1000 × 0.85 = 343 €/Jahr
```

#### 2.3.4 Gesamt Intraday-Erlös

**Formel:**
```
intraday_total = (spot_arbitrage_revenue + intraday_trading_revenue + balancing_energy_revenue) × participation_rate
```

**Parameter:**
- `participation_rate`: 0.5 (50% Marktteilnahme)

**Beispiel:**
```
intraday_total = (36.773 + 55.160 + 343) × 0.5 = 46.138 €/Jahr
```

---

### 2.4 Day-Ahead-Erlöse

**Formel:**
```
day_ahead_revenue = bess_size_mwh × annual_cycles × day_ahead_price × participation_rate
```

**Parameter:**
- `bess_size_mwh`: BESS-Kapazität in MWh
- `annual_cycles`: Jahreszyklen
- `day_ahead_price`: 50.0 €/MWh
- `participation_rate`: 0.3 (30% Marktteilnahme)

**Beispiel:**
```
day_ahead_revenue = 8.0 MWh × 730 × 50.0 €/MWh × 0.3 = 87.600 €/Jahr
```

---

### 2.5 Balancing-Erlöse (Ausgleichsenergie)

**Formel:**
```
balancing_revenue = bess_power_mw × 8760 × balancing_price × participation_rate
```

**Parameter:**
- `bess_power_mw`: BESS-Leistung in MW
- `balancing_price`: 23.1 €/MWh (0.0231 €/kWh × 1000)
- `participation_rate`: 0.2 (20% Marktteilnahme)

**Beispiel:**
```
balancing_revenue = 2.0 MW × 8760 h × 23.1 €/MWh × 0.2 = 80.942 €/Jahr
```

---

### 2.6 Gesamterlös pro Jahr (ohne Degradation)

**Formel:**
```
total_revenue_year = SRL_gesamt + SRE_gesamt + intraday_total + day_ahead_revenue + balancing_revenue
```

**Beispiel:**
```
total_revenue_year = 288 + 20.000 + 46.138 + 87.600 + 80.942 = 234.968 €/Jahr
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

## 5. Degradation über 10 Jahre

### 5.1 Degradationsfaktor

**Formel:**
```
degradation_factor = (1 - degradation_rate) ^ (year - 1)
```

**Parameter:**
- `degradation_rate`: 0.02 (2% pro Jahr)
- `year`: Jahr seit Inbetriebnahme (1-10)

**Degradationsfaktoren:**
- Jahr 1: `(1 - 0.02)^0 = 1.0000` (keine Degradation)
- Jahr 2: `(1 - 0.02)^1 = 0.9800` (2% Degradation)
- Jahr 3: `(1 - 0.02)^2 = 0.9604` (3.96% Degradation)
- Jahr 4: `(1 - 0.02)^3 = 0.9412` (5.88% Degradation)
- Jahr 5: `(1 - 0.02)^4 = 0.9224` (7.76% Degradation)
- Jahr 6: `(1 - 0.02)^5 = 0.9039` (9.61% Degradation)
- Jahr 7: `(1 - 0.02)^6 = 0.8858` (11.42% Degradation)
- Jahr 8: `(1 - 0.02)^7 = 0.8681` (13.19% Degradation)
- Jahr 9: `(1 - 0.02)^8 = 0.8508` (14.92% Degradation)
- Jahr 10: `(1 - 0.02)^9 = 0.8337` (16.63% Degradation)

### 5.2 Erlöse mit Degradation

**Formel (pro Jahr):**
```
revenue_year = total_revenue_year × degradation_factor
```

**Beispiel (Jahr 1-10):**
```
Jahr 1: 234.968 € × 1.0000 = 234.968 €
Jahr 2: 234.968 € × 0.9800 = 230.269 €
Jahr 3: 234.968 € × 0.9604 = 225.620 €
Jahr 4: 234.968 € × 0.9412 = 221.020 €
Jahr 5: 234.968 € × 0.9224 = 216.468 €
Jahr 6: 234.968 € × 0.9039 = 211.963 €
Jahr 7: 234.968 € × 0.8858 = 208.504 €
Jahr 8: 234.968 € × 0.8681 = 205.090 €
Jahr 9: 234.968 € × 0.8508 = 201.721 €
Jahr 10: 234.968 € × 0.8337 = 198.395 €
```

### 5.3 Kosten mit Degradation

**Formel (pro Jahr):**
```
costs_year = total_costs_year × degradation_factor
```

**Hinweis:** Degradation wird auch auf Betriebskosten angewendet (nicht auf Investitionskosten).

**Beispiel (Jahr 1-10):**
```
Jahr 1: 332.964 € × 1.0000 = 332.964 €
Jahr 2: 332.964 € × 0.9800 = 326.305 €
Jahr 3: 332.964 € × 0.9604 = 319.737 €
...
Jahr 10: 332.964 € × 0.8337 = 277.482 €
```

---

## 6. Netto-Cashflow über 10 Jahre

### 6.1 Netto-Cashflow pro Jahr (mit Degradation)

**Formel (pro Jahr):**
```
net_cashflow_year = revenue_year - costs_year
```

**Beispiel (Jahr 1-10):**
```
Jahr 1: 234.968 € - 332.964 € = -97.996 €
Jahr 2: 230.269 € - 326.305 € = -96.036 €
Jahr 3: 225.620 € - 319.737 € = -94.117 €
...
Jahr 10: 198.395 € - 277.482 € = -79.087 €
```

### 6.2 Gesamt Netto-Cashflow (10 Jahre)

**Formel:**
```
net_cashflow_10y = Σ(net_cashflow_year für Jahr 1-10)
```

**Beispiel:**
```
net_cashflow_10y = -97.996 - 96.036 - 94.117 - ... - 79.087 = -880.000 € (ca.)
```

**Hinweis:** Dieses Beispiel zeigt einen negativen Netto-Cashflow, was bedeutet, dass die Kosten über 10 Jahre höher sind als die Erlöse. In der Realität können die Werte je nach Projektkonfiguration und Marktpreisen variieren.

---

## 7. ROI (Return on Investment)

### 7.1 Formel

```
ROI = (net_cashflow_10y / investment_costs) × 100
```

### 7.2 Beispiel

```
ROI = (-880.000 € / 6.130.000 €) × 100 = -14.4%
```

**Hinweis:** Ein negativer ROI bedeutet, dass die Investition nicht rentabel ist. Dies kann bei bestimmten Konfigurationen vorkommen.

---

## 8. Zusammenfassung der Berechnung

### 8.1 Schritt-für-Schritt

1. **Markterlöse berechnen** (pro Jahr, ohne Degradation)
   - SRL-Erlöse
   - SRE-Erlöse
   - Intraday-Erlöse (Spot-Arbitrage, Intraday-Trading, Balancing Energy)
   - Day-Ahead-Erlöse
   - Balancing-Erlöse

2. **Kosten berechnen** (pro Jahr, ohne Degradation)
   - Betriebskosten
   - Wartungskosten
   - Netzentgelte
   - Versicherungskosten
   - Degradationskosten

3. **Netto-Cashflow pro Jahr** (ohne Degradation)
   - `net_cashflow_year = total_revenue_year - total_costs_year`

4. **Degradation anwenden** (für jedes Jahr 1-10)
   - `degradation_factor = (1 - 0.02) ^ (year - 1)`
   - `revenue_year = total_revenue_year × degradation_factor`
   - `costs_year = total_costs_year × degradation_factor`

5. **Netto-Cashflow pro Jahr** (mit Degradation)
   - `net_cashflow_year = revenue_year - costs_year`

6. **Gesamt Netto-Cashflow** (10 Jahre)
   - `net_cashflow_10y = Σ(net_cashflow_year für Jahr 1-10)`

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

- Verschiedene Erlösquellen haben unterschiedliche Marktteilnahme-Raten:
  - SRL: 50% (0.5)
  - SRE: 50% (0.5)
  - Intraday: 50% (0.5)
  - Day-Ahead: 30% (0.3)
  - Balancing: 20% (0.2)

### 9.4 Verfügbarkeitsstunden

- **SRL**: 8000 Stunden/Jahr (nicht 8760, da nicht 100% Verfügbarkeit)
- **Balancing Energy**: 8760 Stunden/Jahr (volle Verfügbarkeit)

---

## 10. Code-Referenzen

### 10.1 Hauptfunktionen

- **`calculate_market_revenue()`**: Berechnet Markterlöse für einen Use Case
- **`calculate_cost_structure()`**: Berechnet Kostenstruktur für einen Use Case
- **`run_simulation()`**: Führt Simulation über 10 Jahre durch (mit Degradation)
- **`calculate_annual_balance()`**: Summiert Werte über 10 Jahre

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
- SRL: 288 €
- SRE: 20.000 €
- Intraday: 46.138 €
- Day-Ahead: 87.600 €
- Balancing: 80.942 €
- **Gesamt: 234.968 €/Jahr**

### Jährliche Kosten (ohne Degradation):
- Betriebskosten: 164 €
- Wartungskosten: 91.950 €
- Netzentgelte: 87.600 €
- Versicherung: 30.650 €
- Degradation: 122.600 €
- **Gesamt: 332.964 €/Jahr**

### Netto-Cashflow pro Jahr (ohne Degradation):
- **-97.996 €/Jahr**

### Netto-Cashflow über 10 Jahre (mit Degradation):
- **~-880.000 €** (ca., abhängig von Degradation)

### ROI:
- **-14.4%** (negativ, Investition nicht rentabel in diesem Beispiel)

---

## 12. Anpassungen und Korrekturen

### 12.1 SRL-Preise korrigiert (2025-01-XX)

**Problem:** SRL-Preise waren zu hoch (18.0 €/MW/h statt 0.018 €/MW/h)

**Korrektur:**
- Vorher: `18.0 €/MW/h`
- Nachher: `0.018 €/MW/h` (18.0 / 1000)

**Auswirkung:** SRL-Erlöse werden um Faktor 1000 reduziert

### 12.2 Balancing Energy aktiviert (2025-01-XX)

**Problem:** Balancing Energy war deaktiviert (`balancing_energy_revenue = 0`)

**Korrektur:**
- Balancing Energy Berechnung wieder aktiviert
- Formel wie im 10-Jahres-Report: `bess_power_kw × 8760 × balancing_energy_price / 1000 × efficiency`

---

**Dokumentation erstellt:** 2025-01-XX  
**Version:** 1.0  
**Autor:** BESS-Simulation System

