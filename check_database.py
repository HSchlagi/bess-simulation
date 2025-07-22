#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

def check_database():
    """Prüft die Datenbank auf vorhandene Daten"""
    
    db_path = 'instance/bess.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Datenbank nicht gefunden: {db_path}")
        return
    
    print(f"✅ Datenbank gefunden: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Tabellen auflisten
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"\n📋 Verfügbare Tabellen:")
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  - {table_name}: {count} Einträge")
        
        # Projekte prüfen
        print(f"\n🏗️ Projekte:")
        cursor.execute("SELECT id, name FROM projects")
        projects = cursor.fetchall()
        for project in projects:
            print(f"  - ID {project[0]}: {project[1]}")
        
        # Lastprofile prüfen
        print(f"\n⚡ Lastprofile:")
        cursor.execute("SELECT id, name, project_id FROM load_profiles")
        load_profiles = cursor.fetchall()
        for profile in load_profiles:
            print(f"  - ID {profile[0]}: {profile[1]} (Projekt ID: {profile[2]})")
        
        # Load Values prüfen
        print(f"\n📊 Load Values:")
        cursor.execute("SELECT COUNT(*) FROM load_values")
        count = cursor.fetchone()[0]
        print(f"  - Gesamt: {count} Werte")
        
        if count > 0:
            cursor.execute("SELECT load_profile_id, COUNT(*) FROM load_values GROUP BY load_profile_id")
            profile_counts = cursor.fetchall()
            for profile_id, count in profile_counts:
                print(f"  - Lastprofil ID {profile_id}: {count} Werte")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Fehler beim Prüfen der Datenbank: {e}")

if __name__ == "__main__":
    check_database() 