#!/usr/bin/env python3
"""
Migration: Dispatch- und Redispatch-Tabellen hinzufügen
Datum: 2025-09-03
Beschreibung: Neue Tabellen für BESS Dispatch-Simulation und Redispatch-Calls
"""

import sqlite3
import os
from datetime import datetime

def migrate_dispatch_tables():
    """Dispatch-Tabellen zur BESS-Datenbank hinzufügen"""
    
    # Datenbankpfad
    db_path = "instance/bess.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Datenbank nicht gefunden: {db_path}")
        return False
    
    try:
        # Verbindung zur Datenbank
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Prüfe bestehende Tabellen...")
        
        # Prüfe ob Dispatch-Tabellen bereits existieren
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='dispatch_simulation'")
        if cursor.fetchone():
            print("✅ Tabelle 'dispatch_simulation' existiert bereits")
        else:
            print("📝 Erstelle Tabelle 'dispatch_simulation'...")
            cursor.execute("""
                CREATE TABLE dispatch_simulation (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    simulation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    dispatch_mode VARCHAR(50) NOT NULL,
                    time_resolution_minutes INTEGER DEFAULT 60,
                    country VARCHAR(2) DEFAULT 'AT',
                    total_revenue REAL DEFAULT 0.0,
                    total_cost REAL DEFAULT 0.0,
                    net_cashflow REAL DEFAULT 0.0,
                    soc_profile TEXT,
                    dispatch_data TEXT,
                    settlement_data TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES project (id)
                )
            """)
            print("✅ Tabelle 'dispatch_simulation' erstellt")
        
        # Prüfe Redispatch-Tabelle
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='redispatch_call'")
        if cursor.fetchone():
            print("✅ Tabelle 'redispatch_call' existiert bereits")
        else:
            print("📝 Erstelle Tabelle 'redispatch_call'...")
            cursor.execute("""
                CREATE TABLE redispatch_call (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dispatch_simulation_id INTEGER NOT NULL,
                    start_time DATETIME NOT NULL,
                    duration_slots INTEGER NOT NULL,
                    power_mw REAL NOT NULL,
                    mode VARCHAR(20) DEFAULT 'delta',
                    compensation_eur_mwh REAL DEFAULT 0.0,
                    reason VARCHAR(200),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (dispatch_simulation_id) REFERENCES dispatch_simulation (id)
                )
            """)
            print("✅ Tabelle 'redispatch_call' erstellt")
        
        # Prüfe Dispatch-Parameter-Tabelle
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='dispatch_parameters'")
        if cursor.fetchone():
            print("✅ Tabelle 'dispatch_parameters' existiert bereits")
        else:
            print("📝 Erstelle Tabelle 'dispatch_parameters'...")
            cursor.execute("""
                CREATE TABLE dispatch_parameters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    parameter_name VARCHAR(100) NOT NULL,
                    parameter_value REAL NOT NULL,
                    unit VARCHAR(20),
                    description TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES project (id)
                )
            """)
            print("✅ Tabelle 'dispatch_parameters' erstellt")
        
        # Erstelle Indizes für bessere Performance
        print("📊 Erstelle Indizes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_dispatch_project_id ON dispatch_simulation(project_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_dispatch_mode ON dispatch_simulation(dispatch_mode)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_redispatch_sim_id ON redispatch_call(dispatch_simulation_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_redispatch_start_time ON redispatch_call(start_time)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_dispatch_params_project_id ON dispatch_parameters(project_id)")
        
        # Commit Änderungen
        conn.commit()
        print("✅ Alle Änderungen gespeichert")
        
        # Zeige Tabellen-Übersicht
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        print("\n📋 Verfügbare Tabellen:")
        for table in tables:
            print(f"   - {table[0]}")
        
        conn.close()
        print("\n🎉 Migration erfolgreich abgeschlossen!")
        return True
        
    except Exception as e:
        print(f"❌ Fehler bei der Migration: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    print("🚀 Starte Dispatch-Tabellen Migration...")
    success = migrate_dispatch_tables()
    if success:
        print("✅ Migration erfolgreich!")
    else:
        print("❌ Migration fehlgeschlagen!")
