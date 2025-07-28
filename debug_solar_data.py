#!/usr/bin/env python3
"""
Debug-Skript für Solar-Daten
"""

import sqlite3
import pandas as pd

def debug_solar_data():
    """Debug Solar-Daten in der Datenbank"""
    
    db_path = "instance/bess.db"
    
    try:
        conn = sqlite3.connect(db_path)
        
        # Prüfe Tabellen
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("📋 Verfügbare Tabellen:")
        for table in tables:
            print(f"   - {table[0]}")
        
        # Prüfe solar_data Tabelle
        if ('solar_data',) in tables:
            print("\n🔍 Solar_data Tabelle Schema:")
            cursor.execute("PRAGMA table_info(solar_data)")
            columns = cursor.fetchall()
            for col in columns:
                print(f"   - {col[1]} ({col[2]})")
            
            # Prüfe Daten
            print("\n📊 Solar-Daten in der Datenbank:")
            df = pd.read_sql_query("SELECT * FROM solar_data LIMIT 10", conn)
            if not df.empty:
                print(f"   ✅ {len(df)} Zeilen gefunden")
                print("   Erste Zeilen:")
                print(df.head())
                
                # Prüfe location_key Werte
                print("\n📍 Verfügbare location_key Werte:")
                cursor.execute("SELECT DISTINCT location_key FROM solar_data")
                locations = cursor.fetchall()
                for loc in locations:
                    print(f"   - {loc[0]}")
                    
                # Prüfe Jahr Werte
                print("\n📅 Verfügbare Jahr Werte:")
                cursor.execute("SELECT DISTINCT year FROM solar_data")
                years = cursor.fetchall()
                for year in years:
                    print(f"   - {year[0]}")
            else:
                print("   ❌ Keine Daten gefunden")
        else:
            print("❌ Solar_data Tabelle nicht gefunden")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Fehler: {e}")

if __name__ == "__main__":
    debug_solar_data() 