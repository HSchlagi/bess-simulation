#!/usr/bin/env python3
"""
Test-Script für BatteryConfig Integration
"""

import sqlite3
import os

def test_battery_config_table():
    """Testet ob die BatteryConfig Tabelle existiert"""
    
    db_path = 'instance/bess.db'
    
    if not os.path.exists(db_path):
        print("❌ Datenbank nicht gefunden:", db_path)
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Prüfe ob Tabelle existiert
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='battery_config'
        """)
        
        table_exists = cursor.fetchone() is not None
        print(f"✅ BatteryConfig Tabelle existiert: {table_exists}")
        
        if table_exists:
            # Prüfe Struktur
            cursor.execute("PRAGMA table_info(battery_config)")
            columns = cursor.fetchall()
            print(f"📋 Spalten: {len(columns)}")
            for col in columns:
                print(f"   - {col[1]} ({col[2]})")
            
            # Prüfe Daten
            cursor.execute("SELECT COUNT(*) FROM battery_config")
            count = cursor.fetchone()[0]
            print(f"📊 Datensätze: {count}")
            
            if count > 0:
                cursor.execute("SELECT project_id, E_nom_kWh, C_chg_rate, C_dis_rate FROM battery_config LIMIT 3")
                rows = cursor.fetchall()
                print("📝 Beispiel-Daten:")
                for row in rows:
                    print(f"   - Projekt {row[0]}: {row[1]} kWh, C_chg={row[2]}, C_dis={row[3]}")
        
        conn.close()
        return table_exists
        
    except Exception as e:
        print(f"❌ Fehler beim Testen: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Teste BatteryConfig Integration...")
    success = test_battery_config_table()
    
    if success:
        print("✅ BatteryConfig Integration erfolgreich!")
    else:
        print("❌ BatteryConfig Integration fehlgeschlagen!")
