# 📊 Arbitrage-Ertragsmodell für Batteriespeicher (C-Rate 0,5)

## 🔧 Annahmen

| Parameter | Wert | Beschreibung |
|------------|-------|--------------|
| Strompreis (Spotmarkt) | 60 – 150 €/MWh | typische Spanne im österreichischen & deutschen Markt |
| Preis-Spread (Differenz Tag/Nacht) | 40 – 70 €/MWh | realistisch zwischen niedrigen und hohen Stunden |
| Speicherleistung | 0,5 MW pro 1 MWh (C-Rate 0,5) | Lade-/Entladezeit ≈ 2 h |
| Zyklusrate | 1 Zyklus / Tag | täglicher Vollzyklus |
| Roundtrip-Wirkungsgrad | 90 % | Lade-/Entladeverluste |
| Verfügbarkeit | 95 % | Wartung, Steuerung, Ausfälle |
| Betriebsdauer | 365 Tage / Jahr | kontinuierlicher Betrieb |

---

## ⚙️ Berechnung

**Formel:**

\[
E_{Jahr} = (\text{Spread} × η × \text{Zyklen pro Jahr})
\]

\[
\text{Zyklen pro Jahr} = 365 × \text{Verfügbarkeit}
\]

---

### Beispielrechnung (1 MWh Kapazität)

| Spread €/MWh | Effizienz | Zyklen/Jahr | Jahresertrag €/MWh |
|---------------|------------|--------------|--------------------|
| 40 | 0,9 | 347 | 10 800 |
| 60 | 0,9 | 347 | 18 700 |
| 80 | 0,9 | 347 | 24 900 |
| 100 | 0,9 | 347 | 31 100 |

---

### Skalierung

| Systemgröße | Leistung | Kapazität | Jahresertrag (ca.) |
|--------------|-----------|------------|--------------------|
| 1 MW / 2 MWh | 1 MW | 2 MWh | 37 000 € |
| 5 MW / 10 MWh | 5 MW | 10 MWh | 187 000 € |
| 10 MW / 20 MWh | 10 MW | 20 MWh | 374 000 € |

---

## 📈 Ergebniszusammenfassung

- **C-Rate 0,5 → ca. 2 h Entladezeit**
- **Jahresertrag (realistisch): 10 000 – 20 000 € pro MWh Kapazität**
- Skalierbar auf größere Anlagen:  
  z. B. 10 MWh → 100 000 – 200 000 €/Jahr  
- Roundtrip-Wirkungsgrad, Spread-Häufigkeit und Prognosequalität beeinflussen das Ergebnis direkt.

---

## 💡 Hinweise

- Zusatzerlöse sind durch Teilnahme an **aFRR/mFRR** oder **Netzdienstleistungen** möglich.  
- Optimierung durch **mehrfache Teilzyklen pro Tag (wenn Spread > Kosten)** kann Rendite weiter steigern.  
- Degeneration (Zellalterung) ca. 1 000 – 2 000 Zyklen → Betrieb wirtschaftlich über 8 – 10 Jahre möglich.

---

**Erstellt für:**  
C-Rate 0,5 | Strompreis 60 – 150 €/MWh | BESS-Arbitrage-Simulation
