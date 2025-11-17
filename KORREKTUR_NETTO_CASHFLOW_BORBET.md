# 🔧 Korrektur: Netto-Cashflow Berechnung für BORBET

## Problem identifiziert

**Datum:** 2025-01-XX  
**Projekt:** BORBET  
**Problem:** Netto-Cashflow wird falsch berechnet - Investitionskosten werden nicht abgezogen!

---

## BORBET-Projektparameter (tatsächlich)

**Aus der Datenbank geladen:**
- **Projekt ID:** 5
- **Projekt Name:** BORBET
- **BESS-Kapazität:** 40.000 kWh (40 MWh) ⚠️ **NICHT 8 MWh!**
- **BESS-Leistung:** 20.000 kW (20 MW) ⚠️ **NICHT 2 MW!**
- **Investitionskosten:** 13.600.000 € ⚠️ **NICHT 6.130.000 €!**
  - BESS: 11.000.000 €
  - PV: 2.100.000 €
  - Other: 500.000 €
- **PV-Leistung:** 2.500 kW
- **Tägliche Zyklen:** 0.50 (182 Zyklen/Jahr)

---

## Berechnete Werte (mit korrekten Parametern)

### Jährliche Erlöse (ohne Degradation)

- **SRL (positiv + negativ):** 2.880 €/Jahr
- **SRE (positiv + negativ):** 20.000 €/Jahr
- **Intraday (Spot + Trading + Balancing):** 59.116 €/Jahr
- **Day-Ahead:** 109.500 €/Jahr
- **Balancing:** 809.424 €/Jahr
- **GESAMT:** ~1.000.920 €/Jahr

### Jährliche Kosten (ohne Degradation)

- **Betriebskosten:** 840 €/Jahr
- **Wartungskosten:** 204.000 €/Jahr
- **Netzentgelte:** 109.500 €/Jahr
- **Versicherung:** 68.000 €/Jahr
- **Degradation:** 272.000 €/Jahr
- **GESAMT:** ~654.340 €/Jahr

### Netto-Cashflow pro Jahr (ohne Degradation)

- **346.580 €/Jahr** (positiv!)

### Über 10 Jahre (mit Degradation)

- **Gesamterlöse (10 Jahre):** ~9.154.777 €
- **Gesamtkosten (10 Jahre):** ~5.984.829 €
- **Investitionskosten:** 13.600.000 €

### Netto-Cashflow über 10 Jahre

**MIT Investitionskosten:**
```
Netto-Cashflow = 9.154.777 € - 5.984.829 € - 13.600.000 € = -10.430.052 €
```

**OHNE Investitionskosten:**
```
Netto-Cashflow = 9.154.777 € - 5.984.829 € = 3.169.948 €
```

### ROI

```
ROI = (-10.430.052 € / 13.600.000 €) × 100 = -76.69%
```

---

## Vergleich mit angezeigten Werten

### Angezeigte Werte (aus Screenshot)

- **UC1 Netto-Cashflow:** 11.364.535 €
- **UC2 Netto-Cashflow:** -4.769.798 €
- **UC3 Netto-Cashflow:** -4.800.905 €
- **Gesamterlös:** 22.263.463 €

### Berechnete Werte (mit tatsächlichen Parametern)

- **Netto-Cashflow (10 Jahre, MIT Investition):** -10.430.052 €
- **Netto-Cashflow (10 Jahre, OHNE Investition):** 3.169.948 €
- **Gesamterlös (10 Jahre):** 9.154.777 €

### Abweichungen

**Netto-Cashflow:**
- Erwartet (MIT Investition): -10.430.052 €
- Angezeigt: 11.364.535 €
- **Differenz:** 21.794.587 € ❌

**Vergleich:**
- Angezeigter Wert (11.364.535 €) ist **näher** am "OHNE Investition"-Wert (3.169.948 €)
- **Das bedeutet: Investitionskosten werden NICHT abgezogen!**

---

## Korrektur

### Problem in `enhanced_economic_analysis.py` (Zeile 209)

**Vorher (FALSCH):**
```python
# Netto-Cashflow über 10 Jahre (ohne Investitionskosten)
net_cashflow_10y = total_revenue_10y - total_costs_10y
# ❌ Investitionskosten werden NICHT abgezogen!
```

**Nachher (KORREKT):**
```python
# Netto-Cashflow über 10 Jahre (MIT Investitionskosten)
# WICHTIG: Investitionskosten müssen abgezogen werden!
net_cashflow_10y = total_revenue_10y - total_costs_10y - total_investment
# ✅ Investitionskosten werden jetzt abgezogen!
```

---

## Erwartete Werte nach Korrektur

### Für BORBET (40 MWh / 20 MW, Investition 13.600.000 €)

**UC1 (Nur Verbrauch):**
- Gesamterlöse (10 Jahre): ~9.154.777 €
- Gesamtkosten (10 Jahre): ~5.984.829 €
- Investitionskosten: 13.600.000 €
- **Netto-Cashflow (10 Jahre):** ~-10.430.052 €
- **ROI:** ~-76.69%

**Hinweis:** Ein negativer Netto-Cashflow ist bei dieser Konfiguration realistisch, da:
- Die Investitionskosten sehr hoch sind (13.600.000 €)
- Die jährlichen Erlöse (~1.000.920 €) die jährlichen Kosten (~654.340 €) zwar übersteigen
- Aber über 10 Jahre nicht ausreichen, um die Investition zu amortisieren

---

## Weitere Probleme

### 1. Gesamterlös ist falsch

**Aktuell:**
```python
'total_revenue': sum(data['annual_balance']['total_revenue'] 
                   for data in analysis_results['use_cases'].values())
```

**Problem:** Summiert alle Use Cases, obwohl sie alternativ sind.

**Korrektur:** Nur den Erlös des besten Use Cases anzeigen.

### 2. Use Cases haben unterschiedliche Parameter

**Problem:** UC1, UC2, UC3 haben möglicherweise unterschiedliche:
- Marktteilnahme-Raten
- Zyklenanzahl
- Effizienz

**Lösung:** Prüfe, ob die Use Cases korrekt aus der Datenbank geladen werden.

---

## Zusammenfassung

### Gefundene Probleme

1. ✅ **Investitionskosten werden nicht abgezogen** → **KORRIGIERT**
2. ⚠️ **Gesamterlös summiert alle Use Cases** → **MUSS KORRIGIERT WERDEN**
3. ⚠️ **Falsche Projektparameter verwendet** → **JETZT MIT BORBET-PARAMETERN**

### Korrekturen durchgeführt

1. ✅ Investitionskosten werden jetzt in `calculate_annual_balance()` abgezogen
2. ✅ Validierungsskript erstellt (`validate_borbet_values.py`)
3. ✅ Dokumentation aktualisiert

### Nächste Schritte

1. **Gesamterlös korrigieren:** Nur besten Use Case anzeigen
2. **Testen:** Use Case Vergleich mit BORBET neu berechnen
3. **Validieren:** Werte mit Validierungsskript prüfen

---

**Dokumentation erstellt:** 2025-01-XX  
**Version:** 1.1  
**Status:** ✅ Investitionskosten-Korrektur durchgeführt

