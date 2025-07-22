#!/usr/bin/env python3
"""
Debug-Skript für das Datenproblem
"""

import sqlite3

def debug_data_issue():
    """Debuggt das Datenproblem direkt in der Datenbank"""
    
    print("🔍 Debug Datenproblem...")
    print("=" * 50)
    
    try:
        # Datenbank verbinden
        conn = sqlite3.connect('instance/bess.db')
        cursor = conn.cursor()
        
        print("1. Alle Lastprofile prüfen:")
        cursor.execute("SELECT * FROM load_profile")
        profiles = cursor.fetchall()
        
        for profile in profiles:
            print(f"   Lastprofil: {profile}")
        
        print("\n2. Alle Datenpunkte prüfen:")
        cursor.execute("SELECT * FROM load_value")
        values = cursor.fetchall()
        
        if values:
            print(f"   {len(values)} Datenpunkte gefunden:")
            for value in values[:5]:  # Erste 5 anzeigen
                print(f"     {value}")
        else:
            print("   ❌ Keine Datenpunkte gefunden!")
        
        print("\n3. SQL-Query testen (wie in der API):")
        query = """
        SELECT lv.timestamp, lv.power_kw as value 
        FROM load_value lv
        JOIN load_profile lp ON lv.load_profile_id = lp.id
        WHERE lp.project_id = 1
        ORDER BY lv.timestamp
        """
        
        cursor.execute(query)
        result = cursor.fetchall()
        
        print(f"   API-Query Ergebnis: {len(result)} Datenpunkte")
        if result:
            for row in result[:3]:
                print(f"     {row[0]}: {row[1]} kW")
        else:
            print("   ❌ API-Query findet keine Daten!")
        
        print("\n4. Tabellen-Struktur prüfen:")
        cursor.execute("PRAGMA table_info(load_value)")
        columns = cursor.fetchall()
        print("   load_value Spalten:")
        for col in columns:
            print(f"     {col[1]} ({col[2]})")
        
        cursor.execute("PRAGMA table_info(load_profile)")
        columns = cursor.fetchall()
        print("   load_profile Spalten:")
        for col in columns:
            print(f"     {col[1]} ({col[2]})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Fehler: {e}")

if __name__ == "__main__":
    debug_data_issue() 