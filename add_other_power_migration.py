#!/usr/bin/env python3
"""
Migration: Fügt other_power Feld zur Project-Tabelle hinzu
"""

import sqlite3
import os

def add_other_power_column():
    """Fügt other_power Spalte zur Project-Tabelle hinzu"""
    
    db_path = 'instance/bess.db'
    
    if not os.path.exists(db_path):
        print("❌ Datenbank nicht gefunden:", db_path)
        return False
    
    try:
        # Datenbankverbindung
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Prüfen ob Spalte bereits existiert
        cursor.execute("PRAGMA table_info(project)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'other_power' in columns:
            print("✅ other_power Spalte existiert bereits")
            return True
        
        # Spalte hinzufügen
        print("🔄 Füge other_power Spalte hinzu...")
        cursor.execute("ALTER TABLE project ADD COLUMN other_power REAL")
        
        # Änderungen speichern
        conn.commit()
        print("✅ other_power Spalte erfolgreich hinzugefügt")
        
        # Verifikation
        cursor.execute("PRAGMA table_info(project)")
        columns = [column[1] for column in cursor.fetchall()]
        print("📋 Verfügbare Spalten:", columns)
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Hinzufügen der Spalte: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starte Migration: other_power Spalte hinzufügen")
    success = add_other_power_column()
    
    if success:
        print("✅ Migration erfolgreich abgeschlossen")
    else:
        print("❌ Migration fehlgeschlagen") 