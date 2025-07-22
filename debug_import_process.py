#!/usr/bin/env python3
"""
Debug-Skript für den Import-Prozess
"""

import sqlite3
from datetime import datetime

def debug_import_process():
    """Debuggt den Import-Prozess"""
    
    print("🔍 Debug Import-Prozess...")
    print("=" * 50)
    
    try:
        # Datenbank verbinden
        conn = sqlite3.connect('instance/bess.db')
        cursor = conn.cursor()
        
        print("1. Datenbank-Tabellen prüfen:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        for table in tables:
            print(f"   - {table[0]}")
        
        print("\n2. Lastprofile prüfen:")
        cursor.execute("SELECT * FROM load_profile")
        profiles = cursor.fetchall()
        
        for profile in profiles:
            print(f"   Lastprofil: {profile}")
        
        print("\n3. load_value Tabelle prüfen:")
        cursor.execute("SELECT COUNT(*) FROM load_value")
        count = cursor.fetchone()[0]
        print(f"   Anzahl Datenpunkte: {count}")
        
        if count > 0:
            cursor.execute("SELECT * FROM load_value LIMIT 5")
            values = cursor.fetchall()
            print("   Erste 5 Datenpunkte:")
            for value in values:
                print(f"     {value}")
        
        print("\n4. Tabellen-Struktur prüfen:")
        cursor.execute("PRAGMA table_info(load_value)")
        columns = cursor.fetchall()
        print("   load_value Spalten:")
        for col in columns:
            print(f"     {col[1]} ({col[2]})")
        
        print("\n5. Import-Log prüfen:")
        # Prüfe ob es eine Log-Tabelle gibt
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%log%'")
        log_tables = cursor.fetchall()
        
        if log_tables:
            for log_table in log_tables:
                print(f"   Log-Tabelle gefunden: {log_table[0]}")
                cursor.execute(f"SELECT * FROM {log_table[0]} ORDER BY rowid DESC LIMIT 5")
                logs = cursor.fetchall()
                for log in logs:
                    print(f"     {log}")
        else:
            print("   Keine Log-Tabellen gefunden")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Fehler: {e}")

if __name__ == "__main__":
    debug_import_process() 