#!/usr/bin/env python3
"""
Test-Skript für die Lastprofile-API
"""

import sqlite3
import json

def test_load_profiles_api():
    """Testet die Lastprofile-API direkt"""
    
    print("🔍 Teste Lastprofile-API...")
    print("=" * 50)
    
    try:
        # Datenbank verbinden
        conn = sqlite3.connect('instance/bess.db')
        cursor = conn.cursor()
        
        print("1. Projekte in der Datenbank:")
        cursor.execute("SELECT id, name FROM project")
        projects = cursor.fetchall()
        
        for project in projects:
            print(f"   Projekt {project[0]}: {project[1]}")
        
        print("\n2. Lastprofile in der Datenbank:")
        cursor.execute("""
            SELECT id, name, project_id, created_at 
            FROM load_profile 
            ORDER BY project_id, created_at DESC
        """)
        profiles = cursor.fetchall()
        
        if profiles:
            for profile in profiles:
                print(f"   Lastprofil {profile[0]}: '{profile[1]}' (Projekt {profile[2]}) - {profile[3]}")
        else:
            print("   ❌ Keine Lastprofile gefunden!")
        
        print("\n3. Datenpunkte pro Lastprofil:")
        cursor.execute("""
            SELECT load_profile_id, COUNT(*) as data_points
            FROM load_value 
            GROUP BY load_profile_id
        """)
        data_points = cursor.fetchall()
        
        if data_points:
            for dp in data_points:
                print(f"   Lastprofil {dp[0]}: {dp[1]} Datenpunkte")
        else:
            print("   ❌ Keine Datenpunkte gefunden!")
        
        print("\n4. API-Simulation für Projekt 1:")
        cursor.execute("""
            SELECT id, name, created_at, 
                   (SELECT COUNT(*) FROM load_value WHERE load_profile_id = load_profile.id) as data_points
            FROM load_profile 
            WHERE project_id = 1
            ORDER BY created_at DESC
        """)
        
        api_result = cursor.fetchall()
        print(f"   API würde {len(api_result)} Lastprofile zurückgeben:")
        
        for profile in api_result:
            print(f"   - ID: {profile[0]}, Name: '{profile[1]}', Datenpunkte: {profile[3]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Fehler: {e}")

if __name__ == "__main__":
    test_load_profiles_api() 