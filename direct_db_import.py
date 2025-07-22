#!/usr/bin/env python3
"""
Direkter Datenbank-Import für Test
"""

import sqlite3
from datetime import datetime

def direct_db_import():
    """Importiert Test-Daten direkt in die Datenbank"""
    
    print("🔍 Direkter Datenbank-Import...")
    print("=" * 50)
    
    try:
        # Datenbank verbinden
        conn = sqlite3.connect('instance/bess.db')
        cursor = conn.cursor()
        
        print("1. Vorherige Daten prüfen:")
        cursor.execute("SELECT COUNT(*) FROM load_value")
        before_count = cursor.fetchone()[0]
        print(f"   Datenpunkte vor Import: {before_count}")
        
        # Neues Lastprofil erstellen
        profile_name = "Test-Lastprofil 2024"
        print(f"\n2. Erstelle Lastprofil: {profile_name}")
        
        cursor.execute("""
            INSERT INTO load_profile (project_id, name, description, type, interval_minutes, created_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        """, (1, profile_name, "Test-Lastprofil mit 2024-Daten", "load", 15))
        
        load_profile_id = cursor.lastrowid
        print(f"   Lastprofil erstellt mit ID: {load_profile_id}")
        
        # Test-Daten einfügen
        test_data = [
            ('2024-02-21 12:07:12', 53.50),
            ('2024-03-30 03:50:24', 90.16),
            ('2024-04-09 10:33:36', 100.44),
            ('2024-02-13 22:48:00', 45.95),
            ('2024-02-21 23:52:48', 54.00)
        ]
        
        print(f"\n3. Füge {len(test_data)} Test-Datenpunkte ein:")
        
        for timestamp, value in test_data:
            cursor.execute("""
                INSERT INTO load_value (load_profile_id, timestamp, power_kw, created_at)
                VALUES (?, ?, ?, datetime('now'))
            """, (load_profile_id, timestamp, value))
            print(f"   - {timestamp}: {value} kW")
        
        # Commit
        conn.commit()
        print(f"\n4. Änderungen gespeichert")
        
        # Nachherige Daten prüfen
        cursor.execute("SELECT COUNT(*) FROM load_value")
        after_count = cursor.fetchone()[0]
        print(f"   Datenpunkte nach Import: {after_count}")
        print(f"   Neue Datenpunkte: {after_count - before_count}")
        
        # Lastprofile prüfen
        cursor.execute("""
            SELECT id, name, 
                   (SELECT COUNT(*) FROM load_value WHERE load_profile_id = load_profile.id) as data_points
            FROM load_profile 
            WHERE project_id = 1
            ORDER BY created_at DESC
        """)
        
        profiles = cursor.fetchall()
        print(f"\n5. Lastprofile in Projekt 1:")
        for profile in profiles:
            print(f"   - ID: {profile[0]}, Name: '{profile[1]}', Datenpunkte: {profile[2]}")
        
        conn.close()
        print(f"\n✅ Import erfolgreich!")
        
    except Exception as e:
        print(f"❌ Fehler: {e}")

if __name__ == "__main__":
    direct_db_import() 