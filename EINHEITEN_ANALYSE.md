# Einheiten-Analyse: MW/kW Verwechslung

## Problem-Identifikation

Der Netto-Cashflow von **248.169.640 €** ist unrealistisch hoch. Mögliche Ursache: **Einheitenverwechslung zwischen MW und kW**.

## Kritische Berechnungen

### 1. SRL-Berechnung (Sekundärregelleistung)

**In `enhanced_economic_analysis.py` (Zeile 262-263):**
```python
srl_positive = bess_power_mw * hours_per_year * positive_price * participation_rate
```

**Parameter:**
- `bess_power_mw`: in **MW** (z.B. 2.0 MW)
- `hours_per_year`: 8000 Stunden
- `positive_price`: 18.0 **€/MW/h** (laut Kommentar Zeile 322)
- Ergebnis: MW * h * €/MW/h = **€** ✅ (korrekt)

**ABER:** In `app/routes.py` (Zeile 5714-5717):
```python
srl_negative_revenue = bess_power_mw * availability_hours * srl_negative_price * srl_negative_ratio * degradation_factor
srl_positive_revenue = bess_power_mw * availability_hours * srl_positive_price * srl_positive_ratio * degradation_factor
```

**Preise:**
- `srl_negative_price = 18.0` **€/MW/h** (Zeile 5694)
- `srl_positive_price = 18.0` **€/MW/h** (Zeile 5695)

**Problem:** Wenn `bess_power_mw` tatsächlich in **kW** gespeichert ist (z.B. 2000 kW statt 2.0 MW), dann:
- 2000 kW * 8000 h * 18.0 €/MW/h = 2000 * 8000 * 18.0 = **288.000.000 €** ❌ (1000x zu hoch!)

### 2. Balancing Energy Berechnung

**In `app/routes.py` (Zeile 5733):**
```python
balancing_energy_revenue = bess_power_kw * 8760 * prices['balancing_energy_price'] / 1000 * degradation_factor
```

**Parameter:**
- `bess_power_kw`: in **kW** (z.B. 2000 kW)
- `prices['balancing_energy_price']`: 0.0231 (laut Zeile 5563: **€/kWh**)
- `* 8760` Stunden
- `/ 1000` - **WARUM?**

**Einheiten-Analyse:**
- Wenn Preis in **€/kWh**: kW * h * €/kWh = € (kein /1000 nötig!) ❌
- Wenn Preis in **€/MWh**: kW * h * €/MWh / 1000 = MW * h * €/MWh = € ✅

**Problem:** Der Preis wird als "€/kWh" deklariert, aber das `/ 1000` deutet darauf hin, dass er tatsächlich in **€/MWh** ist!

**Korrektur:**
- Wenn Preis in €/MWh: `balancing_energy_revenue = bess_power_kw / 1000 * 8760 * prices['balancing_energy_price'] * degradation_factor`
- Oder: `balancing_energy_revenue = bess_power_mw * 8760 * prices['balancing_energy_price'] * degradation_factor`

**In `enhanced_economic_analysis.py` (Zeile 273-276):**
```python
def calculate_balancing_revenue(bess_power_mw: float, hours_per_year: int,
                              balancing_price: float, participation_rate: float = 0.6) -> float:
    return bess_power_mw * hours_per_year * balancing_price * participation_rate
```

**Parameter:**
- `bess_power_mw`: in **MW**
- `balancing_price`: sollte in **€/MW/h** oder **€/MWh** sein
- Ergebnis: MW * h * €/MW/h = € ✅

**ABER:** In Zeile 329 wird `balancing` als `db_prices.get('balancing_energy_price', 0.0231) * 1000` gesetzt (also **23.1 €/MWh**).

### 3. Intraday-Berechnung

**In `enhanced_economic_analysis.py` (Zeile 567-572):**
```python
bess_capacity_kwh = use_case.bess_size_mwh * 1000  # ✅ Korrekt: MWh zu kWh
spot_arbitrage_price = db_prices.get('spot_arbitrage_price', 0.0074)  # €/kWh
spot_arbitrage_revenue = bess_capacity_kwh * daily_cycles * 365 * spot_arbitrage_price * use_case.efficiency
```

**Einheiten:**
- `bess_capacity_kwh`: in **kWh** ✅
- `spot_arbitrage_price`: 0.0074 **€/kWh** ✅
- `daily_cycles`: Zyklen/Tag (dimensionslos)
- `365`: Tage/Jahr (dimensionslos)
- Ergebnis: kWh * Zyklen * Tage * €/kWh = **€** ✅ (korrekt)

## Zusammenfassung der Probleme

### Problem 1: BESS-Power Einheit inkonsistent
- In der Datenbank: `project.bess_power` könnte in **kW** gespeichert sein
- Im Code: wird manchmal als **MW** behandelt (z.B. `bess_power_mw`)
- **Lösung:** Prüfen, ob `project.bess_power` in kW oder MW gespeichert ist

### Problem 2: Balancing Energy Preis-Einheit
- Deklariert als: **€/kWh** (0.0231)
- Verwendet mit: `/ 1000` (deutet auf **€/MWh** hin)
- **Lösung:** Einheit klarstellen und Formel anpassen

### Problem 3: SRL-Preis Einheit
- Deklariert als: **€/MW/h** (18.0)
- Wenn `bess_power_mw` tatsächlich in **kW** ist, wird das Ergebnis 1000x zu hoch

## Empfohlene Korrekturen

### 1. Prüfe Datenbank-Einheiten
```python
# Prüfe, ob project.bess_power in kW oder MW gespeichert ist
# Wenn in kW: bess_power_mw = project.bess_power / 1000
# Wenn in MW: bess_power_mw = project.bess_power
```

### 2. Korrigiere Balancing Energy Berechnung
```python
# Option A: Preis in €/MWh (23.1 statt 0.0231)
balancing_energy_price_mwh = prices['balancing_energy_price'] * 1000  # 0.0231 -> 23.1 €/MWh
balancing_energy_revenue = bess_power_kw / 1000 * 8760 * balancing_energy_price_mwh * degradation_factor

# Option B: Preis in €/kWh (0.0231), dann kein /1000
balancing_energy_revenue = bess_power_kw * 8760 * prices['balancing_energy_price'] * degradation_factor
```

### 3. Korrigiere SRL-Berechnung
```python
# Stelle sicher, dass bess_power_mw wirklich in MW ist
if project.bess_power > 100:  # Wahrscheinlich in kW
    bess_power_mw = project.bess_power / 1000
else:
    bess_power_mw = project.bess_power
```

## Nächste Schritte

1. **Prüfe Datenbank:** Welche Einheit hat `project.bess_power`?
2. **Prüfe 10-Jahres-Report:** Welche Werte werden dort verwendet?
3. **Vergleiche:** Use Case Vergleich mit 10-Jahres-Report
4. **Korrigiere:** Einheiten konsistent machen

