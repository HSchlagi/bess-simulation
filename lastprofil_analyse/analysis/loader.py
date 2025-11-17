
from io import BytesIO
from typing import Literal

import pandas as pd


def load_lastprofil_from_bytes(
    content: bytes,
    ts_col: str = "timestamp",
    power_col: str = "P_total",
    freq: Literal["15min", "60min", "1h"] = "15min",
    sep: str = ";",
    decimal: str = ",",
) -> pd.DataFrame:
    """
    Lädt ein Lastprofil aus Rohbytes (UploadFile),
    resampled auf freq und normiert die Leistungsspalte auf 'P'.

    Erwartet:
      - Spalte mit Zeitstempeln (ts_col)
      - Spalte mit Leistung in kW (power_col)
    """
    df = pd.read_csv(BytesIO(content), sep=sep, decimal=decimal)

    if ts_col not in df.columns:
        raise ValueError(f"Zeitspalte '{ts_col}' nicht in CSV gefunden. Spalten: {list(df.columns)}")

    if power_col not in df.columns:
        raise ValueError(f"Leistungsspalte '{power_col}' nicht in CSV gefunden. Spalten: {list(df.columns)}")

    # Zeitachsen-Aufbereitung
    df[ts_col] = pd.to_datetime(df[ts_col])
    df = df.set_index(ts_col).sort_index()

    # Auf gewünschte zeitliche Auflösung bringen
    df = df.resample(freq).mean(numeric_only=True)

    # Nur relevante Spalte behalten und normieren
    df = df[[power_col]].rename(columns={power_col: "P"})

    # Offensichtliche Ausreißer optional filtern (z. B. negative Werte)
    df["P"] = df["P"].clip(lower=0)

    return df
