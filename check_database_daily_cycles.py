#!/usr/bin/env python3
"""
Script zur direkten Überprüfung der daily_cycles in der Datenbank
"""

import sqlite3
import os

def check_database_daily_cycles():
    """Überprüft die daily_cycles direkt in der Datenbank"""
    
    try:
        # Datenbankpfad
        db_path = 'instance/bess.db'
        
        if not os.path.exists(db_path):
            print(f"❌ Datenbank nicht gefunden: {db_path}")
            return
        
        print(f"🔍 Überprüfe Datenbank: {db_path}")
        
        # Verbindung zur Datenbank
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Prüfe Projekt-Tabelle
        print("\n📊 Projekt-Tabelle:")
        cursor.execute("PRAGMA table_info(project)")
        columns = cursor.fetchall()
        print("Spalten:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # Prüfe daily_cycles für BESS Hinterstoder
        print("\n🔍 BESS Hinterstoder daily_cycles:")
        cursor.execute("SELECT id, name, daily_cycles FROM project WHERE name = 'BESS Hinterstoder'")
        project = cursor.fetchone()
        
        if project:
            print(f"  ID: {project[0]}")
            print(f"  Name: {project[1]}")
            print(f"  daily_cycles: {project[2]} (Typ: {type(project[2])})")
        else:
            print("  ❌ Projekt nicht gefunden")
        
        # Prüfe alle Projekte
        print("\n📋 Alle Projekte:")
        cursor.execute("SELECT id, name, daily_cycles FROM project ORDER BY id")
        projects = cursor.fetchall()
        
        for project in projects:
            print(f"  ID {project[0]}: {project[1]} - daily_cycles: {project[2]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Fehler: {e}")

if __name__ == "__main__":
    check_database_daily_cycles()
