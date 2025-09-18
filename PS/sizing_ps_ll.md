# BESS Sizing mit Exhaustionsmethode (Peak Shaving + Load Leveling)

## Hintergrund
Das ZHAW-Sizing-Tool nutzt die Exhaustionsmethode, um optimale Batteriegrößen (Q_ESS, P_ESS) für
- **Peak Shaving (PS)**: Lastspitzen kappen unterhalb eines monatlichen Grenzwerts P_limit,m  
- **Load Leveling (LL)**: Lastausgleich über den Monat (glatter Verlauf, weniger Varianz)  

Der Algorithmus arbeitet in **zwei Schritten**:
1. **Feasible Region**: Alle (P_ESS, Q_ESS)-Kombinationen, die die PS- und LL-Anforderungen erfüllen.
2. **Optimum**: Innerhalb der zulässigen Kombinationen wird diejenige mit dem höchsten Kostenvorteil ausgewählt (Leistungspreis ↓, Arbitrage ↑, Degradation berücksichtigt).

## Workflow
1. **Inputdaten**
   - 15-min Load (und optional PV/Wasserkraft)
   - Tarife: Energie + Leistungspreis
   - BESS-Parameter: C-Rate, η (Wirkungsgrad), SoC-Limits

2. **Monatliche Grenzwerte**
   - Für jeden Monat wird ein `P_limit,m` abgeleitet (z. B. aus dem 95%-Quantil der Last).

3. **Simulation je Kandidat**
   - Simuliere Lade/Entlade-Strategie:
     - Entladen, wenn Last > P_limit,m (PS)
     - Laden, wenn Last < Monatsmittel (LL)
   - Prüfe Constraints: SoC, P_max, Q_max, C-Rate.

4. **Feasible Region**
   - Behalte nur (P_ESS, Q_ESS), die alle Monate bestehen.

5. **Kostenoptimierung**
   - Berechne ΔK = Einsparung Leistungspreis + Energieverschiebung – Degradationskosten.
   - Wähle Minimum.

## Python-Minibeispiel

```python
import numpy as np
import pandas as pd

# Beispiel-Lastgang (1 Woche, 15-min Auflösung)
np.random.seed(42)
load = 5 + 2*np.sin(np.linspace(0, 14*np.pi, 7*96)) + np.random.normal(0, 0.5, 7*96)
index = pd.date_range("2024-01-01", periods=7*96, freq="15min")
df = pd.DataFrame({"load": load}, index=index)

def simulate(load, P_ESS, Q_ESS, P_limit):
    soc, Q = 0.5*Q_ESS, Q_ESS
    soc_trace = []
    clipped = []
    for l in load:
        if l > P_limit and soc > 0:      # Peak Shaving: entladen
            discharge = min(P_ESS, soc/1) 
            soc -= discharge*0.25  # 0.25h pro Step
            clipped.append(l - discharge)
        elif l < P_limit and soc < Q:    # Load Leveling: laden
            charge = min(P_ESS, (Q-soc)/1)
            soc += charge*0.25
            clipped.append(l + charge)
        else:
            clipped.append(l)
        soc_trace.append(soc)
    return np.array(clipped), np.array(soc_trace)

# Simulation
P_ESS, Q_ESS = 3.0, 10.0   # kW, kWh
P_limit = np.quantile(df["load"], 0.95) # heuristisch
clipped, soc = simulate(df["load"].values, P_ESS, Q_ESS, P_limit)

print("Original Peak:", df["load"].max())
print("Neuer Peak   :", clipped.max())
```

## Nächste Schritte
- Integration ins Projekt als Modul `sizing_ps_ll.py`
- Heatmap-Plot: Kosten über P/Q-Gitter
- Dashboard-Erweiterung: Vergleich Arbitrage vs. PS+LL
