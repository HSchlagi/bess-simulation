#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migration: Fügt daily_cycles Feld zur Project-Tabelle hinzu
"""

import sqlite3
import os

def add_daily_cycles_column():
    """Fügt daily_cycles Spalte zur project Tabelle hinzu"""
    
    db_path = 'instance/bess.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Datenbank nicht gefunden: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Prüfen ob Spalte bereits existiert
        cursor.execute("PRAGMA table_info(project)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'daily_cycles' in columns:
            print("✅ daily_cycles Spalte existiert bereits")
            return True
        
        # Spalte hinzufügen
        print("🔄 Füge daily_cycles Spalte zur project Tabelle hinzu...")
        cursor.execute("ALTER TABLE project ADD COLUMN daily_cycles FLOAT DEFAULT 1.2")
        
        # Standardwerte für bestehende Projekte setzen
        print("🔄 Setze Standardwerte für bestehende Projekte...")
        
        # Projekt-spezifische Zyklen basierend auf BESS-Größe
        cursor.execute("""
            UPDATE project 
            SET daily_cycles = CASE 
                WHEN bess_size >= 5000 THEN 1.5  -- Große BESS: 1,5 Zyklen/Tag
                WHEN bess_size >= 1000 THEN 1.2  -- Mittlere BESS: 1,2 Zyklen/Tag
                ELSE 1.0                         -- Kleine BESS: 1,0 Zyklen/Tag
            END
            WHERE daily_cycles IS NULL OR daily_cycles = 1.2
        """)
        
        conn.commit()
        
        # Aktualisierte Projekte anzeigen
        cursor.execute("SELECT id, name, bess_size, daily_cycles FROM project")
        projects = cursor.fetchall()
        
        print("\n✅ Migration erfolgreich abgeschlossen!")
        print("📊 Aktualisierte Projekte:")
        for project in projects:
            print(f"   - {project[1]} (ID: {project[0]}): {project[2]} kWh → {project[3]} Zyklen/Tag")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Fehler bei der Migration: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    print("🚀 Starte Migration: daily_cycles Feld hinzufügen")
    success = add_daily_cycles_column()
    
    if success:
        print("\n✅ Migration erfolgreich!")
        print("📝 Nächste Schritte:")
        print("   1. Server neu starten")
        print("   2. Projekt-Formulare erweitern")
        print("   3. Berechnungsfunktionen anpassen")
    else:
        print("\n❌ Migration fehlgeschlagen!")

