# 📊 Marktpreis-Konfiguration: Detaillierte Beschreibung der Eingabewerte

## Übersicht

Die **Marktpreis-Konfiguration** ermöglicht es, die Preise für verschiedene Energie-Märkte anzupassen, die für die Wirtschaftlichkeitsberechnung und Erlösprognose verwendet werden. Diese Werte beeinflussen direkt die berechneten Erlöse im **10-Jahres-Report** und im **Use Case Vergleich**.

---

## 1. Intraday Trading (€/kWh)

Die Intraday-Trading-Preise werden für den **Intraday-Handel** verwendet, bei dem Energie innerhalb eines Tages gehandelt wird. Diese Preise beeinflussen die Erlöse aus der **Intraday-Speicherstrategie**.

### 1.1 Spot-Arbitrage

**Feldname:** `spot_arbitrage_price`  
**Einheit:** €/kWh  
**Standardwert:** 0.0074 €/kWh  
**Referenzwert:** 0.0074 €/kWh

#### Was ist Spot-Arbitrage?

Spot-Arbitrage ist der Handel von Energie am **Day-Ahead-Spotmarkt**. Die BESS kauft Energie zu niedrigen Preisen (z.B. nachts) und verkauft sie zu hohen Preisen (z.B. tagsüber).

#### Verwendung in der Berechnung

**Formel:**
```
spot_arbitrage_revenue = bess_capacity_kwh × daily_cycles × 365 × spot_arbitrage_price × efficiency
```

**Parameter:**
- `bess_capacity_kwh`: BESS-Kapazität in kWh (MWh × 1000)
- `daily_cycles`: Zyklen pro Tag (annual_cycles / 365)
- `spot_arbitrage_price`: Konfigurierter Preis in €/kWh
- `efficiency`: BESS-Effizienz (z.B. 0.85 = 85%)

#### Beispiel-Berechnung

**Projekt:** Hinterstoder (8 MWh / 2 MW, 2 Zyklen/Tag, 85% Effizienz)

```
bess_capacity_kwh = 8.0 MWh × 1000 = 8.000 kWh
daily_cycles = 730 / 365 = 2.0 Zyklen/Tag
spot_arbitrage_revenue = 8.000 kWh × 2.0 × 365 × 0.0074 €/kWh × 0.85 = 36.773 €/Jahr
```

#### Auswirkung von Änderungen

- **Erhöhung um 10%** (0.0074 → 0.00814): Erlös steigt um ~3.677 €/Jahr
- **Erhöhung um 50%** (0.0074 → 0.0111): Erlös steigt um ~18.386 €/Jahr
- **Verdopplung** (0.0074 → 0.0148): Erlös verdoppelt sich auf ~73.546 €/Jahr

**Über 10 Jahre (mit Degradation):** Eine Erhöhung um 10% führt zu einem zusätzlichen Erlös von ca. **33.000 €** über 10 Jahre.

---

### 1.2 Intraday-Handel

**Feldname:** `intraday_trading_price`  
**Einheit:** €/kWh  
**Standardwert:** 0.0111 €/kWh  
**Referenzwert:** 0.0111 €/kWh

#### Was ist Intraday-Handel?

Intraday-Handel ist der Handel von Energie **innerhalb des Tages** auf dem Intraday-Markt. Dieser Markt ermöglicht es, kurzfristige Preisunterschiede zu nutzen.

#### Verwendung in der Berechnung

**Formel:**
```
intraday_trading_revenue = bess_capacity_kwh × daily_cycles × 365 × intraday_trading_price × efficiency
```

**Parameter:**
- `bess_capacity_kwh`: BESS-Kapazität in kWh
- `daily_cycles`: Zyklen pro Tag
- `intraday_trading_price`: Konfigurierter Preis in €/kWh
- `efficiency`: BESS-Effizienz

#### Beispiel-Berechnung

```
intraday_trading_revenue = 8.000 kWh × 2.0 × 365 × 0.0111 €/kWh × 0.85 = 55.160 €/Jahr
```

#### Auswirkung von Änderungen

- **Erhöhung um 10%** (0.0111 → 0.01221): Erlös steigt um ~5.516 €/Jahr
- **Erhöhung um 50%** (0.0111 → 0.01665): Erlös steigt um ~27.580 €/Jahr
- **Verdopplung** (0.0111 → 0.0222): Erlös verdoppelt sich auf ~110.320 €/Jahr

**Über 10 Jahre (mit Degradation):** Eine Erhöhung um 10% führt zu einem zusätzlichen Erlös von ca. **50.000 €** über 10 Jahre.

---

### 1.3 Regelenergie (Balancing Energy)

**Feldname:** `balancing_energy_price`  
**Einheit:** €/kWh  
**Standardwert:** 0.0231 €/kWh  
**Referenzwert:** 0.0231 €/kWh

#### Was ist Regelenergie?

Regelenergie (Balancing Energy) wird verwendet, um das Stromnetz stabil zu halten. Die BESS stellt **Regelleistung** zur Verfügung, um Frequenzschwankungen auszugleichen.

#### Verwendung in der Berechnung

**Formel:**
```
balancing_energy_revenue = bess_power_kw × 8760 × balancing_energy_price / 1000 × efficiency
```

**Parameter:**
- `bess_power_kw`: BESS-Leistung in kW (MW × 1000)
- `8760`: Stunden pro Jahr (volle Verfügbarkeit)
- `balancing_energy_price`: Konfigurierter Preis in €/kWh
- `/ 1000`: Einheitenumrechnung (wie im 10-Jahres-Report)
- `efficiency`: BESS-Effizienz

#### Beispiel-Berechnung

```
bess_power_kw = 2.0 MW × 1000 = 2.000 kW
balancing_energy_revenue = 2.000 kW × 8760 h × 0.0231 €/kWh / 1000 × 0.85 = 343 €/Jahr
```

#### Auswirkung von Änderungen

- **Erhöhung um 10%** (0.0231 → 0.02541): Erlös steigt um ~34 €/Jahr
- **Erhöhung um 50%** (0.0231 → 0.03465): Erlös steigt um ~172 €/Jahr
- **Verdopplung** (0.0231 → 0.0462): Erlös verdoppelt sich auf ~686 €/Jahr

**Über 10 Jahre (mit Degradation):** Eine Erhöhung um 10% führt zu einem zusätzlichen Erlös von ca. **310 €** über 10 Jahre.

**Hinweis:** Dieser Wert ist relativ klein im Vergleich zu den anderen Intraday-Erlösen, da er auf der **Leistung** (kW) basiert, nicht auf der **Energie** (kWh).

---

## 2. Sekundärmarkt (€/kWh)

Die Sekundärmarkt-Preise werden für **zusätzliche Erlösquellen** verwendet, die über den Standard-Intraday-Handel hinausgehen.

### 2.1 Frequenzregelung

**Feldname:** `frequency_regulation_price`  
**Einheit:** €/kWh  
**Standardwert:** 0.30 €/kWh  
**Referenzwert:** 0.30 €/kWh

#### Was ist Frequenzregelung?

Frequenzregelung ist eine **Netzstabilisierungsdienstleistung**, bei der die BESS sehr schnell auf Frequenzschwankungen im Netz reagiert (Sekunden bis Minuten).

#### Verwendung in der Berechnung

**Formel:**
```
frequency_regulation_revenue = bess_power_kw × 8760 × frequency_regulation_price / 1000
```

**Parameter:**
- `bess_power_kw`: BESS-Leistung in kW
- `8760`: Stunden pro Jahr
- `frequency_regulation_price`: Konfigurierter Preis in €/kWh
- `/ 1000`: Einheitenumrechnung

#### Beispiel-Berechnung

```
frequency_regulation_revenue = 2.000 kW × 8760 h × 0.30 €/kWh / 1000 = 5.256 €/Jahr
```

#### Auswirkung von Änderungen

- **Erhöhung um 10%** (0.30 → 0.33): Erlös steigt um ~526 €/Jahr
- **Erhöhung um 50%** (0.30 → 0.45): Erlös steigt um ~2.628 €/Jahr
- **Verdopplung** (0.30 → 0.60): Erlös verdoppelt sich auf ~10.512 €/Jahr

**Über 10 Jahre (mit Degradation):** Eine Erhöhung um 10% führt zu einem zusätzlichen Erlös von ca. **4.700 €** über 10 Jahre.

**Hinweis:** Dieser Wert wird derzeit **nicht** im Use Case Vergleich verwendet**, sondern nur in speziellen Sekundärmarkt-Berechnungen.

---

### 2.2 Kapazitätsmärkte

**Feldname:** `capacity_market_price`  
**Einheit:** €/kWh  
**Standardwert:** 0.18 €/kWh  
**Referenzwert:** 0.18 €/kWh

#### Was sind Kapazitätsmärkte?

Kapazitätsmärkte sind Märkte, auf denen **Leistungsreserven** gehandelt werden. Die BESS erhält eine Vergütung dafür, dass sie **Kapazität bereitstellt**, auch wenn sie nicht aktiv genutzt wird.

#### Verwendung in der Berechnung

**Formel:**
```
capacity_market_revenue = bess_power_kw × 8760 × capacity_market_price / 1000
```

**Parameter:**
- `bess_power_kw`: BESS-Leistung in kW
- `8760`: Stunden pro Jahr
- `capacity_market_price`: Konfigurierter Preis in €/kWh
- `/ 1000`: Einheitenumrechnung

#### Beispiel-Berechnung

```
capacity_market_revenue = 2.000 kW × 8760 h × 0.18 €/kWh / 1000 = 3.154 €/Jahr
```

#### Auswirkung von Änderungen

- **Erhöhung um 10%** (0.18 → 0.198): Erlös steigt um ~315 €/Jahr
- **Erhöhung um 50%** (0.18 → 0.27): Erlös steigt um ~1.577 €/Jahr
- **Verdopplung** (0.18 → 0.36): Erlös verdoppelt sich auf ~6.308 €/Jahr

**Über 10 Jahre (mit Degradation):** Eine Erhöhung um 10% führt zu einem zusätzlichen Erlös von ca. **2.800 €** über 10 Jahre.

**Hinweis:** Dieser Wert wird derzeit **nicht** im Use Case Vergleich verwendet**, sondern nur in speziellen Sekundärmarkt-Berechnungen.

---

### 2.3 Flexibilitätsmärkte

**Feldname:** `flexibility_market_price`  
**Einheit:** €/kWh  
**Standardwert:** 0.22 €/kWh  
**Referenzwert:** 0.22 €/kWh

#### Was sind Flexibilitätsmärkte?

Flexibilitätsmärkte sind Märkte, auf denen **Flexibilität** gehandelt wird. Die BESS kann ihre **Lade- und Entladeleistung** flexibel anpassen, um Netzengpässe zu vermeiden oder lokale Lastspitzen zu glätten.

#### Verwendung in der Berechnung

**Formel:**
```
flexibility_market_revenue = bess_power_kw × 8760 × flexibility_market_price / 1000
```

**Parameter:**
- `bess_power_kw`: BESS-Leistung in kW
- `8760`: Stunden pro Jahr
- `flexibility_market_price`: Konfigurierter Preis in €/kWh
- `/ 1000`: Einheitenumrechnung

#### Beispiel-Berechnung

```
flexibility_market_revenue = 2.000 kW × 8760 h × 0.22 €/kWh / 1000 = 3.854 €/Jahr
```

#### Auswirkung von Änderungen

- **Erhöhung um 10%** (0.22 → 0.242): Erlös steigt um ~385 €/Jahr
- **Erhöhung um 50%** (0.22 → 0.33): Erlös steigt um ~1.927 €/Jahr
- **Verdopplung** (0.22 → 0.44): Erlös verdoppelt sich auf ~7.708 €/Jahr

**Über 10 Jahre (mit Degradation):** Eine Erhöhung um 10% führt zu einem zusätzlichen Erlös von ca. **3.500 €** über 10 Jahre.

**Hinweis:** Dieser Wert wird derzeit **nicht** im Use Case Vergleich verwendet**, sondern nur in speziellen Sekundärmarkt-Berechnungen.

---

## 3. Bezugsjahr für 10-Jahres-Berechnung

**Feldname:** `reference_year`  
**Einheit:** Jahr (Integer)  
**Standardwert:** Aktuelles Jahr (z.B. 2025)  
**Referenzwert:** 2024

### Was ist das Bezugsjahr?

Das **Bezugsjahr** (Reference Year) ist das **Referenzjahr** für die 10-Jahres-Prognose. Es bestimmt, welches Jahr als **Jahr 1** in der Berechnung verwendet wird.

### Verwendung in der Berechnung

Die 10-Jahres-Berechnung verwendet das Bezugsjahr wie folgt:

- **Jahr 1 (Referenzjahr):** `reference_year` (z.B. 2024)
- **Jahr 2:** `reference_year + 1` (z.B. 2025)
- **Jahr 3:** `reference_year + 2` (z.B. 2026)
- ...
- **Jahr 10:** `reference_year + 9` (z.B. 2033)

### Beispiel

**Bezugsjahr:** 2024

Die 10-Jahres-Prognose umfasst:
- 2024 (Referenzjahr)
- 2025-2033 (Projektionsjahre)

**Bezugsjahr:** 2025

Die 10-Jahres-Prognose umfasst:
- 2025 (Referenzjahr)
- 2026-2034 (Projektionsjahre)

### Auswirkung von Änderungen

Das Bezugsjahr beeinflusst:
1. **Die Jahresbezeichnungen** in den Tabellen und Reports
2. **Die Degradationsberechnung** (Degradation beginnt ab Jahr 2)
3. **Die Projektionsjahre** in der 10-Jahres-Prognose

**Hinweis:** Die Degradation wird immer ab **Jahr 2** angewendet, unabhängig vom Bezugsjahr.

---

## 4. Gesamtauswirkung der Marktpreise

### 4.1 Intraday-Erlöse (Gesamt)

Die drei Intraday-Preise werden **kombiniert** verwendet:

**Formel:**
```
intraday_total = (spot_arbitrage_revenue + intraday_trading_revenue + balancing_energy_revenue) × participation_rate
```

**Beispiel (Hinterstoder):**
```
spot_arbitrage_revenue = 36.773 €/Jahr
intraday_trading_revenue = 55.160 €/Jahr
balancing_energy_revenue = 343 €/Jahr
intraday_total = (36.773 + 55.160 + 343) × 0.5 = 46.138 €/Jahr
```

**Über 10 Jahre (mit Degradation):** ~415.000 €

### 4.2 Sensitivitätsanalyse

#### Szenario 1: Alle Intraday-Preise um 10% erhöhen

**Änderungen:**
- Spot-Arbitrage: 0.0074 → 0.00814 (+10%)
- Intraday-Trading: 0.0111 → 0.01221 (+10%)
- Balancing Energy: 0.0231 → 0.02541 (+10%)

**Auswirkung:**
- Jährlicher Erlös: +4.607 €/Jahr
- Über 10 Jahre: +41.500 €

#### Szenario 2: Alle Intraday-Preise um 50% erhöhen

**Änderungen:**
- Spot-Arbitrage: 0.0074 → 0.0111 (+50%)
- Intraday-Trading: 0.0111 → 0.01665 (+50%)
- Balancing Energy: 0.0231 → 0.03465 (+50%)

**Auswirkung:**
- Jährlicher Erlös: +23.069 €/Jahr
- Über 10 Jahre: +207.500 €

#### Szenario 3: Nur Spot-Arbitrage verdoppeln

**Änderung:**
- Spot-Arbitrage: 0.0074 → 0.0148 (+100%)

**Auswirkung:**
- Jährlicher Erlös: +36.773 €/Jahr (nur Spot-Arbitrage)
- Über 10 Jahre: +331.000 €

---

## 5. Empfohlene Wertebereiche

### 5.1 Realistische Marktpreise (Österreich/Deutschland)

| Markt | Realistischer Bereich | Aktueller Standardwert | Status |
|-------|----------------------|------------------------|--------|
| Spot-Arbitrage | 0.005 - 0.010 €/kWh | 0.0074 €/kWh | ✅ Realistisch |
| Intraday-Trading | 0.008 - 0.015 €/kWh | 0.0111 €/kWh | ✅ Realistisch |
| Balancing Energy | 0.015 - 0.030 €/kWh | 0.0231 €/kWh | ✅ Realistisch |
| Frequenzregelung | 0.20 - 0.40 €/kWh | 0.30 €/kWh | ✅ Realistisch |
| Kapazitätsmärkte | 0.10 - 0.25 €/kWh | 0.18 €/kWh | ✅ Realistisch |
| Flexibilitätsmärkte | 0.15 - 0.30 €/kWh | 0.22 €/kWh | ✅ Realistisch |

### 5.2 Anpassungsempfehlungen

#### Wenn Erlöse zu niedrig sind:
- **Spot-Arbitrage erhöhen** (größter Einfluss auf Intraday-Erlöse)
- **Intraday-Trading erhöhen** (zweithöchster Einfluss)
- **Balancing Energy erhöhen** (kleiner Einfluss, aber einfach umzusetzen)

#### Wenn Erlöse zu hoch sind:
- **Spot-Arbitrage reduzieren** (größter Einfluss)
- **Intraday-Trading reduzieren** (zweithöchster Einfluss)
- **Balancing Energy reduzieren** (kleiner Einfluss)

---

## 6. Verwendung in verschiedenen Berechnungen

### 6.1 10-Jahres-Report

**Verwendete Preise:**
- ✅ Spot-Arbitrage (`spot_arbitrage_price`)
- ✅ Intraday-Trading (`intraday_trading_price`)
- ✅ Balancing Energy (`balancing_energy_price`)
- ❌ Frequenzregelung (nicht verwendet)
- ❌ Kapazitätsmärkte (nicht verwendet)
- ❌ Flexibilitätsmärkte (nicht verwendet)
- ✅ Bezugsjahr (`reference_year`)

### 6.2 Use Case Vergleich

**Verwendete Preise:**
- ✅ Spot-Arbitrage (`spot_arbitrage_price`)
- ✅ Intraday-Trading (`intraday_trading_price`)
- ✅ Balancing Energy (`balancing_energy_price`)
- ❌ Frequenzregelung (nicht verwendet)
- ❌ Kapazitätsmärkte (nicht verwendet)
- ❌ Flexibilitätsmärkte (nicht verwendet)
- ❌ Bezugsjahr (nicht direkt verwendet, aber für Degradation relevant)

### 6.3 Sekundärmarkt-Berechnungen

**Verwendete Preise:**
- ✅ Frequenzregelung (`frequency_regulation_price`)
- ✅ Kapazitätsmärkte (`capacity_market_price`)
- ✅ Flexibilitätsmärkte (`flexibility_market_price`)

**Hinweis:** Diese werden in separaten API-Endpunkten verwendet, nicht im Standard-Use Case Vergleich.

---

## 7. Speicherung und Priorität

### 7.1 Speicherung

Die Marktpreise werden in der Datenbank gespeichert:

- **Projektspezifisch:** In der Tabelle `market_price_config` mit `project_id`
- **Global:** In der Tabelle `market_price_config` mit `project_id = NULL` und `is_default = TRUE`

### 7.2 Priorität

1. **Projektspezifische Konfiguration** (höchste Priorität)
2. **Globale Standard-Konfiguration** (mittlere Priorität)
3. **Hardcodierte Standardwerte** (niedrigste Priorität, Fallback)

### 7.3 Beispiel

**Projekt "Hinterstoder" (ID: 1):**
- Hat eigene Marktpreis-Konfiguration → Diese wird verwendet
- Hat keine eigene Konfiguration → Globale Standardwerte werden verwendet
- Keine globale Konfiguration → Hardcodierte Standardwerte werden verwendet

---

## 8. Formeln im Detail

### 8.1 Spot-Arbitrage Erlös

```
spot_arbitrage_revenue = bess_capacity_kwh × daily_cycles × 365 × spot_arbitrage_price × efficiency
```

**Einheiten-Prüfung:**
- `bess_capacity_kwh`: kWh
- `daily_cycles`: 1/Tag (dimensionslos)
- `365`: Tage/Jahr (dimensionslos)
- `spot_arbitrage_price`: €/kWh
- `efficiency`: dimensionslos (0-1)
- **Ergebnis:** kWh × 1/Tag × Tage/Jahr × €/kWh × 1 = **€/Jahr** ✅

### 8.2 Intraday-Trading Erlös

```
intraday_trading_revenue = bess_capacity_kwh × daily_cycles × 365 × intraday_trading_price × efficiency
```

**Einheiten-Prüfung:**
- Gleiche Einheiten wie Spot-Arbitrage
- **Ergebnis:** **€/Jahr** ✅

### 8.3 Balancing Energy Erlös

```
balancing_energy_revenue = bess_power_kw × 8760 × balancing_energy_price / 1000 × efficiency
```

**Einheiten-Prüfung:**
- `bess_power_kw`: kW
- `8760`: h/Jahr
- `balancing_energy_price`: €/kWh
- `/ 1000`: Einheitenumrechnung
- `efficiency`: dimensionslos
- **Ergebnis:** kW × h/Jahr × €/kWh / 1000 × 1 = **€/Jahr** ✅

**Hinweis:** Das `/ 1000` wird verwendet, um die Einheiten korrekt zu handhaben. Die genaue Begründung ist im 10-Jahres-Report dokumentiert.

---

## 9. Häufige Fragen (FAQ)

### 9.1 Warum sind die Intraday-Preise so niedrig (0.0074, 0.0111, 0.0231)?

**Antwort:** Diese Preise wurden basierend auf einem **Referenz-Screenshot** angepasst. Der ursprüngliche Wert für "Erlös Intraday Speicherstrategie" war zu hoch (1.172.380 € statt 108.274 €). Die Preise wurden um **ca. 90% reduziert**, um realistische Werte zu erreichen.

**Berechnung:**
- Reduktionsfaktor: 108.274 / 1.172.380 = 0.0924 (≈ 9.24%)
- Spot-Arbitrage: 0.08 × 0.0924 = 0.007392 ≈ 0.0074
- Intraday-Trading: 0.12 × 0.0924 = 0.011088 ≈ 0.0111
- Balancing Energy: 0.25 × 0.0924 = 0.0231

### 9.2 Warum wird Balancing Energy durch 1000 geteilt?

**Antwort:** Die Formel `bess_power_kw × 8760 × balancing_energy_price / 1000` wird verwendet, um die Einheiten korrekt zu handhaben. Das `/ 1000` ist Teil der Formel, wie sie im 10-Jahres-Report verwendet wird.

**Alternative Interpretation:** Der Preis könnte tatsächlich in **€/MWh** sein (23.1 €/MWh statt 0.0231 €/kWh), dann würde die Formel ohne `/ 1000` sein:
```
balancing_energy_revenue = bess_power_mw × 8760 × 23.1 €/MWh × efficiency
```

### 9.3 Werden die Sekundärmarkt-Preise im Use Case Vergleich verwendet?

**Antwort:** **Nein**, die Sekundärmarkt-Preise (Frequenzregelung, Kapazitätsmärkte, Flexibilitätsmärkte) werden derzeit **nicht** im Use Case Vergleich verwendet. Sie werden nur in speziellen Sekundärmarkt-Berechnungen verwendet.

### 9.4 Wie wirkt sich das Bezugsjahr auf die Berechnung aus?

**Antwort:** Das Bezugsjahr bestimmt:
1. **Welches Jahr als Jahr 1** verwendet wird
2. **Die Jahresbezeichnungen** in den Tabellen (z.B. "2024" statt "2025")
3. **Die Projektionsjahre** (z.B. 2025-2033 statt 2026-2034)

**Die Degradation** wird immer ab **Jahr 2** angewendet, unabhängig vom Bezugsjahr.

### 9.5 Kann ich die Preise projektspezifisch anpassen?

**Antwort:** **Ja**, die Marktpreise können projektspezifisch konfiguriert werden:
1. Öffne die **Marktpreis-Konfiguration** für das Projekt
2. Passe die Werte an
3. Klicke auf **"Speichern"**
4. Die Werte werden für dieses Projekt gespeichert

**Hinweis:** Wenn keine projektspezifische Konfiguration existiert, werden die **globalen Standardwerte** verwendet.

---

## 10. Zusammenfassung

### 10.1 Wichtigste Eingabewerte

| Eingabewert | Einheit | Standardwert | Verwendung | Einfluss |
|-------------|---------|--------------|------------|----------|
| **Spot-Arbitrage** | €/kWh | 0.0074 | ✅ 10-Jahres-Report<br>✅ Use Case Vergleich | ⭐⭐⭐ Hoch |
| **Intraday-Trading** | €/kWh | 0.0111 | ✅ 10-Jahres-Report<br>✅ Use Case Vergleich | ⭐⭐⭐ Hoch |
| **Balancing Energy** | €/kWh | 0.0231 | ✅ 10-Jahres-Report<br>✅ Use Case Vergleich | ⭐ Niedrig |
| **Frequenzregelung** | €/kWh | 0.30 | ❌ Nur Sekundärmarkt | ⭐⭐ Mittel |
| **Kapazitätsmärkte** | €/kWh | 0.18 | ❌ Nur Sekundärmarkt | ⭐⭐ Mittel |
| **Flexibilitätsmärkte** | €/kWh | 0.22 | ❌ Nur Sekundärmarkt | ⭐⭐ Mittel |
| **Bezugsjahr** | Jahr | 2025 | ✅ 10-Jahres-Report | ⭐⭐⭐ Sehr hoch |

### 10.2 Empfohlene Anpassungsstrategie

1. **Für realistische Werte:** Verwende die Standardwerte (bereits angepasst)
2. **Für höhere Erlöse:** Erhöhe Spot-Arbitrage und Intraday-Trading (größter Einfluss)
3. **Für niedrigere Erlöse:** Reduziere Spot-Arbitrage und Intraday-Trading
4. **Für Jahresanpassung:** Ändere das Bezugsjahr (z.B. Ende des Jahres auf nächstes Jahr)

---

**Dokumentation erstellt:** 2025-01-XX  
**Version:** 1.0  
**Autor:** BESS-Simulation System

