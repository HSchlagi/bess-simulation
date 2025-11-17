
from __future__ import annotations

import pandas as pd


def _get_dt_hours(df: pd.DataFrame) -> float:
    """Ermittelt Δt in Stunden auf Basis der ersten beiden Zeitstempel."""
    if len(df.index) < 2:
        raise ValueError("Zu wenige Datenpunkte, um Δt zu bestimmen.")
    return (df.index[1] - df.index[0]).total_seconds() / 3600.0


def calc_basic_kpis(df: pd.DataFrame, power_col: str = "P") -> dict:
    """
    Berechnet Basis-Kennzahlen eines Lastprofils.
    Annahme: df.index ist DatetimeIndex, df[power_col] in kW.
    """
    if power_col not in df.columns:
        raise ValueError(f"Spalte '{power_col}' nicht im DataFrame.")

    dt_hours = _get_dt_hours(df)
    s = df[power_col].fillna(0.0)

    energy_kwh = (s * dt_hours).sum()
    p_max = float(s.max())
    p_mean = float(s.mean())

    lastfaktor = p_mean / p_max if p_max > 0 else 0.0
    benutzungsdauer_h = energy_kwh / p_max if p_max > 0 else 0.0

    return {
        "E_jahr_kWh": energy_kwh,
        "P_max_kW": p_max,
        "P_mean_kW": p_mean,
        "Lastfaktor": lastfaktor,
        "Benutzungsdauer_h": benutzungsdauer_h,
    }


def load_duration_curve(df: pd.DataFrame, power_col: str = "P") -> pd.DataFrame:
    """
    Erzeugt eine Lastdauerlinie:
      - sortierte Leistungen absteigend
      - zugehörige Stunden (x-Achse) als kumulierte Zeit.
    """
    if power_col not in df.columns:
        raise ValueError(f"Spalte '{power_col}' nicht im DataFrame.")

    dt_hours = _get_dt_hours(df)
    s = df[power_col].dropna().sort_values(ascending=False).reset_index(drop=True)

    hours = (s.index + 1) * dt_hours
    ldc = pd.DataFrame({"hours": hours, "P_kW": s.values})
    return ldc
