#!/usr/bin/env python3
"""
Datenbank-Struktur-Überprüfung für Lastprofile-Tabellen
"""

import sqlite3
import os

def check_database_structure():
    """Überprüft die Struktur der Lastprofile-Tabellen"""
    
    db_path = 'instance/bess.db'
    
    if not os.path.exists(db_path):
        print("❌ Datenbank nicht gefunden:", db_path)
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Überprüfe Datenbank-Struktur...")
        
        # Alle Tabellen auflisten
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("\n📋 Verfügbare Tabellen:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Lastprofile-relevante Tabellen detailliert prüfen
        load_tables = ['load_profile', 'load_profiles', 'load_value', 'load_profile_data']
        
        for table_name in load_tables:
            print(f"\n🔍 Tabelle: {table_name}")
            try:
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                
                if columns:
                    print(f"  ✅ Tabelle existiert mit {len(columns)} Spalten:")
                    for col in columns:
                        print(f"    - {col[1]} ({col[2]})")
                else:
                    print(f"  ❌ Tabelle existiert nicht oder ist leer")
                    
            except sqlite3.OperationalError as e:
                print(f"  ❌ Fehler beim Prüfen der Tabelle: {e}")
        
        # Beispieldaten prüfen
        print(f"\n📊 Beispieldaten:")
        
        for table_name in load_tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"  - {table_name}: {count} Einträge")
                
                if count > 0:
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
                    sample = cursor.fetchone()
                    print(f"    Beispiel: {sample}")
                    
            except sqlite3.OperationalError:
                print(f"  - {table_name}: Tabelle nicht verfügbar")
        
        # Detaillierte Analyse der neuen Tabellen
        print(f"\n🔍 DETAILLIERTE ANALYSE:")
        
        # load_profiles Tabelle
        print(f"\n📋 load_profiles Tabelle:")
        try:
            cursor.execute("PRAGMA table_info(load_profiles);")
            columns = cursor.fetchall()
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
        except:
            print("  ❌ Tabelle nicht verfügbar")
        
        # load_profile_data Tabelle
        print(f"\n📋 load_profile_data Tabelle:")
        try:
            cursor.execute("PRAGMA table_info(load_profile_data);")
            columns = cursor.fetchall()
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
        except:
            print("  ❌ Tabelle nicht verfügbar")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Fehler bei der Datenbank-Überprüfung: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starte Datenbank-Struktur-Überprüfung")
    success = check_database_structure()
    
    if success:
        print("\n✅ Datenbank-Überprüfung abgeschlossen")
    else:
        print("\n❌ Datenbank-Überprüfung fehlgeschlagen") 