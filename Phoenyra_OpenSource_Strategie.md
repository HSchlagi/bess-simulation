# Phoenyra BESS Studio – Open Source Strategie

## 1. Überblick
**Phoenyra BESS Studio** ist eine modulare Plattform für:
- Batteriespeicher-Simulation (BESS)
- Monitoring & Datenanalyse
- Energy-Trading & Dispatching

Ziel: Veröffentlichung als **Open-Source-Projekt** mit wirtschaftlicher und strategischer Tragfähigkeit.

---

## 2. Mögliche Erträge („Obulus“)
Bei einer Open-Source-Freigabe erfolgt kein klassischer Lizenzumsatz.  
Der Ertrag entsteht über neue Umsatzkanäle:

| Modell | Beschreibung | Möglicher Ertrag |
|--------|---------------|------------------|
| **Dual License** | Basis frei, kommerzielle Nutzung oder Hosting lizenziert | 1 000 – 50 000 €/Jahr |
| **Support & Consulting** | Installation, Customizing, Schulung | 100 – 250 €/h |
| **Managed Cloud / SaaS** | Betrieb als Service (z. B. phoenyra.cloud) | 20 – 100 €/User/Monat |
| **Add-ons & Plugins** | Erweiterungen (z. B. Trading Optimizer, Grid Connect) | 100 – 1 000 € pro Modul |
| **Förderungen / EU-Projekte** | Open-Energy-Projekte (FFG, Horizon Europe) | 50 000 – 500 000 € |
| **Partnerschaften / Investoren** | Seed- oder Beteiligungskapital | 50 000 – 1 000 000 € |

---

## 3. Strategischer Nutzen
- **Vertrauen & Sichtbarkeit:** Positionierung als europäische Open-Energy-Marke  
- **Community-Beteiligung:** Entwickler, Forschung & EVUs können beitragen  
- **Standardisierung:** Phoenyra als De-facto-Standard für BESS Simulation & Trading  
- **Förderfähigkeit:** Bessere Chancen bei EU-Projekten (Open-Source-Pflicht)  
- **Markenwert:** Wert des Know-hows und der SaaS-Infrastruktur steigt

---

## 4. Schutz & Lizenzwahl
Empfohlene Lizenzmodelle:

| Lizenz | Vorteile | Empfohlen für |
|--------|-----------|---------------|
| **AGPL v3** | Schützt vor unrechtmäßiger SaaS-Kopie | Simulation-Core |
| **MPL 2.0** | Kompatibel mit kommerzieller Nutzung | UI- und Dashboard-Komponenten |
| **Custom License (Phoenyra Community License)** | Nur Forschung/Nicht-kommerzielle Nutzung erlaubt | Gesamtpaket für Testprojekte |

Empfohlene Trennung:
```text
phoenyra-bess/
 ├── simulation-core/    # Open Source (AGPL)
 ├── dashboard-ui/       # Open Source (MIT oder MPL)
 ├── trading-engine/     # Proprietär oder Dual License
 ├── connectors/         # Teilweise offen
 ├── docs/               # Öffentlich (ReadTheDocs)
 └── saas/               # Intern (kommerziell)
```

---

## 5. Realistische Erwartung
**Kurzfristig:** Kein direkter Verkaufserlös.  
**Mittelfristig:** Mehr Aufträge, Partner & Förderungen.  
**Langfristig:** Starker Markenwert und strategische Marktposition.

**Risiko:** Kopien ohne klare Lizenz können dich Wettbewerb kosten → Lizenzierung ist zentral.

---

## 6. Fazit
Die Open-Source-Freigabe ist kein Verlust, sondern ein Multiplikator:

> Du tauschst kurzfristige Lizenzumsätze gegen langfristige Markenmacht,  
> Innovationsvorsprung und Zugang zu größeren Partnern & Projekten.

---

## 7. Nächste Schritte
1. **Lizenzmodell wählen** (AGPL / MPL / Dual License)  
2. **Code-Struktur vorbereiten** (Open-Core vs Enterprise)  
3. **GitHub-Repository aufsetzen**  
4. **Community-Dokumentation & Branding**  
5. **Phoenyra Open Launch ankündigen**

---

© 2025 Phoenyra Energy Systems – Open Source Strategy Draft v1.0
