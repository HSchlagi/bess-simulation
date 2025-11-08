#!/usr/bin/env python3
"""Importiert ENTSO-E Day-Ahead Spotpreise aus exportierten CSV-Dateien."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from typing import Iterable

import pandas as pd

from app import create_app, db
from models import SpotPrice

DEFAULT_SOURCE = "ENTSO-E (FTP)"
DEFAULT_REGION = "AT"
DEFAULT_PRICE_TYPE = "day_ahead"
DEFAULT_AREA = "BZN|AT"


def load_price_file(path: Path, area: str = DEFAULT_AREA) -> pd.Series:
    """Liest eine ENTSO-E Export-CSV und liefert eine stündliche Preis-Serie."""
    df = pd.read_csv(path)

    # Nur relevante Spalten behalten
    df = df[["MTU (UTC)", "Area", "Sequence", "Day-ahead Price (EUR/MWh)"]]
    df = df[df["Area"] == area].copy()

    if df.empty:
        return pd.Series(dtype=float)

    # Startzeit extrahieren
    df["start_utc"] = (
        df["MTU (UTC)"].str.split(" - ").str[0].pipe(
            lambda s: pd.to_datetime(s, format="%d/%m/%Y %H:%M:%S", utc=True)
        )
    )

    # Sequenzen pivotieren (Sequence Sequence 1/2)
    df["Sequence"] = df["Sequence"].str.extract(r"(Sequence \d)")
    df = df.pivot_table(
        index="start_utc",
        columns="Sequence",
        values="Day-ahead Price (EUR/MWh)",
        aggfunc="first",
    )

    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Preispräferenz: Sequence 2 vor Sequence 1
    price = df.get("Sequence 2").fillna(df.get("Sequence 1"))
    price.name = "price_eur_mwh"

    # Auf Stundenmittel aggregieren
    price = price.resample("h").mean()
    price = price.dropna()
    return price


def combine_series(paths: Iterable[Path], area: str = DEFAULT_AREA) -> pd.Series:
    series_list = [load_price_file(path, area) for path in paths]
    if not series_list:
        return pd.Series(dtype=float)
    combined = pd.concat(series_list)
    combined = combined[~combined.index.duplicated(keep="last")]
    combined = combined.sort_index()
    return combined


def import_prices(series: pd.Series, source: str, region: str, price_type: str) -> int:
    if series.empty:
        return 0

    app = create_app()
    with app.app_context():
        start_dt = series.index.min().to_pydatetime()
        end_dt = series.index.max().to_pydatetime()

        # Naive UTC für DB speichern
        start_naive = start_dt.replace(tzinfo=None)
        end_naive = end_dt.replace(tzinfo=None)

        # Alte Datensätze entfernen
        deleted = (
            SpotPrice.query.filter(
                SpotPrice.source == source,
                SpotPrice.region == region,
                SpotPrice.price_type == price_type,
                SpotPrice.timestamp >= start_naive,
                SpotPrice.timestamp <= end_naive,
            ).delete(synchronize_session=False)
        )
        if deleted:
            print(f"{deleted} bestehende Datensätze entfernt")

        for ts, price in series.items():
            timestamp = ts.to_pydatetime().replace(tzinfo=None)
            db.session.add(
                SpotPrice(
                    timestamp=timestamp,
                    price_eur_mwh=float(price),
                    source=source,
                    region=region,
                    price_type=price_type,
                    created_at=datetime.utcnow(),
                )
            )

        db.session.commit()
        return len(series)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "files",
        nargs="*",
        type=Path,
        help="Pfad(e) zu ENTSO-E CSV-Dateien",
        default=[
            Path("TP_export/GUI_ENERGY_PRICES_202401010000-202501010000.csv"),
            Path("TP_export/GUI_ENERGY_PRICES_202501010000-202601010000.csv"),
        ],
    )
    parser.add_argument("--source", default=DEFAULT_SOURCE)
    parser.add_argument("--region", default=DEFAULT_REGION)
    parser.add_argument("--price-type", default=DEFAULT_PRICE_TYPE)
    parser.add_argument("--area", default=DEFAULT_AREA, help="ENTSO-E Area Code (z. B. BZN|AT)")
    args = parser.parse_args()

    available_paths = [path for path in args.files if path.exists()]
    if not available_paths:
        raise SystemExit("Keine Eingabedateien gefunden.")

    series = combine_series(available_paths, area=args.area)
    inserted = import_prices(series, args.source, args.region, args.price_type)
    print(f"Import abgeschlossen – {inserted} Stundenpreise gespeichert.")


if __name__ == "__main__":
    main()
