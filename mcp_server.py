#!/usr/bin/env python3
"""
BESS-Simulation MCP Server
Intelligente Integration mit bestehender BESS-Architektur

Features:
- Nutzt bestehende instance/bess.db
- Integration mit aWATTar/APG APIs
- MQTT-Integration für Hardware-Steuerung
- Pluggable Dispatch-Adapter
- Cursor AI optimiert
"""

import os
import sys
import json
import sqlite3
import time
import importlib
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

# BESS-Simulation Pfad hinzufügen
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from mcp.server.fastmcp import FastMCP
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("Warnung: MCP nicht verfügbar. Installiere mit: pip install mcp")

try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False
    print("Warnung: paho-mqtt nicht verfügbar")

# Konfiguration
DB_PATH = os.getenv("BESS_DB_PATH", "instance/bess.db")
MQTT_HOST = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")

# Dispatch-Adapter Konfiguration
DISPATCH_MODULE = os.getenv("DISPATCH_MODULE", "app.mcp_dispatch_adapter")
DISPATCH_FUNC = os.getenv("DISPATCH_FUNC", "run_dispatch")

# API-Konfiguration
AWATTAR_BASE_URL = os.getenv("AWATTAR_BASE_URL", "https://api.awattar.at/v1/marketdata")
APG_BASE_URL = os.getenv("APG_BASE_URL", "https://api.apg.at/v1")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if MCP_AVAILABLE:
    mcp = FastMCP("bess-simulation")
else:
    mcp = None

def _db():
    """Datenbankverbindung zur BESS-Simulation DB"""
    if not os.path.exists(DB_PATH):
        logger.warning(f"Datenbank nicht gefunden: {DB_PATH}")
        return None
    
    try:
        con = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
        con.row_factory = sqlite3.Row
        return con
    except Exception as e:
        logger.error(f"Fehler beim Verbinden zur Datenbank: {e}")
        return None

def _mqtt():
    """MQTT-Client für Hardware-Steuerung"""
    if not MQTT_AVAILABLE:
        raise RuntimeError("paho-mqtt nicht installiert")
    
    client = mqtt.Client()
    if MQTT_USERNAME:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD or "")
    
    try:
        client.connect(MQTT_HOST, MQTT_PORT, keepalive=30)
        return client
    except Exception as e:
        logger.error(f"Fehler beim Verbinden zu MQTT: {e}")
        raise

def _import_dispatch():
    """Lade Dispatch-Adapter dynamisch"""
    try:
        mod = importlib.import_module(DISPATCH_MODULE)
        fn = getattr(mod, DISPATCH_FUNC)
        return fn
    except Exception as e:
        logger.error(f"Fehler beim Laden des Dispatch-Adapters: {e}")
        return None

# ==================== MCP TOOLS ====================

def prices_get_spotcurve(date_iso: str) -> Dict[str, Any]:
    """Hole Spotpreise aus BESS-Datenbank"""
    con = _db()
    if not con:
        return {"error": "Datenbank nicht verfügbar"}
    
    try:
        cur = con.execute("""
            SELECT ts, price_eur_mwh 
            FROM spot_prices 
            WHERE date(ts) = ? 
            ORDER BY ts
        """, (date_iso,))
        
        rows = [dict(ts=r["ts"], price_eur_mwh=r["price_eur_mwh"]) for r in cur.fetchall()]
        con.close()
        
        return {
            "date": date_iso,
            "curve": rows,
            "points": len(rows),
            "source": "bess_database"
        }
    except Exception as e:
        logger.error(f"Fehler beim Laden der Spotpreise: {e}")
        return {"error": str(e)}

def prices_get_awattar(day: str, country: str = "AT") -> Dict[str, Any]:
    """Hole aWATTar Live-Preise"""
    try:
        base_url = "https://api.awattar.de/v1/marketdata" if country.upper() == "DE" else "https://api.awattar.at/v1/marketdata"
        
        response = requests.get(base_url, timeout=15)
        response.raise_for_status()
        data = response.json().get("data", [])
        
        # Filtere auf gewünschten Tag
        filtered_data = []
        for item in data:
            start_time = datetime.utcfromtimestamp(item["start_timestamp"] / 1000)
            if start_time.strftime("%Y-%m-%d") == day:
                filtered_data.append({
                    "ts": start_time.isoformat() + "Z",
                    "price_eur_mwh": item["marketprice"] / 10.0
                })
        
        return {
            "day": day,
            "curve": filtered_data,
            "points": len(filtered_data),
            "source": base_url,
            "country": country.upper()
        }
    except Exception as e:
        logger.error(f"Fehler beim Laden der aWATTar-Daten: {e}")
        return {"error": str(e)}

def bess_read_soc() -> float:
    """Lese aktuellen SOC-Wert"""
    con = _db()
    if not con:
        return -1.0
    
    try:
        # Suche in verschiedenen möglichen Tabellen
        tables_to_check = ["metrics", "battery_status", "system_status"]
        
        for table in tables_to_check:
            try:
                cur = con.execute(f"""
                    SELECT value FROM {table} 
                    WHERE key = 'soc' OR parameter = 'soc'
                    ORDER BY timestamp DESC LIMIT 1
                """)
                row = cur.fetchone()
                if row:
                    con.close()
                    return float(row[0])
            except:
                continue
        
        con.close()
        return -1.0
    except Exception as e:
        logger.error(f"Fehler beim Lesen des SOC: {e}")
        return -1.0

def bess_set_mode(mode: str) -> str:
    """Setze BESS-Betriebsmodus via MQTT"""
    mode = mode.strip().lower()
    if mode not in {"idle", "charge", "discharge"}:
        return "error: mode muss idle, charge oder discharge sein"
    
    try:
        client = _mqtt()
        client.loop_start()
        
        # MQTT-Topic für BESS-Steuerung
        topic = "bess/cmd/mode"
        info = client.publish(topic, payload=mode, qos=1, retain=False)
        
        if info.wait_for_publish(timeout=5.0):
            client.loop_stop()
            client.disconnect()
            return f"ok: Modus '{mode}' gesetzt"
        else:
            client.loop_stop()
            client.disconnect()
            return "error: MQTT-Publish fehlgeschlagen"
            
    except Exception as e:
        logger.error(f"Fehler beim Setzen des BESS-Modus: {e}")
        return f"error: {str(e)}"

def sim_run_dispatch(params_json: str) -> Dict[str, Any]:
    """Starte BESS-Dispatch-Simulation"""
    try:
        params = json.loads(params_json or "{}")
        dispatch_func = _import_dispatch()
        
        if not dispatch_func:
            return {
                "error": "Dispatch-Adapter nicht verfügbar",
                "status": "error"
            }
        
        result = dispatch_func(params)
        return result
        
    except json.JSONDecodeError as e:
        return {"error": f"Ungültige JSON-Parameter: {e}", "status": "error"}
    except Exception as e:
        logger.error(f"Fehler beim Ausführen des Dispatch: {e}")
        return {"error": str(e), "status": "error"}

def read_pv_load(day: str) -> Dict[str, Any]:
    """Lese PV/Last-Zeitreihen"""
    con = _db()
    if not con:
        return {"error": "Datenbank nicht verfügbar"}
    
    try:
        # Suche in verschiedenen möglichen Tabellen
        tables_to_check = ["pv_load", "load_profiles", "solar_data"]
        
        for table in tables_to_check:
            try:
                cur = con.execute(f"""
                    SELECT ts, pv_kw, load_kw 
                    FROM {table} 
                    WHERE date(ts) = ? 
                    ORDER BY ts
                """, (day,))
                
                rows = [dict(ts=r["ts"], pv_kw=r["pv_kw"], load_kw=r["load_kw"]) for r in cur.fetchall()]
                if rows:
                    con.close()
                    return {
                        "day": day,
                        "series": rows,
                        "points": len(rows),
                        "source": f"bess_database.{table}"
                    }
            except:
                continue
        
        con.close()
        return {"day": day, "series": [], "points": 0, "error": "Keine PV/Last-Daten gefunden"}
        
    except Exception as e:
        logger.error(f"Fehler beim Lesen der PV/Last-Daten: {e}")
        return {"error": str(e)}

def db_project(table: str, limit: int = 200) -> Dict[str, Any]:
    """Datenbank-Tabellen-Dump"""
    if table not in {"spot_prices", "metrics", "pv_load", "projects", "battery_configs"}:
        return {"error": f"Tabelle '{table}' nicht unterstützt"}
    
    con = _db()
    if not con:
        return {"error": "Datenbank nicht verfügbar"}
    
    try:
        cur = con.execute(f"SELECT * FROM {table} ORDER BY id DESC LIMIT ?", (limit,))
        rows = [dict(r) for r in cur.fetchall()]
        con.close()
        
        return {
            "table": table,
            "rows": rows,
            "count": len(rows)
        }
    except Exception as e:
        logger.error(f"Fehler beim Lesen der Tabelle {table}: {e}")
        return {"error": str(e)}

# ==================== MCP REGISTRATION ====================

if MCP_AVAILABLE and mcp:
    # Tools registrieren
    mcp.tool(description="Hole Spotpreise (EUR/MWh) für YYYY-MM-DD aus BESS-Datenbank")(prices_get_spotcurve)
    mcp.tool(description="Hole aWATTar/EPEX Live-Preise für Tag (AT/DE)")(prices_get_awattar)
    mcp.tool(description="Lese aktuellen SOC-Wert (0-100%) aus BESS-System")(bess_read_soc)
    mcp.tool(description="Setze BESS-Betriebsmodus via MQTT (idle/charge/discharge)")(bess_set_mode)
    mcp.tool(description="Starte BESS-Dispatch-Simulation mit Parametern")(sim_run_dispatch)
    mcp.tool(description="Lese PV/Last-Zeitreihen aus BESS-Datenbank")(read_pv_load)
    mcp.tool(description="Datenbank-Tabellen-Dump für BESS-Projekte")(db_project)
    
    # Resources registrieren (ohne Parameter-Konflikt)
    # mcp.resource("bess.database", description="BESS-Simulation Datenbank-Zugriff")(db_project)

def main():
    """Hauptfunktion für MCP-Server"""
    if not MCP_AVAILABLE:
        print("Fehler: MCP nicht verfügbar. Installiere mit: pip install mcp")
        return
    
    print("BESS-Simulation MCP Server startet...")
    print(f"Datenbank: {DB_PATH}")
    print(f"Dispatch-Adapter: {DISPATCH_MODULE}.{DISPATCH_FUNC}")
    
    # Test der Datenbankverbindung
    con = _db()
    if con:
        print("✅ Datenbankverbindung erfolgreich")
        con.close()
    else:
        print("❌ Datenbankverbindung fehlgeschlagen")
    
    # MCP-Server starten
    mcp.run_stdio()

if __name__ == "__main__":
    main()
