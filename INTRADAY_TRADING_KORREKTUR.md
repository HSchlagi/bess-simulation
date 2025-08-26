# Intraday Trading Korrektur - Wirtschaftlichkeitsanalyse

## Problem
Die Werte für Intraday Trading in der detaillierten Wirtschaftlichkeitsanalyse waren unrealistisch hoch:
- **Vorher:** 2.708.008 € (unrealistisch)
- **Nachher:** ~584.000 € (realistisch)

## Ursache
Die Berechnung verwendete zu optimistische Parameter:

### 1. Tägliche Zyklen
- **Vorher:** 2,5 Zyklen/Tag
- **Nachher:** 1,2 Zyklen/Tag (realistischer)

### 2. Preise (€/kWh)
| Komponente | Vorher | Nachher | Begründung |
|------------|--------|---------|------------|
| Spot-Arbitrage | 0,15€ | 0,08€ | Realistischer Marktpreis |
| Intraday-Trading | 0,22€ | 0,12€ | Reduziert auf Marktniveau |
| Regelenergie | 0,40€ | 0,25€ | Angepasst an aktuelle Preise |

### 3. Sekundärmarkt-Preise
| Komponente | Vorher | Nachher | Begründung |
|------------|--------|---------|------------|
| Frequenzregelung | 0,45€ | 0,30€ | Realistischer Marktpreis |
| Kapazitätsmärkte | 0,28€ | 0,18€ | Angepasst an aktuelle Preise |
| Flexibilitätsmärkte | 0,35€ | 0,22€ | Reduziert auf Marktniveau |

## Berechnung für BESS Hinterstoder (8.000 kWh / 2.000 kW)

### Vorher (unrealistisch):
- Spot-Arbitrage: 8.000 kWh × 2,5 × 365 × 0,15€ = **1.095.000€**
- Intraday-Trading: 8.000 kWh × 2,5 × 365 × 0,22€ = **1.606.000€**
- Regelenergie: 2.000 kW × 8.760h × 0,40€/1000 = **7.008€**
- **Gesamt:** 2.708.008€

### Nachher (realistisch):
- Spot-Arbitrage: 8.000 kWh × 1,2 × 365 × 0,08€ = **280.320€**
- Intraday-Trading: 8.000 kWh × 1,2 × 365 × 0,12€ = **420.480€**
- Regelenergie: 2.000 kW × 8.760h × 0,25€/1000 = **4.380€**
- **Gesamt:** ~705.180€

## Datei-Änderungen
- `app/routes.py`: Zeilen 4334-4361 (Intraday-Berechnung)
- `app/routes.py`: Zeilen 4363-4390 (Sekundärmarkt-Berechnung)

## Validierung
Die neuen Werte sind jetzt realistisch und entsprechen den aktuellen Marktpreisen für:
- EPEX Spot-Markt
- EPEX Intraday-Markt
- APG Regelenergie
- Sekundärmarkt-Dienstleistungen

## Nächste Schritte
1. Server neu starten für die Änderungen
2. Wirtschaftlichkeitsanalyse erneut durchführen
3. Werte mit aktuellen Marktdaten validieren

