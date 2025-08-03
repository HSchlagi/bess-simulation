
# Prompt zur Weiterentwicklung des BESS-Simulationsprogramms mit Cursor AI

Basierend auf der Analyse des Use Case "Hinterstoder" (CyberGrid, Juli 2025) entwickle bitte neue Funktionen für mein bestehendes BESS-Simulationsprogramm. Ziel ist es, sowohl das ökonomische Potenzial realistischer abzubilden als auch die Steuerung des Speichers flexibler zu machen.

## Neue Anforderungen und Ergänzungen

1. **Simulation mehrerer Use Cases:**
   - UC1: Verbrauch ohne Eigenerzeugung
   - UC2: Verbrauch + PV (1,95 MWp)
   - UC3: Verbrauch + PV + Wasserkraft (650 kW, 2700 MWh/a)

2. **Erlösmodellierung:**
   - Berücksichtige Strompreise (Spotmarkt, Day-Ahead & Intraday)
   - Sekundärregelenergie-Vermarktung (SRL+, SRL-)
   - Arbitragepotenziale (Lade-/Entladeoptimierung)
   - Einbindung von Erlösen durch Aktivierungen und Bereitstellungen

3. **Netzentgelte & gesetzliche Abgaben:**
   - Spot-indizierte Tarife für Bezug & Einspeisung
   - Stromabgaben, Netzverlustentgelte, Clearinggebühren
   - Förderlogik für Erneuerbare (z.B. 0 EUR im Jahr 2024)

4. **Prognose- & Degradationsmodell:**
   - 10-Jahres-Verlauf der Erlöse mit Batteriedegradation
   - Modellierung gesetzlicher Änderungen (z.B. Stromabgabe von 1 EUR auf 15 EUR/MWh)

5. **Lastprofil-Import & Residuallast-Berechnung:**
   - Import 15-Min-Werte aus realen CSV-Dateien
   - Darstellung typischer Jahres- & Wochenverläufe
   - Analyse der Residuallast für Lade-/Entladestrategie

6. **Visualisierung:**
   - Darstellung von:
     - Jahres- & Monatsbilanz
     - Erlöspotenzial nach Komponenten (Arbitrage, SRL+, SRL-, etc.)
     - Netzentgeltbelastungen
     - Batterienutzung (Zyklen pro Jahr)

7. **Flexibles Energiemanagementsystem:**
   - Erzeuge Simulationen mit eingeschränkten Einspeise-/Bezugskapazitäten
   - Plane Lastverschiebung (Load-Shifting) in Zeiten günstiger Tarife
   - Erzeuge zeitlich aufgelöste Fahrpläne für Speicher

## Technische Hinweise
- Zielumgebung: Python + Flask + SQLite
- Frontend: TailwindCSS, ChartJS
- Exportmöglichkeiten: CSV, Excel, PDF
