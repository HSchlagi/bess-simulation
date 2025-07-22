#!/usr/bin/env python3
"""
Debug-Skript für das Datenimport-Problem
"""

import sqlite3
import os

def debug_import():
    """Debuggt das Datenimport-Problem"""
    
    db_path = 'instance/bess.db'
    
    if not os.path.exists(db_path):
        print("❌ Datenbank nicht gefunden!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Debug: Datenimport-Problem analysieren...")
        print("=" * 60)
        
        # 1. Lastprofile prüfen
        print("1. Lastprofile:")
        cursor.execute("SELECT id, name, project_id, created_at FROM load_profile")
        profiles = cursor.fetchall()
        
        for profile in profiles:
            profile_id, name, project_id, created_at = profile
            print(f"   - ID: {profile_id}, Name: '{name}', Projekt: {project_id}")
            
            # Datenpunkte für dieses Profil
            cursor.execute("SELECT COUNT(*) FROM load_value WHERE load_profile_id = ?", (profile_id,))
            count = cursor.fetchone()[0]
            print(f"     Datenpunkte: {count}")
        
        print()
        
        # 2. Load Values prüfen
        print("2. Load Values:")
        cursor.execute("SELECT COUNT(*) FROM load_value")
        total_values = cursor.fetchone()[0]
        print(f"   Gesamte Load Values: {total_values}")
        
        if total_values > 0:
            cursor.execute("SELECT load_profile_id, COUNT(*) FROM load_value GROUP BY load_profile_id")
            for profile_id, count in cursor.fetchall():
                print(f"   - Profil {profile_id}: {count} Werte")
        
        print()
        
        # 3. Tabellen-Struktur prüfen
        print("3. Tabellen-Struktur:")
        cursor.execute("PRAGMA table_info(load_profile)")
        print("   load_profile Spalten:")
        for col in cursor.fetchall():
            print(f"     - {col[1]} ({col[2]})")
        
        cursor.execute("PRAGMA table_info(load_value)")
        print("   load_value Spalten:")
        for col in cursor.fetchall():
            print(f"     - {col[1]} ({col[2]})")
        
        print()
        
        # 4. Letzte Einträge prüfen
        print("4. Letzte Einträge:")
        cursor.execute("SELECT * FROM load_profile ORDER BY created_at DESC LIMIT 3")
        print("   Letzte 3 Lastprofile:")
        for row in cursor.fetchall():
            print(f"     {row}")
        
        if total_values > 0:
            cursor.execute("SELECT * FROM load_value ORDER BY created_at DESC LIMIT 3")
            print("   Letzte 3 Load Values:")
            for row in cursor.fetchall():
                print(f"     {row}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Fehler beim Debugging: {e}")

if __name__ == "__main__":
    debug_import() 