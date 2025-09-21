#!/usr/bin/env python3
"""
MCP-Tools Test Script
Testet alle MCP-Funktionen ohne MCP-Server
"""

import os
import sys
import json
import sqlite3
from datetime import datetime, timedelta

# BESS-Simulation Pfad hinzufügen
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def _db():
    """Datenbankverbindung zur BESS-Simulation DB"""
    db_path = "instance/bess.db"
    if not os.path.exists(db_path):
        print(f"❌ Datenbank nicht gefunden: {db_path}")
        return None
    
    try:
        con = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        con.row_factory = sqlite3.Row
        return con
    except Exception as e:
        print(f"❌ Fehler beim Verbinden zur Datenbank: {e}")
        return None

def test_prices_get_spotcurve(date_iso: str):
    """Test: Spotpreise aus BESS-Datenbank"""
    print(f"\n🔍 Test: Spotpreise für {date_iso}")
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
        
        result = {
            "date": date_iso,
            "curve": rows,
            "points": len(rows),
            "source": "bess_database"
        }
        print(f"✅ {len(rows)} Spotpreise gefunden")
        return result
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return {"error": str(e)}

def test_bess_read_soc():
    """Test: SOC-Wert lesen"""
    print(f"\n🔍 Test: SOC-Wert lesen")
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
                    print(f"✅ SOC gefunden: {float(row[0])}%")
                    return float(row[0])
            except:
                continue
        
        con.close()
        print("⚠️ Kein SOC-Wert gefunden")
        return -1.0
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return -1.0

def test_sim_run_dispatch(params):
    """Test: Dispatch-Simulation"""
    print(f"\n🔍 Test: Dispatch-Simulation")
    try:
        from app.mcp_dispatch_adapter import run_dispatch
        result = run_dispatch(params)
        print("✅ Dispatch-Simulation erfolgreich")
        return result
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return {"error": str(e)}

def test_read_pv_load(day: str):
    """Test: PV/Last-Zeitreihen"""
    print(f"\n🔍 Test: PV/Last-Daten für {day}")
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
                    result = {
                        "day": day,
                        "series": rows,
                        "points": len(rows),
                        "source": f"bess_database.{table}"
                    }
                    print(f"✅ {len(rows)} PV/Last-Daten gefunden in {table}")
                    return result
            except:
                continue
        
        con.close()
        print("⚠️ Keine PV/Last-Daten gefunden")
        return {"day": day, "series": [], "points": 0, "error": "Keine PV/Last-Daten gefunden"}
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return {"error": str(e)}

def test_db_project(table: str, limit: int = 5):
    """Test: Datenbank-Tabellen-Dump"""
    print(f"\n🔍 Test: Datenbank-Tabelle {table}")
    if table not in {"spot_prices", "metrics", "pv_load", "projects", "battery_configs"}:
        print(f"❌ Tabelle '{table}' nicht unterstützt")
        return {"error": f"Tabelle '{table}' nicht unterstützt"}
    
    con = _db()
    if not con:
        return {"error": "Datenbank nicht verfügbar"}
    
    try:
        cur = con.execute(f"SELECT * FROM {table} ORDER BY id DESC LIMIT ?", (limit,))
        rows = [dict(r) for r in cur.fetchall()]
        con.close()
        
        result = {
            "table": table,
            "rows": rows,
            "count": len(rows)
        }
        print(f"✅ {len(rows)} Zeilen aus {table} gelesen")
        return result
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return {"error": str(e)}

def main():
    """Hauptfunktion für MCP-Tools Test"""
    print("🚀 BESS-Simulation MCP-Tools Test")
    print("=" * 50)
    
    # Test 1: Spotpreise
    spot_result = test_prices_get_spotcurve("2025-09-21")
    print(f"Spotpreise: {spot_result.get('points', 0)} Punkte")
    
    # Test 2: SOC-Wert
    soc = test_bess_read_soc()
    print(f"SOC: {soc}%")
    
    # Test 3: Dispatch-Simulation
    dispatch_params = {
        "capacity_mwh": 0.5,
        "price_spread_eur_mwh": 100,
        "cycles_limit_per_day": 1.5
    }
    dispatch_result = test_sim_run_dispatch(dispatch_params)
    print(f"Dispatch Profit: {dispatch_result.get('profit_eur', 0)} EUR")
    
    # Test 4: PV/Last-Daten
    pv_result = test_read_pv_load("2025-09-21")
    print(f"PV/Last: {pv_result.get('points', 0)} Punkte")
    
    # Test 5: Datenbank-Tabellen
    db_result = test_db_project("projects", 3)
    print(f"Datenbank: {db_result.get('count', 0)} Projekte")
    
    print("\n" + "=" * 50)
    print("✅ MCP-Tools Test abgeschlossen!")
    print("\n📋 Nächste Schritte:")
    print("1. Cursor MCP konfigurieren (cursor_mcp_config.json)")
    print("2. MCP-Server starten: python mcp_server.py")
    print("3. In Cursor AI testen:")
    print("   - 'Hole Spotpreise für heute'")
    print("   - 'Starte BESS-Dispatch mit 0.5 MWh'")
    print("   - 'Zeige mir den aktuellen SOC'")

if __name__ == "__main__":
    main()

