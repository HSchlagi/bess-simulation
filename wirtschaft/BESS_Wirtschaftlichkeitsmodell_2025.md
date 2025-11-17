# 📊 Wirtschaftlichkeitsbewertung von Batteriespeichern (BESS) – Multi-Use Ansatz 2025

## 1️⃣ Ziel der Berechnung
Ermittlung der jährlichen Erlöse und Renditen (IRR / ROI) für BESS-Projekte unter Berücksichtigung aller relevanten Märkte:  
- Arbitrage (Spotmarkt)
- Regelenergiemarkt (aFRR, mFRR, FCR)
- Netzdienstleistungen (Redispatch 2.0)
- Eigenverbrauch & Peak-Shaving
- PPA-Glättung & Flexibilitätsmärkte

---

## 2️⃣ Basisparameter

| Parameter | Symbol | Beispielwert | Einheit | Beschreibung |
|------------|---------|---------------|----------|--------------|
| Nennleistung | P_nom | 1 | MW | Max. Lade-/Entladeleistung |
| Kapazität | E_nom | 2 | MWh | Energieinhalt |
| C-Rate | C | 0.5 | – | Entladezeit 2 h |
| Wirkungsgrad (Round-Trip) | η | 0.9 | – | Lade-/Entladeverluste |
| Verfügbarkeit | Av | 0.95 | – | Wartung & Steuerung |
| Investkosten | CAPEX | 650 000 | €/MWh | Batteriesystem, PCS, EMS, Montage |
| Betriebskosten | OPEX | 2 % | vom CAPEX | Wartung, IT, Kommunikation |
| Lebensdauer | t | 10 | Jahre | Wirtschaftliche Nutzungsdauer |

---

## 3️⃣ Erlösströme

### 3.1 Arbitrage (Spotmarkt)
\[
R_{arb} = Spread × η × Zyklen_{a} × E_{nom}
\]
- Spread: 40 – 70 €/MWh  
- Zyklen: 300 – 350 /a  
→ **Ertrag:** 10 000 – 25 000 €/MWh·a  

---

### 3.2 Sekundärregelenergie (aFRR)
\[
R_{aFRR} = (Entgelt_{Leistung} × h_{Bereit}) + (Preis_{Energie} × E_{bereit})
\]
- Leistungspreis: 10 – 30 €/MW·h  
- Energiepreis: 40 – 180 €/MWh  
→ **Ertrag:** 140 000 – 180 000 €/MW·a  
→ Netto nach Kosten ≈ 120 000 – 150 000 €/MW·a  

---

### 3.3 Tertiärregelenergie (mFRR)
- Manuelle Aktivierung nach Abruf  
→ **Ertrag:** 40 000 – 90 000 €/MW·a  

---

### 3.4 Primärregelenergie (FCR)
- Frequenzhaltung < 30 s  
→ **Ertrag:** 200 000 – 350 000 €/MW·a  
→ Hohe Anforderungen, nur für Schnellbatterien (1 – 4 C)

---

### 3.5 Netzdienstleistungen / Redispatch 2.0
- Lokale Netzstützung bei Engpässen  
→ **Ertrag:** 30 000 – 70 000 €/MW·a  

---

### 3.6 Eigenverbrauch / Peak Shaving
- Reduktion von Lastspitzen und PV-Speicherung  
→ **Ersparnis:** 50 – 120 €/kW·a  
→ entspricht 50 000 – 120 000 €/MW·a  

---

### 3.7 PPA-Glättung / Flexibilitätsmärkte
- Glättung von PV- oder Wind-Einspeisung (Firm Power)  
→ **Ertrag:** 15 000 – 40 000 €/MW·a  
→ Abhängig von PPA-Verträgen und Penalty-Struktur  

---

## 4️⃣ Kombinationsszenarien

| Szenario | Märkte | Gesamterlös (€/MW·a) | Bemerkung |
|-----------|---------|----------------------|------------|
| A | Nur Arbitrage | 30 000 – 50 000 | Grundbetrieb |
| B | aFRR + Arbitrage | 160 000 – 220 000 | häufigste Kombination |
| C | aFRR + Redispatch | 180 000 – 240 000 | Netzoptimierung |
| D | PV + Peak Shaving + Arbitrage | 60 000 – 120 000 | Gewerbe/Industrie |
| E | Hybrid aFRR + PPA-Glättung | 200 000 – 260 000 | Contracting / PPA-Projekte |

---

## 5️⃣ Wirtschaftliche Kennzahlen (Beispiel)

### Beispielanlage: 1 MW / 2 MWh (BESS)

| Parameter | Wert |
|------------|------|
| CAPEX | 1.3 M € |
| OPEX | 26 000 €/a |
| Erlös (aFRR + Arbitrage) | 180 000 €/a |
| Cashflow | 154 000 €/a |
| ROI | 11.8 % p.a. |
| Amortisationszeit | ~ 8.5 Jahre |

---

## 6️⃣ Sensitivitätsanalyse (ROI nach Spread)

| Spread (€/MWh) | ROI (%) | Bemerkung |
|----------------|----------|------------|
| 40 | 8.2 | Schwache Volatilität |
| 60 | 11.8 | Realistisch 2025 |
| 90 | 15.5 | Hohe Marktvolatilität |
| 120 | 18.3 | Extremjahr |

---

## 7️⃣ Ergänzende Potenziale
- **CO₂-optimierte Flexibilität / Grüne Märkte** → Bonusprogramme ab 2026 (EU FlexHub, GOPACS)  
- **Black-Start Capability** → Zusatzvergütung vom TSO  
- **Blindleistung / Voltage Support** → lokale Netzverträge  

---

## 8️⃣ Zusammenfassung

| Kategorie | Beschreibung | Realistischer Ertrag €/MW·a |
|------------|---------------|-----------------------------|
| Arbitrage | Spotmarktspreizungen | 30 000 – 50 000 |
| Regelenergie (aFRR / mFRR / FCR) | Netzstabilität | 140 000 – 300 000 |
| Netzdienstleistungen | Redispatch 2.0, Spannung | 30 000 – 70 000 |
| Eigenverbrauch / Peak Shaving | Lastmanagement | 50 000 – 120 000 |
| PPA / Flexibilitätsmärkte | Grünstrom-Verträge | 15 000 – 40 000 |

---

## 9️⃣ Fazit
Ein moderner **BESS mit 1 MW / 2 MWh (C = 0.5)** kann je nach Marktstrategie  
zwischen **150 000 und 250 000 € pro Jahr** an Nettoerlösen erzielen.  
Der wirtschaftliche Erfolg hängt direkt ab von:
- Marktpreisvolatilität  
- Aggregator-/Handelsanbindung  
- EMS-Optimierung (Multi-Use-Betrieb)  
- Degeneration & Effizienz  

---

**Erstellt für:**  
Wirtschaftlichkeitsanalyse BESS 2025 | Mehrmarkt-Optimierung | Cursor AI Integration
