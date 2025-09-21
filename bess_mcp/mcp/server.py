import os, json, sqlite3, time, importlib, requests
from typing import Dict, Any

from mcp.server.fastmcp import FastMCP

try:
    import paho.mqtt.client as mqtt
except Exception:
    mqtt = None

DB_PATH = os.getenv("BESS_DB_PATH", "/data/bess.db")
MQTT_HOST = os.getenv("MQTT_BROKER", "mqtt-broker")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_USERNAME = os.getenv("MQTT_USERNAME") or None
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD") or None

DISPATCH_MODULE = os.getenv("DISPATCH_MODULE", "app.sim_dispatch")
DISPATCH_FUNC = os.getenv("DISPATCH_FUNC", "run_dispatch")

AWATTAR_BASE_URL = os.getenv("AWATTAR_BASE_URL", "https://api.awattar.at/v1/marketdata")
AWATTAR_COUNTRY = os.getenv("AWATTAR_COUNTRY", "AT").upper()

mcp = FastMCP("bess-sim")

def _db():
    con = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
    con.row_factory = sqlite3.Row
    return con

def _mqtt():
    if mqtt is None:
        raise RuntimeError("paho-mqtt not installed")
    client = mqtt.Client()
    if MQTT_USERNAME:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD or "")
    client.connect(MQTT_HOST, MQTT_PORT, keepalive=30)
    return client

def _import_dispatch():
    mod = importlib.import_module(DISPATCH_MODULE)
    fn = getattr(mod, DISPATCH_FUNC)
    return fn

# ------------------ Tools ------------------

@mcp.tool(description="Hole Spotpreise (EUR/MWh) für YYYY-MM-DD aus Tabelle spot(ts ISO, price_eur_mwh REAL).")
def prices_get_spotcurve(date_iso: str) -> Dict[str, Any]:
    con = _db()
    cur = con.execute("SELECT ts, price_eur_mwh FROM spot WHERE date(ts)=? ORDER BY ts", (date_iso,))
    rows = [dict(ts=r["ts"], price_eur_mwh=r["price_eur_mwh"]) for r in cur.fetchall()]
    return {"date": date_iso, "curve": rows, "points": len(rows)}

@mcp.tool(description="Hole aWATTar/EPEX Viertelstundenpreise als Live-API (Tag in YYYY-MM-DD).")
def prices_get_awattar(day: str, country: str = None) -> Dict[str, Any]:
    base = AWATTAR_BASE_URL if country is None else ( "https://api.awattar.de/v1/marketdata" if country.upper()=="DE" else "https://api.awattar.at/v1/marketdata")
    url = base
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    data = r.json().get("data", [])
    # Clientseitig filtern auf 'day'
    import datetime as dt
    res = []
    for it in data:
        start = dt.datetime.utcfromtimestamp(it["start_timestamp"]/1000).isoformat()
        if start.startswith(day):
            res.append({"ts": start+"Z", "price_eur_mwh": it["marketprice"]/10.0})  # aWATTar returns €/MWh*10?
    return {"day": day, "curve": res, "points": len(res), "source": base}

@mcp.tool(description="Lese letzten SOC-Wert (0-100 %) aus metrics(key='soc').")
def bess_read_soc() -> float:
    con = _db()
    row = con.execute("""SELECT value FROM metrics WHERE key='soc' ORDER BY ts DESC LIMIT 1""").fetchone()
    return float(row["value"]) if row else -1.0

@mcp.tool(description="Setze Betriebsmodus via MQTT. mode in {'idle','charge','discharge'} → Topic bess/cmd/mode")
def bess_set_mode(mode: str) -> str:
    mode = mode.strip().lower()
    assert mode in {"idle","charge","discharge"}, "mode must be one of idle|charge|discharge"
    client = _mqtt()
    client.loop_start()
    info = client.publish("bess/cmd/mode", payload=mode, qos=1, retain=False)
    info.wait_for_publish(timeout=5.0)
    client.loop_stop()
    client.disconnect()
    return "ok"

@mcp.tool(description="Starte echte Dispatch-Simulation (Adapter über ENV: DISPATCH_MODULE/FUNC). Übergabe: JSON.")
def sim_run_dispatch(params_json: str) -> Dict[str, Any]:
    params = json.loads(params_json or "{}")
    fn = _import_dispatch()
    res = fn(params)  # must return dict of KPIs
    # sanity
    assert isinstance(res, dict), "Dispatch function must return dict"
    return res

@mcp.tool(description="Lies PV-/Last-Zeitreihen aus Tabelle pv_load(ts ISO, pv_kw REAL, load_kw REAL) für YYYY-MM-DD.")
def read_pv_load(day: str) -> Dict[str, Any]:
    con = _db()
    cur = con.execute("SELECT ts, pv_kw, load_kw FROM pv_load WHERE date(ts)=? ORDER BY ts", (day,))
    rows = [dict(ts=r["ts"], pv_kw=r["pv_kw"], load_kw=r["load_kw"]) for r in cur.fetchall()]
    return {"day": day, "series": rows, "points": len(rows)}

@mcp.resource("db.project", description="Read-only Tabellen-Dump ('spot','metrics','pv_load').")
def db_project(table: str, limit: int = 200) -> Dict[str, Any]:
    assert table in {"spot","metrics","pv_load"}, "Unsupported table"
    con = _db()
    cur = con.execute(f"SELECT * FROM {table} ORDER BY ts DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in cur.fetchall()]
    return {"table": table, "rows": rows}

if __name__ == "__main__":
    mcp.run_stdio()
