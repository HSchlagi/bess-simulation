#!/usr/bin/env python3
"""
Migration: BatteryConfig Tabelle erstellen
==========================================

Erstellt die neue BatteryConfig Tabelle für C-Rate Integration
"""

import sqlite3
import os
from datetime import datetime

def create_battery_config_table():
    """Erstellt die BatteryConfig Tabelle"""
    
    # Datenbankpfad
    db_path = 'instance/bess.db'
    
    if not os.path.exists('instance'):
        os.makedirs('instance')
    
    # Verbindung zur Datenbank
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Prüfe ob Tabelle bereits existiert
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='battery_config'
        """)
        
        if cursor.fetchone():
            print("✅ BatteryConfig Tabelle existiert bereits")
            return True
        
        # Tabelle erstellen
        cursor.execute("""
            CREATE TABLE battery_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                E_nom_kWh REAL NOT NULL,
                C_chg_rate REAL DEFAULT 0.5,
                C_dis_rate REAL DEFAULT 1.0,
                derating_enable BOOLEAN DEFAULT 1,
                soc_derate_charge TEXT,
                soc_derate_discharge TEXT,
                temp_derate_charge TEXT,
                temp_derate_discharge TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES project (id)
            )
        """)
        
        # Index für project_id erstellen
        cursor.execute("""
            CREATE INDEX idx_battery_config_project_id 
            ON battery_config (project_id)
        """)
        
        conn.commit()
        print("✅ BatteryConfig Tabelle erfolgreich erstellt")
        
        # Beispiel-Daten für bestehende Projekte erstellen
        cursor.execute("SELECT id, bess_size FROM project WHERE bess_size IS NOT NULL")
        projects = cursor.fetchall()
        
        for project_id, bess_size in projects:
            # Default-Konfiguration erstellen
            default_config = {
                'soc_charge': '[[0.0,0.2,0.2],[0.2,0.8,1.0],[0.8,1.0,0.5]]',
                'soc_discharge': '[[0.0,0.2,0.7],[0.2,0.8,1.0],[0.8,1.0,0.8]]',
                'temp_charge': '[[-20,0,0.2],[0,10,0.6],[10,35,1.0],[35,50,0.7]]',
                'temp_discharge': '[[-20,0,0.6],[0,10,0.9],[10,35,1.0],[35,50,0.9]]'
            }
            
            cursor.execute("""
                INSERT INTO battery_config 
                (project_id, E_nom_kWh, C_chg_rate, C_dis_rate, derating_enable,
                 soc_derate_charge, soc_derate_discharge, temp_derate_charge, temp_derate_discharge)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                project_id, bess_size, 0.5, 1.0, True,
                default_config['soc_charge'], default_config['soc_discharge'],
                default_config['temp_charge'], default_config['temp_discharge']
            ))
        
        conn.commit()
        print(f"✅ Default-Konfigurationen für {len(projects)} Projekte erstellt")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Erstellen der BatteryConfig Tabelle: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    print("🔄 Erstelle BatteryConfig Tabelle...")
    success = create_battery_config_table()
    
    if success:
        print("✅ Migration erfolgreich abgeschlossen")
    else:
        print("❌ Migration fehlgeschlagen")
