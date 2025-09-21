#!/usr/bin/env python3
"""
BESS-Simulation MCP Server (Einfache Version)
Intelligente Integration mit bestehender BESS-Architektur
"""

import os
import sys
import json
import sqlite3
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

# BESS-Simulation Pfad hinzufügen
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Konfiguration
DB_PATH = os.getenv("BESS_DB_PATH", "instance/bess.db")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

def test_tools():
    """Teste alle MCP-Tools"""
    print("🧪 Teste BESS MCP Tools...")
    
    # Test Spotpreise
    print("\n1. Teste Spotpreise (heute):")
    today = datetime.now().strftime("%Y-%m-%d")
    result = prices_get_spotcurve(today)
    print(f"   Ergebnis: {len(result.get('curve', []))} Datenpunkte")
    
    # Test aWATTar
    print("\n2. Teste aWATTar API:")
    result = prices_get_awattar(today)
    print(f"   Ergebnis: {len(result.get('curve', []))} Datenpunkte")
    
    # Test SOC
    print("\n3. Teste SOC-Lesung:")
    soc = bess_read_soc()
    print(f"   SOC: {soc}%")
    
    # Test PV/Load
    print("\n4. Teste PV/Load-Daten:")
    result = read_pv_load(today)
    print(f"   Ergebnis: {len(result.get('series', []))} Datenpunkte")
    
    # Test Datenbank
    print("\n5. Teste Datenbank-Tabellen:")
    result = db_project("projects", 5)
    print(f"   Projekte: {result.get('count', 0)} gefunden")
    
    print("\n✅ Alle Tests abgeschlossen!")

def main():
    """Hauptfunktion für MCP-Server"""
    print("BESS-Simulation MCP Server (Einfache Version)")
    print(f"Datenbank: {DB_PATH}")
    
    # Test der Datenbankverbindung
    con = _db()
    if con:
        print("✅ Datenbankverbindung erfolgreich")
        con.close()
    else:
        print("❌ Datenbankverbindung fehlgeschlagen")
        return
    
    # Tools testen
    test_tools()
    
    print("\n🔧 MCP-Server bereit für Integration mit Cursor AI")
    print("Verwende diese Funktionen in deinem Code:")
    print("- prices_get_spotcurve(date_iso)")
    print("- prices_get_awattar(day, country)")
    print("- bess_read_soc()")
    print("- read_pv_load(day)")
    print("- db_project(table, limit)")

if __name__ == "__main__":
    main()

