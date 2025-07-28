#!/usr/bin/env python3
"""
Skript zur Reparatur der solar_data Tabelle
"""

import sqlite3
import os

def fix_solar_data_table():
    """Repariert die solar_data Tabelle"""
    
    db_path = "instance/bess.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Datenbank nicht gefunden: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Prüfe ob Tabelle existiert
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='solar_data'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("🔄 Solar_data Tabelle existiert - lösche und erstelle neu...")
            cursor.execute("DROP TABLE solar_data")
        
        # Erstelle Tabelle neu
        cursor.execute('''
            CREATE TABLE solar_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                location_key TEXT NOT NULL,
                year INTEGER NOT NULL,
                datetime TEXT NOT NULL,
                global_irradiance REAL,
                beam_irradiance REAL,
                diffuse_irradiance REAL,
                sun_height REAL,
                temperature_2m REAL,
                wind_speed_10m REAL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(location_key, year, datetime)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        print("✅ Solar_data Tabelle erfolgreich erstellt!")
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Erstellen der Tabelle: {e}")
        return False

if __name__ == "__main__":
    fix_solar_data_table() 