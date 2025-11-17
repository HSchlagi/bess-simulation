# 🔍 Validierung der Use Case Vergleich Werte

## Problemstellung

Im Use Case Vergleich werden folgende Werte angezeigt:
- **UC1 Netto-Cashflow:** 11.364.535 €
- **UC2 Netto-Cashflow:** -4.769.798 €
- **UC3 Netto-Cashflow:** -4.800.905 €
- **Gesamterlös:** 22.263.463 €

**Frage:** Wie können wir sicherstellen, dass diese Werte korrekt sind?

**WICHTIG:** Diese Werte beziehen sich auf das **BORBET-Projekt**, nicht auf Hinterstoder!

### BORBET-Projektparameter (tatsächlich):
- **BESS-Kapazität:** 40.000 kWh (40 MWh)
- **BESS-Leistung:** 20.000 kW (20 MW)
- **Investitionskosten:** 13.600.000 €
- **Tägliche Zyklen:** 0.50 (182 Zyklen/Jahr)
- **PV-Leistung:** 2.500 kW

---

## 1. Was bedeutet "Gesamterlös"?

### 1.1 Aktuelle Berechnung

Der "Gesamterlös" wird aktuell wie folgt berechnet:

```python
'total_revenue': sum(data['annual_balance']['total_revenue'] 
                   for data in analysis_results['use_cases'].values())
```

**Das bedeutet:**
- UC1 `total_revenue` (10 Jahre) + UC2 `total_revenue` (10 Jahre) + UC3 `total_revenue` (10 Jahre)
- **Summe aller 10-Jahres-Erlöse über alle Use Cases**

### 1.2 Ist das korrekt?

**❌ NEIN!** Die Use Cases sind **alternative Szenarien**, nicht additive:

- **UC1:** Nur Verbrauch (ein Szenario)
- **UC2:** Nur Einspeisung (ein anderes Szenario)
- **UC3:** Hybrid (ein drittes Szenario)

**Man kann nicht alle drei gleichzeitig betreiben!**

### 1.3 Was sollte "Gesamterlös" bedeuten?

**Option 1: Gesamterlös des besten Use Cases**
- Nur der Erlös des empfohlenen Use Cases (UC1)
- **Korrekt:** 11.364.535 € (nur UC1)

**Option 2: Durchschnittlicher Gesamterlös**
- Durchschnitt über alle Use Cases
- **Berechnung:** (UC1 + UC2 + UC3) / 3
- **Wert:** (11.364.535 - 4.769.798 - 4.800.905) / 3 = 597.943 €

**Option 3: Summe aller Use Cases (aktuell)**
- Summe über alle Use Cases
- **Aktuell:** 22.263.463 €
- **❌ Falsch, da Use Cases nicht gleichzeitig betrieben werden können**

---

## 2. Validierung der einzelnen Werte

### 2.1 UC1 Netto-Cashflow: 11.364.535 €

**Berechnung:**
```
Netto-Cashflow = Gesamterlöse (10 Jahre) - Gesamtkosten (10 Jahre) - Investitionskosten
```

**Validierung mit BORBET-Parametern:**
1. **Prüfe Gesamterlöse über 10 Jahre:**
   - Jährliche Erlöse (ohne Degradation): ~1.000.920 €/Jahr
   - Mit Degradation über 10 Jahre: ~9.154.777 €
   - **Erwartet:** ~9.000.000 - 9.500.000 €

2. **Prüfe Gesamtkosten über 10 Jahre:**
   - Jährliche Kosten (ohne Degradation): ~654.340 €/Jahr
   - Mit Degradation über 10 Jahre: ~5.984.829 €
   - **Erwartet:** ~5.800.000 - 6.200.000 €

3. **Prüfe Investitionskosten:**
   - **BORBET:** 13.600.000 € (nicht 6.130.000 €!)

4. **Netto-Cashflow:**
   - **MIT Investition:** 9.154.777 € (Erlöse) - 5.984.829 € (Kosten) - 13.600.000 € (Investition) = **-10.430.052 €**
   - **OHNE Investition:** 9.154.777 € (Erlöse) - 5.984.829 € (Kosten) = **3.169.948 €**
   - **Angezeigt:** 11.364.535 €

**❌ KRITISCHES PROBLEM:** 
- Der angezeigte Wert (11.364.535 €) entspricht **NICHT** dem berechneten Wert
- **Investitionskosten werden NICHT abgezogen!** (Zeile 209 in `enhanced_economic_analysis.py`)

---

### 2.2 UC2 Netto-Cashflow: -4.769.798 €

**Validierung:**
- Negativer Wert ist plausibel (schlechteres Szenario)
- Aber: Warum ist UC2 so viel schlechter als UC1?

---

### 2.3 UC3 Netto-Cashflow: -4.800.905 €

**Validierung:**
- Ähnlich wie UC2 (negativ)
- Plausibel, aber: Warum ist Hybrid schlechter als nur Verbrauch?

---

## 3. Konsistenzprüfung

### 3.1 Summe der Netto-Cashflows

```
UC1: 11.364.535 €
UC2: -4.769.798 €
UC3: -4.800.905 €
Summe: 1.793.832 €
```

**Gesamterlös:** 22.263.463 €

**Problem:** 
- Gesamterlös (22.263.463 €) ≠ Summe der Netto-Cashflows (1.793.832 €)
- **Das ist korrekt**, da Gesamterlös die Summe der Erlöse ist, nicht der Netto-Cashflows

### 3.2 Gesamterlös vs. Netto-Cashflow

**Gesamterlös sollte sein:**
- Summe aller Erlöse über 10 Jahre für alle Use Cases

**Netto-Cashflow sollte sein:**
- Erlöse - Kosten - Investition für jeden Use Case

**Konsistenzprüfung:**
```
Gesamterlös = UC1_Erlöse + UC2_Erlöse + UC3_Erlöse
Netto-Cashflow_UC1 = UC1_Erlöse - UC1_Kosten - Investition
```

**Wenn wir die Werte umstellen:**
```
UC1_Erlöse = Netto-Cashflow_UC1 + UC1_Kosten + Investition
```

**Problem:** Wir kennen UC1_Kosten nicht direkt, können aber schätzen:
- Wenn Netto-Cashflow = 11.364.535 €
- Und Investition = 6.130.000 €
- Dann: UC1_Erlöse - UC1_Kosten = 11.364.535 + 6.130.000 = 17.494.535 €

**Das bedeutet:**
- UC1_Erlöse über 10 Jahre: ~17.494.535 € + UC1_Kosten
- **Das ist sehr hoch!** (ca. 1.750.000 €/Jahr)

---

## 4. Validierungslogik

### 4.1 Erwartete Wertebereiche

**Für Hinterstoder (8 MWh / 2 MW):**

#### Jährliche Erlöse (ohne Degradation):
- SRL: 288 €
- SRE: 20.000 €
- Intraday: 46.138 €
- Day-Ahead: 87.600 €
- Balancing: 80.942 €
- **Gesamt: ~234.968 €/Jahr**

#### Jährliche Kosten (ohne Degradation):
- Betriebskosten: 164 €
- Wartungskosten: 91.950 €
- Netzentgelte: 87.600 €
- Versicherung: 30.650 €
- Degradation: 122.600 €
- **Gesamt: ~332.964 €/Jahr**

#### Netto-Cashflow pro Jahr (ohne Degradation):
- **-97.996 €/Jahr** (negativ!)

#### Über 10 Jahre (mit Degradation):
- **Erlöse:** ~2.100.000 € (ca.)
- **Kosten:** ~3.000.000 € (ca.)
- **Investition:** 6.130.000 €
- **Netto-Cashflow:** ~-7.000.000 € (negativ!)

**❌ Problem:** Die angezeigten Werte (11.364.535 €) passen nicht zu dieser Berechnung!

---

## 5. Mögliche Ursachen

### 5.1 Falsche Summierung

**Problem:** Vielleicht werden die Werte mehrfach summiert?

**Prüfung:**
- Werden die jährlichen Werte korrekt über 10 Jahre summiert?
- Wird die Degradation korrekt angewendet?
- Werden die Investitionskosten korrekt abgezogen?

### 5.2 Falsche Einheiten

**Problem:** Vielleicht werden Einheiten falsch konvertiert?

**Prüfung:**
- Sind alle Preise in der richtigen Einheit (€/kWh, €/MWh, €/MW/h)?
- Werden kW und MW korrekt konvertiert?
- Werden kWh und MWh korrekt konvertiert?

### 5.3 Falsche Marktpreise

**Problem:** Vielleicht werden falsche Marktpreise verwendet?

**Prüfung:**
- Werden die konfigurierten Marktpreise korrekt geladen?
- Werden die Standardwerte korrekt verwendet?
- Werden die Preise in der richtigen Einheit verwendet?

### 5.4 Falsche Degradation

**Problem:** Vielleicht wird die Degradation falsch angewendet?

**Prüfung:**
- Wird die Degradation korrekt auf Erlöse angewendet?
- Wird die Degradation korrekt auf Kosten angewendet?
- Wird die Degradation ab Jahr 2 korrekt angewendet?

---

## 6. Validierungsschritte

### 6.1 Schritt 1: Prüfe jährliche Werte

**Erstelle eine Debug-Ausgabe:**
```python
# Für jedes Jahr ausgeben:
for year in range(1, 11):
    print(f"Jahr {year}:")
    print(f"  Erlöse: {revenue_year}")
    print(f"  Kosten: {costs_year}")
    print(f"  Netto-Cashflow: {net_cashflow_year}")
```

**Erwartete Werte:**
- Jahr 1: Erlöse ~235.000 €, Kosten ~333.000 €, Netto-Cashflow ~-98.000 €
- Jahr 2: Erlöse ~230.000 €, Kosten ~326.000 €, Netto-Cashflow ~-96.000 €
- ...
- Jahr 10: Erlöse ~198.000 €, Kosten ~277.000 €, Netto-Cashflow ~-79.000 €

### 6.2 Schritt 2: Prüfe 10-Jahres-Summe

**Berechne manuell:**
```python
total_revenue_10y = sum(revenue_year for year in range(1, 11))
total_costs_10y = sum(costs_year for year in range(1, 11))
net_cashflow_10y = total_revenue_10y - total_costs_10y - investment_costs
```

**Erwartete Werte:**
- Total Revenue: ~2.100.000 €
- Total Costs: ~3.000.000 €
- Investment: 6.130.000 €
- Netto-Cashflow: ~-7.000.000 €

### 6.3 Schritt 3: Prüfe Marktpreise

**Prüfe geladene Marktpreise:**
```python
print(f"Spot-Arbitrage: {spot_arbitrage_price} €/kWh")
print(f"Intraday-Trading: {intraday_trading_price} €/kWh")
print(f"Balancing Energy: {balancing_energy_price} €/kWh")
```

**Erwartete Werte:**
- Spot-Arbitrage: 0.0074 €/kWh
- Intraday-Trading: 0.0111 €/kWh
- Balancing Energy: 0.0231 €/kWh

### 6.4 Schritt 4: Prüfe Einheiten

**Prüfe BESS-Parameter:**
```python
print(f"BESS-Kapazität: {bess_size_mwh} MWh")
print(f"BESS-Leistung: {bess_power_mw} MW")
print(f"Jahreszyklen: {annual_cycles}")
print(f"Effizienz: {efficiency}")
```

**Erwartete Werte (Hinterstoder):**
- BESS-Kapazität: 8.0 MWh
- BESS-Leistung: 2.0 MW
- Jahreszyklen: 730
- Effizienz: 0.85

---

## 7. Empfohlene Korrekturen

### 7.1 Gesamterlös korrigieren

**Aktuell (falsch):**
```python
'total_revenue': sum(data['annual_balance']['total_revenue'] 
                   for data in analysis_results['use_cases'].values())
```

**Korrektur Option 1: Gesamterlös des besten Use Cases**
```python
best_use_case = max(analysis_results['use_cases'].items(), 
                    key=lambda x: x[1]['annual_balance']['net_cashflow'])
'total_revenue': best_use_case[1]['annual_balance']['total_revenue']
```

**Korrektur Option 2: Gesamterlös entfernen**
- Entferne "Gesamterlös" aus der Anzeige, da Use Cases nicht additiv sind

### 7.2 Validierungslogik hinzufügen

**Erstelle eine Validierungsfunktion:**
```python
def validate_use_case_values(analysis_results, project):
    """Validiert die Use Case Vergleich Werte"""
    
    # Prüfe 1: Netto-Cashflow sollte realistisch sein
    for uc_name, uc_data in analysis_results['use_cases'].items():
        net_cashflow = uc_data['annual_balance']['net_cashflow']
        investment = uc_data['annual_balance']['total_investment']
        
        # Netto-Cashflow sollte nicht größer sein als 2x Investition
        if abs(net_cashflow) > investment * 2:
            print(f"⚠️ WARNUNG: {uc_name} Netto-Cashflow ({net_cashflow:,.0f} €) ist unrealistisch hoch!")
    
    # Prüfe 2: Gesamterlös sollte nicht Summe aller Use Cases sein
    total_revenue = sum(data['annual_balance']['total_revenue'] 
                       for data in analysis_results['use_cases'].values())
    
    if total_revenue > investment * 10:
        print(f"⚠️ WARNUNG: Gesamterlös ({total_revenue:,.0f} €) ist unrealistisch hoch!")
    
    # Prüfe 3: ROI sollte realistisch sein
    for uc_name, uc_data in analysis_results['use_cases'].items():
        roi = uc_data['annual_balance']['cumulative_roi']
        
        # ROI sollte zwischen -100% und 500% sein
        if roi < -100 or roi > 500:
            print(f"⚠️ WARNUNG: {uc_name} ROI ({roi:.1f}%) ist unrealistisch!")
```

---

## 8. Zusammenfassung

### 8.1 Aktuelle Probleme

1. **Gesamterlös ist falsch:** Summiert alle Use Cases, obwohl sie alternativ sind
2. **Netto-Cashflow scheint zu hoch:** 11.364.535 € passt nicht zu erwarteten ~-7.000.000 €
3. **Keine Validierungslogik:** Es gibt keine automatische Prüfung der Werte

### 8.2 Empfohlene Maßnahmen

1. **Gesamterlös korrigieren:** Nur den Erlös des besten Use Cases anzeigen
2. **Validierungslogik hinzufügen:** Automatische Prüfung der Werte
3. **Debug-Ausgabe hinzufügen:** Detaillierte Ausgabe für jedes Jahr
4. **Dokumentation erweitern:** Erkläre, was "Gesamterlös" bedeutet

### 8.3 Nächste Schritte

1. **Prüfe die Berechnung:** Führe die Validierungsschritte durch
2. **Korrigiere die Logik:** Passe die Berechnung an
3. **Teste die Werte:** Prüfe mit bekannten Projektparametern
4. **Dokumentiere:** Erkläre die Berechnung in der Dokumentation

---

**Dokumentation erstellt:** 2025-01-XX  
**Version:** 1.0  
**Status:** ⚠️ Validierung erforderlich

