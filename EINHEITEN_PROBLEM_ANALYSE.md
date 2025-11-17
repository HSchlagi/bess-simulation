# KRITISCHES PROBLEM: Einheiten-Verwechslung bei SRL-Berechnung

## Problem-Identifikation

Der Netto-Cashflow von **248.201.104 €** ist unrealistisch hoch. Nach Analyse der Berechnung:

### SRL-Berechnung (Sekundärregelleistung)

**Aktuelle Formel:**
```python
srl_positive = bess_power_mw * hours_per_year * positive_price * participation_rate
```

**Parameter:**
- `bess_power_mw`: 2.0 MW (korrekt konvertiert von 2000 kW)
- `hours_per_year`: 8000 Stunden
- `positive_price`: 18.0 (laut Kommentar: €/MW/h)
- `participation_rate`: 0.5

**Berechnung:**
- 2.0 MW * 8000 h * 18.0 €/MW/h * 0.5 = **144.000 € pro Jahr**

**Über 10 Jahre (mit Degradation):**
- Jahr 1: 144.000 €
- Jahr 2: 144.000 * 0.98 = 141.120 €
- Jahr 3: 144.000 * 0.9604 = 138.298 €
- ...
- Summe über 10 Jahre: ~1.300.000 €

**ABER:** Wenn der Preis tatsächlich in **€/kW/h** ist (nicht €/MW/h), dann:
- 2.0 MW = 2000 kW
- 2000 kW * 8000 h * 18.0 €/kW/h * 0.5 = **144.000.000 € pro Jahr** ❌ (1000x zu hoch!)

**Über 10 Jahre:**
- Summe: ~1.300.000.000 € (über 1 Milliarde!)

## Mögliche Ursachen

### 1. Preis-Einheit falsch deklariert
- Kommentar sagt: "18.0 €/MW/h"
- Tatsächlich könnte es sein: "18.0 €/kW/h"
- **Lösung:** Preis durch 1000 teilen oder Einheit korrigieren

### 2. BESS-Power nicht korrekt konvertiert
- Wenn `bess_power_mw` tatsächlich in kW gespeichert ist (z.B. 2000 statt 2.0)
- Dann: 2000 * 8000 * 18.0 * 0.5 = 144.000.000 € ❌

### 3. Mehrfache Summierung
- Werte werden über 10 Jahre summiert ✅ (korrekt)
- Aber vielleicht werden sie zusätzlich nochmal summiert?

## Empfohlene Korrektur

### Option 1: Preis-Einheit korrigieren
Wenn der Preis tatsächlich in €/kW/h ist:
```python
# Preis von €/kW/h zu €/MW/h konvertieren
srl_price_mw = srl_price_kw / 1000  # 18.0 / 1000 = 0.018 €/MW/h
```

### Option 2: BESS-Power prüfen
Stelle sicher, dass `bess_power_mw` wirklich in MW ist:
```python
# Prüfe, ob bess_power > 100 (dann ist es wahrscheinlich in kW)
if bess_power > 100:
    bess_power_mw = bess_power / 1000
else:
    bess_power_mw = bess_power
```

### Option 3: Vergleich mit 10-Jahres-Report
Prüfe, welche Werte im 10-Jahres-Report für SRL verwendet werden und verwende die gleiche Formel.

## Nächste Schritte

1. **Prüfe 10-Jahres-Report:** Welche SRL-Erlöse werden dort angezeigt?
2. **Prüfe Datenbank:** Welche Einheit hat `project.bess_power` tatsächlich?
3. **Prüfe Marktpreise:** Welche Einheit haben die SRL-Preise wirklich?
4. **Korrigiere:** Passe die Formel entsprechend an

