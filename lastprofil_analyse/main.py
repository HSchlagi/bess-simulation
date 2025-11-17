
from __future__ import annotations

from typing import List

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from analysis.loader import load_lastprofil_from_bytes
from analysis.kpi import calc_basic_kpis, load_duration_curve

app = FastAPI(
    title="Lastprofil Analyse API",
    version="0.1.0",
    description="Einfache API zur Analyse von elektrischen Lastprofilen (BESS / Netzplanung).",
)

# CORS für lokale Entwicklung / Frontend-Integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # später einschränken (Phoenyra-Domain)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class KPIResponse(BaseModel):
    E_jahr_kWh: float
    P_max_kW: float
    P_mean_kW: float
    Lastfaktor: float
    Benutzungsdauer_h: float


class LDCPoint(BaseModel):
    hours: float
    P_kW: float


class AnalyzeResponse(BaseModel):
    kpis: KPIResponse
    ldc: List[LDCPoint]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_lastprofil(
    file: UploadFile = File(..., description="CSV mit Lastprofil"),
    ts_col: str = Form("timestamp"),
    power_col: str = Form("P_total"),
    freq: str = Form("15min"),
    sep: str = Form(";"),
    decimal: str = Form(","),
    max_ldc_points: int = Form(500),
):
    """
    Nimmt ein CSV-Lastprofil entgegen und liefert:
      - Basis-KPIs
      - Lastdauerlinie (ggf. reduziert auf max_ldc_points Punkte)

    Ideal als Backend für Phoenyra BESS Studio / Lastprofil-Analyse-UI.
    """
    try:
        raw_bytes = await file.read()
        df = load_lastprofil_from_bytes(
            raw_bytes,
            ts_col=ts_col,
            power_col=power_col,
            freq=freq,
            sep=sep,
            decimal=decimal,
        )

        kpis_dict = calc_basic_kpis(df)
        ldc_df = load_duration_curve(df)

        # Downsampling der Lastdauerlinie für Frontend
        n = len(ldc_df)
        if n == 0:
            ldc_points = []
        else:
            if n > max_ldc_points and max_ldc_points > 0:
                step = max(n // max_ldc_points, 1)
                ldc_df = ldc_df.iloc[::step]

            ldc_points = [
                LDCPoint(hours=float(row["hours"]), P_kW=float(row["P_kW"]))
                for _, row in ldc_df.iterrows()
            ]

        return AnalyzeResponse(
            kpis=KPIResponse(**kpis_dict),
            ldc=ldc_points,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Interner Fehler: {e}")
