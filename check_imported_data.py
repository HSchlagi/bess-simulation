#!/usr/bin/env python3
"""
Skript zum Prüfen der importierten Lastprofile in der Datenbank
"""

import sqlite3
import os
from datetime import datetime

def check_imported_data():
    """Prüft die importierten Lastprofile in der Datenbank"""
    
    db_path = 'instance/bess.db'
    
    if not os.path.exists(db_path):
        print("❌ Datenbank nicht gefunden!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Prüfe importierte Lastprofile...")
        print("=" * 50)
        
        # Alle Lastprofile abrufen
        cursor.execute("""
            SELECT id, name, project_id, created_at 
            FROM load_profile 
            ORDER BY created_at DESC
        """)
        
        profiles = cursor.fetchall()
        
        if not profiles:
            print("❌ Keine Lastprofile in der Datenbank gefunden!")
            return
        
        print(f"✅ {len(profiles)} Lastprofile gefunden:")
        print()
        
        for profile in profiles:
            profile_id, name, project_id, created_at = profile
            
            # Anzahl Datenpunkte für dieses Profil
            cursor.execute("""
                SELECT COUNT(*) FROM load_value WHERE load_profile_id = ?
            """, (profile_id,))
            data_points = cursor.fetchone()[0]
            
            # Projekt-Name
            cursor.execute("SELECT name FROM project WHERE id = ?", (project_id,))
            project_name = cursor.fetchone()
            project_name = project_name[0] if project_name else "Unbekannt"
            
            print(f"📊 Profil ID: {profile_id}")
            print(f"   Name: {name}")
            print(f"   Projekt: {project_name} (ID: {project_id})")
            print(f"   Datenpunkte: {data_points}")
            print(f"   Erstellt: {created_at}")
            
            # Erste und letzte Datenpunkte
            if data_points > 0:
                cursor.execute("""
                    SELECT timestamp, value FROM load_value 
                    WHERE load_profile_id = ? 
                    ORDER BY timestamp ASC 
                    LIMIT 1
                """, (profile_id,))
                first_point = cursor.fetchone()
                
                cursor.execute("""
                    SELECT timestamp, value FROM load_value 
                    WHERE load_profile_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT 1
                """, (profile_id,))
                last_point = cursor.fetchone()
                
                if first_point and last_point:
                    print(f"   Zeitraum: {first_point[0]} bis {last_point[0]}")
                    print(f"   Wertebereich: {first_point[1]} - {last_point[1]} kW")
            
            print("-" * 40)
        
        # Gesamtstatistik
        cursor.execute("SELECT COUNT(*) FROM load_value")
        total_data_points = cursor.fetchone()[0]
        
        print(f"📈 Gesamtstatistik:")
        print(f"   Lastprofile: {len(profiles)}")
        print(f"   Gesamte Datenpunkte: {total_data_points}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Fehler beim Prüfen der Datenbank: {e}")

if __name__ == "__main__":
    check_imported_data() 