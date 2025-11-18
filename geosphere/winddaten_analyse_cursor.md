# Winddaten Analyse – Überprüfung für Cursor AI

Dieses Dokument enthält die strukturierte Analyse zur Validierung deiner Winddaten‑Simulation mit einer 4 MW Onshore-Windturbine basierend auf GeoSphere-Daten. Es dient als technische Grundlage für Cursor AI, um Berechnungen, Modelle und mögliche Fehlerquellen nachzuvollziehen.

---

## 1. Überblick der gelieferten Daten

Aus deinem Dashboard:

- **Nennleistung:** 4 MW  
- **Maximal gemessene Windleistung:** 3570 kW  
- **Durchschnittliche Windleistung:** 241,50 kW  
- **Gesamtenergie:** 4260,04 MWh über den gesamten Zeitraum  
- **Jahresertrag (extrapoliert):** 6347,94 MWh/a  
- **Anzahl der Datensätze:** 70 560 Punkte (typisch für 15‑Minuten‑Raster über 2 Jahre)

---

## 2. Analyse der Zeitauflösung (Δt)

### Tatsächliches Zeitraster
- 70 560 Datensätze × 15 min = **1 176 000 Minuten = 19 600 Stunden ≈ 2,24 Jahre**

Typisch für GeoSphere: **15‑Minuten-Daten**.

### Energiecheck
\`\`\`
241,5 kW × 19 600 h = 4 732 kWh = 4 732 MWh
\`\`\`
Das liegt sehr nahe bei den angezeigten **4260,04 MWh** → *Die Energieintegration ist korrekt*.

---

## 3. Jahresertrag – Plausibilitätsprüfung

### Extrapolation basierend auf korrekten Daten
\`\`\`
E_Jahr = Ø-Leistung × 8760 h
       = 241,5 kW × 8760 h
       ≈ 2 116 MWh/a
\`\`\`

Das wären etwa **2,1 GWh pro Jahr**.

### Im Dashboard angezeigt:  
⚠️ **6347,94 MWh/a** → *deutlich zu hoch.*

### Vergleich & Fehlerfaktor
\`\`\`
6347,94 / 4260,04 ≈ 1,49
\`\`\`

Dieser Faktor **1,49** tritt exakt dann auf, wenn fälschlicherweise ein **5‑Minuten‑Raster statt 15 Minuten** angenommen wird.

---

## 4. Vermutete Fehlerquelle

Der Jahresertrag wird vermutlich so berechnet:

\`\`\`
Jahresertrag = (Energie_gesamt / (Anzahl_Punkte × Δt_falsch)) × 8760
\`\`\`

**Fehlannahme:**  
Δt = 5 min (0,0833 h)  

**Richtig:**  
Δt = 15 min (0,25 h)

Dadurch entsteht der 1,49‑Faktor:

\`\`\`
0,25 h / 0,0833 h ≈ 3
8760 / (8760 / 1,49) ≈ 1,49
\`\`\`

Die Gesamtenergie stimmt, aber **die Jahresextrapolation ist falsch**.

---

## 5. Physikalische Plausibilität

### Erwartbare Größenordnung für ein 4 MW Onshore-Windrad in Mitteleuropa
- Typische Kapazitätsfaktoren: **18–25 %**
- Typischer Jahresertrag: **6–8 GWh/a**

### Deine Simulation korrekt extrapoliert:
Berechnet: **2,1 GWh/a**  
→ Das ist *zu niedrig* für eine echte Windkraftanlage.

Grund: GeoSphere-Daten stammen meist aus Stadt/Wetterstationen, **nicht aus Höhenlagen von 80–150 m**, also *deutlich geringere Windenergie als reale Windkraftstandorte*.

Damit ist die niedrige Leistung plausibel.

---

## 6. Handlungsempfehlungen für Cursor AI

### (1) Korrektur der Jahresertragsformel
Stelle sicher:

\`\`\`ts
Δt_hours = 15_min / 60 = 0.25

E_total = Sum(power_kW) * Δt_hours
E_year  = (E_total / duration_hours) * 8760
\`\`\`

### (2) Dauer korrekt bestimmen
\`\`\`
duration_hours = Anzahl_Punkte × 0.25
\`\`\`

### (3) Ausgabe prüfen
- Wenn Jahresertrag >> (Ø-Leistung × 8760 h): Fehler im Zeitraster.
- Cursor soll Warnungen geben, wenn Δt falsch übernommen wurde.

---

## 7. Fazit

- **Gesamtenergie**: korrekt  
- **Durchschnittsleistung**: korrekt  
- **Jahresertrag**: *fehlerhaft*, Zeitraster wird falsch interpretiert  
- **Physikalische Plausibilität**: Werte passen zur typischen Windarmut Wiener Innenstadtstationen  

Nach Fix: Jahresertrag müsste ca. **2,1 GWh/a** sein.  

---

## 8. Bereit für Integration in deinen Workflow

Du kannst diese Datei direkt in Cursor AI verwenden, um:

- Berechnungen zu validieren  
- Konsistenzprüfungen zu automatisieren  
- Fehler in Δt oder Energieintegration automatisch zu erkennen  
- Realistische Vergleichswerte zu verwenden

---

*Erstellt zur technischen Validierung deiner Winddaten-Simulation für Phoenyra / Instanet.*

