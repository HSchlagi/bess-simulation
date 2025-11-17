# ⚡ Sekundärmarkt (aFRR) – Potenziale für Batteriespeicher

## 🔍 Überblick der Märkte für Batteriespeicher

| Markt | Beschreibung | Zeithorizont | Hauptziel | Erlösart |
|--------|---------------|---------------|------------|-----------|
| **Day-Ahead / Intraday (Arbitrage)** | Kauf/Verkauf auf Spotmarkt | Stunden bis Minuten | Preisunterschiede nutzen | Energiehandel |
| **Sekundärregelenergie (aFRR)** | automatische Leistungsbereitstellung | Sekunden–Minuten | Netzfrequenzstützung | Leistungsbereitstellung (€ / MW) |
| **Tertiärregelenergie (mFRR)** | manuell abgerufen | Minuten–15 min | Reserve nach aFRR | Leistungsbereitstellung |
| **Primärregelenergie (FCR)** | Frequenzhaltung sofort | < 30 s | Stabilisierung | hohe Anforderungen, konstante Leistung |
| **Netzdienstleistungen / Redispatch 2.0** | Entlastung von Netzengpässen | Stunden–Tage | lokale Flexibilität | Energie und Leistung |

---

## 📊 Typische aFRR-Erlöse (2024–2025)

| Land | Bereitstellungsentgelt (€/MW/h) | Energiepreis (€/MWh) | Gesamterlös (€/MW·Jahr) |
|-------|----------------------------------|-----------------------|--------------------------|
| 🇩🇪 Deutschland | 8 – 25 | 50 – 200 | 150 000 – 300 000 |
| 🇦🇹 Österreich | 10 – 30 | 40 – 180 | 180 000 – 320 000 |
| 🇨🇭 Schweiz | 20 – 40 | 70 – 250 | 220 000 – 350 000 |

---

## 💰 Beispielrechnung (Österreich, aFRR)

**Anlage:** 1 MW / 2 MWh (C = 0,5)

| Komponente | Annahme | Jahresertrag |
|-------------|----------|---------------|
| Bereitstellungsvergütung | 18 €/MW/h × 8 000 h | 144 000 € |
| Energievergütung (Arbeit) | 80 €/MWh × 250 MWh | 20 000 € |
| **Summe brutto** |  | **≈ 164 000 € / Jahr** |
| – Betrieb, Prognose, Ausfall | ca. 15 % | ≈ 140 000 €/Jahr netto |

---

## ⚙️ Voraussetzungen für Teilnahme (APG / E-Control)

1. **Technische Präqualifikation**
   - Reaktionszeit < 30 s, Dauerleistung ≥ 15 min  
   - Frequenzregelung über EMS oder Reglerbox  
   - Kommunikation mit Plattform (PICASSO, MARI)

2. **Bilanzgruppenvertrag & Direktvermarktung**
   - Teilnahme über **Aggregator** oder **Direktvermarkter**  
   - Beispiele: *Next Kraftwerke, Entelios, Energie Steiermark, aWATTar Flex, etc.*

3. **Mindestgröße**
   - ab ca. 1 MW möglich (Aggregation erlaubt)  
   - 2 MWh Kapazität → volle 15 min bei 1 MW (C = 0,5 passt perfekt)

---

## ⚡ Kombinationsstrategie

Ein moderner BESS kann **mehrere Märkte parallel** bedienen:

| Strategie | Beschreibung | Jahresertrag (realistisch €/MW·Jahr) |
|------------|---------------|--------------------------------------|
| Nur Arbitrage | Preisunterschiede am Spotmarkt nutzen | 30 000 – 50 000 |
| Nur aFRR | reine Regelenergie-Bereitstellung | 140 000 – 180 000 |
| Kombiniert | EMS entscheidet dynamisch zwischen Märkten | 160 000 – 220 000 |

---

## 🧭 Fazit

- Der **Sekundärmarkt (aFRR)** ist **2–4× profitabler** als reine Arbitrage.  
- Mit **C = 0,5** und **2 MWh pro MW Leistung** ist der Speicher **technisch optimal** für 15‑min‑Anforderungen.  
- Kombination aus **aFRR + Arbitrage** erhöht den Gesamtumsatz auf **≈ 180 000 – 220 000 €/MW·Jahr**.  
- Weitere Potenziale: Teilnahme an **Redispatch 2.0**, **Netzdienstleistungen**, oder **Flexibilitätsmärkten (FlexHub, GOPACS)**.

---

**Erstellt für:**  
C‑Rate 0,5 | BESS‑Leistung 1 MW | Sekundärmarkt (aFRR) Österreich 2025
