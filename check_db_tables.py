#!/usr/bin/env python3
"""Überprüft die Datenbank-Tabellen"""

import sqlite3

def check_tables():
    try:
        conn = sqlite3.connect('instance/bess.db')
        cursor = conn.cursor()
        
        # Alle Tabellen anzeigen
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print("📋 Vorhandene Tabellen:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Dispatch-Tabellen prüfen
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%dispatch%'")
        dispatch_tables = cursor.fetchall()
        print(f"\n🔄 Dispatch-Tabellen: {dispatch_tables}")
        
        # APG-Tabellen prüfen
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%apg%'")
        apg_tables = cursor.fetchall()
        print(f"📊 APG-Tabellen: {apg_tables}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False

if __name__ == "__main__":
    check_tables()