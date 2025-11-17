# 🔍 Vergleich: 10-Jahres-Analyse vs. Use Case Vergleich

## Problemstellung

Die **10-Jahres-Analyse** erscheint stimmig, aber der **Use Case Vergleich** zeigt negative ROI-Werte. Warum?

---

## Kritische Unterschiede

### 1. SRL-Preise (Sekundärregelleistung)

#### 10-Jahres-Analyse (`app/routes.py`, Zeile 5694-5695):
```python
srl_negative_price = 18.0  # €/MW/h
srl_positive_price = 18.0  # €/MW/h
```

#### Use Case Vergleich (`enhanced_economic_analysis.py`, Zeile 322-323):
```python
'srl_positive': 0.018,    # €/MW/h (18.0 €/kW/h / 1000 = 0.018 €/MW/h - KORRIGIERT)
'srl_negative': 0.018,    # €/MW/h (18.0 €/kW/h / 1000 = 0.018 €/MW/h - KORRIGIERT)
```

**❌ PROBLEM:** Faktor 1000 Unterschied!
- 10-Jahres-Analyse: **18.0 €/MW/h**
- Use Case Vergleich: **0.018 €/MW/h**

**Auswirkung:**
- 10-Jahres-Analyse: 20 MW × 8000 h × 18.0 €/MW/h × 0.5 = **1.440.000 €/Jahr** ✅
- Use Case Vergleich: 20 MW × 8000 h × 0.018 €/MW/h × 0.5 = **1.440 €/Jahr** ❌

**Das ist ein Faktor 1000 zu niedrig!**

---

### 2. Marktteilnahme-Raten

#### 10-Jahres-Analyse (`app/routes.py`, Zeile 5688-5691):
```python
srl_negative_ratio = 0.5
srl_positive_ratio = 0.5
sre_negative_ratio = 0.5
sre_positive_ratio = 0.5
# Keine Marktteilnahme-Rate für Intraday (immer 100%)
```

#### Use Case Vergleich (`enhanced_economic_analysis.py`, Zeile 557, 596, 610, 616):
```python
# SRL: 0.5 (50%)
use_case.market_participation.get('srl_positive', 0.5)

# Intraday: 0.5 (50%)
intraday_revenue * use_case.market_participation.get('intraday_trading', 0.5)

# Day-Ahead: 0.3 (30%)
use_case.market_participation.get('day_ahead', 0.3)

# Balancing: 0.2 (20%)
use_case.market_participation.get('balancing_energy', 0.2)
```

**Unterschied:**
- 10-Jahres-Analyse: Intraday-Erlöse werden **ohne Marktteilnahme-Rate** berechnet (100%)
- Use Case Vergleich: Intraday-Erlöse werden mit **50% Marktteilnahme-Rate** multipliziert

**Auswirkung:**
- 10-Jahres-Analyse: Intraday-Erlöse = 100% der berechneten Werte
- Use Case Vergleich: Intraday-Erlöse = 50% der berechneten Werte

---

### 3. Verfügbarkeitsstunden

**Beide verwenden:** 8000 Stunden/Jahr ✅

---

## Berechnungsvergleich (BORBET: 40 MWh / 20 MW)

### 10-Jahres-Analyse

**SRL-Erlöse:**
```
SRL_positive = 20 MW × 8000 h × 18.0 €/MW/h × 0.5 = 1.440.000 €/Jahr
SRL_negative = 20 MW × 8000 h × 18.0 €/MW/h × 0.5 = 1.440.000 €/Jahr
SRL_gesamt = 2.880.000 €/Jahr
```

**Intraday-Erlöse (ohne Marktteilnahme-Rate):**
```
Spot-Arbitrage = 40.000 kWh × 0.5 × 365 × 0.0074 €/kWh = 54.020 €/Jahr
Intraday-Trading = 40.000 kWh × 0.5 × 365 × 0.0111 €/kWh = 81.030 €/Jahr
Balancing Energy = 20.000 kW × 8760 × 0.0231 €/kWh / 1000 = 4.047 €/Jahr
Intraday_gesamt = 54.020 + 81.030 + 4.047 = 139.097 €/Jahr
```

**Gesamterlös pro Jahr (ohne Degradation):**
```
Gesamterlös = 2.880.000 + 20.000 + 139.097 = 3.039.097 €/Jahr
```

**Über 10 Jahre (mit Degradation):**
```
Gesamterlöse (10 Jahre) = ~30.279.839 €
```

---

### Use Case Vergleich (aktuell)

**SRL-Erlöse:**
```
SRL_positive = 20 MW × 8000 h × 0.018 €/MW/h × 0.5 = 1.440 €/Jahr ❌
SRL_negative = 20 MW × 8000 h × 0.018 €/MW/h × 0.5 = 1.440 €/Jahr ❌
SRL_gesamt = 2.880 €/Jahr ❌ (Faktor 1000 zu niedrig!)
```

**Intraday-Erlöse (mit 50% Marktteilnahme-Rate):**
```
Spot-Arbitrage = 40.000 kWh × 0.5 × 365 × 0.0074 €/kWh × 0.85 × 0.5 = 22.958 €/Jahr
Intraday-Trading = 40.000 kWh × 0.5 × 365 × 0.0111 €/kWh × 0.85 × 0.5 = 34.438 €/Jahr
Balancing Energy = 20.000 kW × 8760 × 0.0231 €/kWh / 1000 × 0.85 × 0.5 = 1.720 €/Jahr
Intraday_gesamt = (22.958 + 34.438 + 1.720) = 59.116 €/Jahr
```

**Gesamterlös pro Jahr (ohne Degradation):**
```
Gesamterlös = 2.880 + 20.000 + 59.116 + ... = ~1.000.920 €/Jahr
```

**Über 10 Jahre (mit Degradation):**
```
Gesamterlöse (10 Jahre) = ~9.154.777 €
```

---

## Problem-Zusammenfassung

### Hauptproblem: SRL-Preise

**10-Jahres-Analyse verwendet:** 18.0 €/MW/h  
**Use Case Vergleich verwendet:** 0.018 €/MW/h

**Das ist ein Faktor 1000 Unterschied!**

**Korrektur:** Use Case Vergleich sollte auch **18.0 €/MW/h** verwenden (wie 10-Jahres-Analyse)

---

## Korrektur

### Option 1: SRL-Preise im Use Case Vergleich korrigieren

**Aktuell (FALSCH):**
```python
'srl_positive': 0.018,    # €/MW/h
'srl_negative': 0.018,    # €/MW/h
```

**Korrektur:**
```python
'srl_positive': 18.0,    # €/MW/h (wie im 10-Jahres-Report)
'srl_negative': 18.0,    # €/MW/h (wie im 10-Jahres-Report)
```

### Option 2: Marktteilnahme-Raten angleichen

**Problem:** Use Case Vergleich verwendet Marktteilnahme-Raten, die die Erlöse reduzieren.

**Lösung:** Entweder:
- Marktteilnahme-Raten auf 1.0 setzen (wie 10-Jahres-Analyse)
- Oder: Marktteilnahme-Raten dokumentieren und erklären

---

## Erwartete Werte nach Korrektur

### Für BORBET (40 MWh / 20 MW, Investition 13.600.000 €)

**Nach SRL-Preis-Korrektur:**

**Jährliche Erlöse (ohne Degradation):**
- SRL: 2.880.000 € (statt 2.880 €)
- SRE: 20.000 €
- Intraday: 59.116 € (mit 50% Marktteilnahme)
- Day-Ahead: 109.500 €
- Balancing: 809.424 €
- **Gesamt: ~3.878.040 €/Jahr**

**Über 10 Jahre (mit Degradation):**
- **Gesamterlöse (10 Jahre):** ~35.500.000 €
- **Gesamtkosten (10 Jahre):** ~5.984.829 €
- **Investitionskosten:** 13.600.000 €
- **Netto-Cashflow (10 Jahre):** ~15.915.171 €
- **ROI:** ~117.1% ✅ (positiv!)

---

## Empfohlene Korrekturen

1. **SRL-Preise korrigieren:** 0.018 → 18.0 €/MW/h
2. **Marktteilnahme-Raten prüfen:** Sollten sie verwendet werden?
3. **Konsistenz sicherstellen:** Beide Berechnungen sollten die gleichen Preise verwenden

---

**Dokumentation erstellt:** 2025-01-XX  
**Version:** 1.0  
**Status:** ⚠️ SRL-Preise müssen korrigiert werden

