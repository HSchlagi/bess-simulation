#!/usr/bin/env python3
"""
Migration: Aktuelle Stromkosten zur Project Tabelle hinzufügen
"""

import sqlite3
import os

def add_current_electricity_cost_column():
    """Fügt current_electricity_cost Spalte zur Project Tabelle hinzu"""
    
    db_path = 'instance/bess.db'
    
    if not os.path.exists(db_path):
        print("❌ Datenbank nicht gefunden:", db_path)
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Überprüfe current_electricity_cost Spalte...")
        
        # Prüfe ob Spalte bereits existiert
        cursor.execute("PRAGMA table_info(project);")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'current_electricity_cost' in column_names:
            print("✅ Spalte current_electricity_cost existiert bereits")
            return True
        
        print("➕ Füge current_electricity_cost Spalte hinzu...")
        
        # Spalte hinzufügen mit Standardwert 12.5 Ct/kWh
        cursor.execute("""
            ALTER TABLE project 
            ADD COLUMN current_electricity_cost REAL DEFAULT 12.5
        """)
        
        # Bestätige Änderung
        cursor.execute("PRAGMA table_info(project);")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'current_electricity_cost' in column_names:
            print("✅ Spalte current_electricity_cost erfolgreich hinzugefügt")
            
            # Setze Standardwert für bestehende Projekte
            cursor.execute("""
                UPDATE project 
                SET current_electricity_cost = 12.5 
                WHERE current_electricity_cost IS NULL
            """)
            
            updated_rows = cursor.rowcount
            print(f"✅ {updated_rows} bestehende Projekte mit Standardwert 12.5 Ct/kWh aktualisiert")
            
        else:
            print("❌ Fehler beim Hinzufügen der Spalte")
            return False
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Fehler bei der Migration: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starte Migration: Aktuelle Stromkosten")
    success = add_current_electricity_cost_column()
    
    if success:
        print("\n✅ Migration erfolgreich abgeschlossen")
    else:
        print("\n❌ Migration fehlgeschlagen") 