from fastapi import FastAPI, HTTPException, Header, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Any
import sqlite3, os, json

API_TOKEN = os.getenv("API_TOKEN", "changeme_token_123")
DB_FILE = os.getenv("DB_FILE", "/data/bess.db")

app = FastAPI(title="BESS Ingestion API (SQLite)")

class Telemetry(BaseModel):
    ts: str
    site: str = "site1"
    device: str = "bess1"
    soc: Optional[float] = None
    p: Optional[float] = None
    p_ch: Optional[float] = None
    p_dis: Optional[float] = None
    v_dc: Optional[float] = None
    i_dc: Optional[float] = None
    t_cell_max: Optional[float] = None
    soh: Optional[float] = None
    alarms: Optional[List[Any]] = Field(default_factory=list)

def init_db():
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS bess_telemetry (
      site TEXT NOT NULL,
      device TEXT NOT NULL,
      ts TEXT NOT NULL,
      soc REAL,
      p REAL,
      p_ch REAL,
      p_dis REAL,
      v_dc REAL,
      i_dc REAL,
      t_cell_max REAL,
      soh REAL,
      alarms TEXT,
      PRIMARY KEY (site, device, ts)
    )
    """)
    con.commit()
    con.close()

@app.on_event("startup")
def startup():
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True) if os.path.dirname(DB_FILE) else None
    init_db()

def check_token(authorization: Optional[str]):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    token = authorization.split(" ", 1)[1]
    if token != API_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")

@app.post("/api/ingest")
def ingest(payload: Telemetry, authorization: Optional[str] = Header(None)):
    check_token(authorization)
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("""
    INSERT OR REPLACE INTO bess_telemetry
    (site, device, ts, soc, p, p_ch, p_dis, v_dc, i_dc, t_cell_max, soh, alarms)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        payload.site, payload.device, payload.ts,
        payload.soc, payload.p, payload.p_ch, payload.p_dis,
        payload.v_dc, payload.i_dc, payload.t_cell_max,
        payload.soh, json.dumps(payload.alarms)
    ))
    con.commit()
    con.close()
    return JSONResponse({"ok": True})

@app.get("/api/last")
def last(authorization: Optional[str] = Header(None), limit: int = Query(5, ge=1, le=100)):
    check_token(authorization)
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("""
      SELECT site, device, ts, soc, p, p_ch, p_dis, v_dc, i_dc, t_cell_max, soh, alarms
      FROM bess_telemetry
      ORDER BY ts DESC
      LIMIT ?
    """, (limit,))
    rows = cur.fetchall()
    con.close()
    cols = ["site","device","ts","soc","p","p_ch","p_dis","v_dc","i_dc","t_cell_max","soh","alarms"]
    return [dict(zip(cols, r)) for r in rows]

@app.get("/healthz")
def healthz():
    return {"ok": True}
