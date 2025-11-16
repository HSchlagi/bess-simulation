# Windkraft-Ertragsmodell + BESS-Integration (15‑Minuten-Basis)

Diese Datei beschreibt **vollständig**, wie du:
- Winddaten (ZAMG/GeoSphere) verarbeitest,
- Windleistung aus einer Power-Curve berechnest,
- 15‑Minuten-Energie ableitest,
- Jahresertrag berechnest,
- das Ergebnis in deine **BESS-Simulation** integrierst (PV + Wind + Last + Handel).

---

# 1. Grundlagen des Windmodells

## 1.1 Eingangsdaten
Du benötigst Zeitreihen mit:
- `timestamp`
- `v_10m` … Windgeschwindigkeit auf 10 m (ZAMG)
- optional: Temperatur, Luftdruck, Luftdichte

---

# 2. Hochrechnung der Windgeschwindigkeit auf Hubhöhe

Formel (Power Law):
```
v_hub = v_10m * (hub_height / 10)^alpha
```

Typische α-Werte:
- 0.12–0.16 offene Fläche  
- 0.20–0.30 hügelig / bewaldet  

---

# 3. Power‑Curve zuordnen

Power‑Curve (Hersteller):
- `v [m/s]` → `P [kW]`

Interpolation linear zwischen Stützstellen.

Pseudo-Code:
```
if v < cut_in: P = 0
if cut_in <= v <= rated: interpolate
if rated <= v <= cut_out: P = P_rated
if v > cut_out: P = 0
```

---

# 4. Nettoleistung nach Verlusten

Verlustfaktoren (beispielhaft):
- Turbinen-Verfügbarkeit: 97 %
- Netz/Trafo: 3 %
- Curtailment: 5 %

Beispiel:
```
P_net = P_raw * (1 - total_losses)
```

---

# 5. Energie in 15‑Minuten‑Intervallen

```
E_15min_kWh = P_net_kW * 0.25
```

---

# 6. Jahresertrag

Summieren:
```
E_year = SUM(E_15min_kWh)
```

Vollbenutzungsstunden:
```
VBH = E_year / P_rated
```

---

# 7. Einbindung in die BESS-Simulation

Nettoenergie am Knoten:
```
P_total(t) = PV(t) + Wind(t) - Load(t)
```

BESS lädt bei Überschuss, entlädt bei Defizit.
Wind erhöht typischerweise die Zyklenzahl, aber reduziert Netzbezug.

---

# 8. Excel-Struktur

Das Excel enthält:
- Wind_Input (Rohdaten + Modellformeln)
- PowerCurve (Tabelle)
- Annual_Results (Summen & KPIs)

Formelbeispiele findest du in der Excel-Datei selbst.

---

# 9. Beispiel für vollständigen Workflow (Cursor AI)

1. CSV (ZAMG) einlesen  
2. Hubhöhe berechnen  
3. PowerCurve interpolieren  
4. Nettoleistung berechnen  
5. 15‑Min‑Energie ermitteln  
6. Jahresertrag summieren  
7. Windleistung in BESS‑Simulation einspeisen  
8. Graphen & KPIs erzeugen  

---

Fertig für Cursor AI!