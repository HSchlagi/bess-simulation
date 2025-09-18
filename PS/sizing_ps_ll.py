import numpy as np
import pandas as pd

def simulate(load, P_ESS, Q_ESS, P_limit):
    soc, Q = 0.5*Q_ESS, Q_ESS
    soc_trace = []
    clipped = []
    for l in load:
        if l > P_limit and soc > 0:
            discharge = min(P_ESS, soc/1)
            soc -= discharge*0.25  # 0.25h Zeitschritt
            clipped.append(l - discharge)
        elif l < P_limit and soc < Q:
            charge = min(P_ESS, (Q-soc)/1)
            soc += charge*0.25
            clipped.append(l + charge)
        else:
            clipped.append(l)
        soc_trace.append(soc)
    return np.array(clipped), np.array(soc_trace)

if __name__ == "__main__":
    np.random.seed(42)
    load = 5 + 2*np.sin(np.linspace(0, 14*np.pi, 7*96)) + np.random.normal(0, 0.5, 7*96)
    index = pd.date_range("2024-01-01", periods=7*96, freq="15min")
    df = pd.DataFrame({"load": load}, index=index)

    P_ESS, Q_ESS = 3.0, 10.0   # kW, kWh
    P_limit = np.quantile(df["load"], 0.95)

    clipped, soc = simulate(df["load"].values, P_ESS, Q_ESS, P_limit)

    print("Original Peak:", df["load"].max())
    print("Neuer Peak   :", clipped.max())
