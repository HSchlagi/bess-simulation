#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migration für Roadmap Stufe 2.1: Co-Location PV + BESS
Erstellt die notwendigen Datenbank-Tabellen
"""

import sqlite3
import os
from datetime import datetime


def create_co_location_config_table(cursor):
    """Erstellt die co_location_config Tabelle"""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS co_location_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            is_co_location BOOLEAN DEFAULT 0,
            shared_grid_connection_kw REAL DEFAULT 0.0,
            curtailment_reduction_percent REAL DEFAULT 80.0,
            pv_guided_peak_shaving BOOLEAN DEFAULT 1,
            self_consumption_boost_percent REAL DEFAULT 15.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES project (id)
        )
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_co_location_config_project_id 
        ON co_location_config (project_id)
    """)
    
    print("[OK] co_location_config Tabelle erstellt")


def create_co_location_history_table(cursor):
    """Erstellt die co_location_history Tabelle"""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS co_location_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            simulation_id INTEGER,
            timestamp TIMESTAMP NOT NULL,
            pv_generation_kw REAL NOT NULL,
            consumption_kw REAL NOT NULL,
            curtailment_losses_kw REAL DEFAULT 0.0,
            avoided_curtailment_kw REAL DEFAULT 0.0,
            pv_utilization_percent REAL DEFAULT 100.0,
            self_consumption_rate_percent REAL DEFAULT 0.0,
            peak_shaving_kw REAL DEFAULT 0.0,
            grid_fee_savings_eur REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES project (id)
        )
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_co_location_history_project_id 
        ON co_location_history (project_id)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_co_location_history_timestamp 
        ON co_location_history (timestamp)
    """)
    
    print("[OK] co_location_history Tabelle erstellt")


def initialize_default_co_location(cursor, project_id, pv_power, bess_power):
    """Initialisiert Standard-Co-Location-Konfiguration für ein Projekt"""
    cursor.execute("SELECT 1 FROM co_location_config WHERE project_id = ?", (project_id,))
    if not cursor.fetchone():
        # Standard: Co-Location aktivieren, wenn PV vorhanden
        is_co_location = pv_power > 0 if pv_power else False
        shared_grid_connection = max(pv_power, bess_power) if pv_power and bess_power else (pv_power or bess_power or 0)
        
        cursor.execute("""
            INSERT INTO co_location_config (
                project_id, is_co_location, shared_grid_connection_kw,
                curtailment_reduction_percent, pv_guided_peak_shaving, self_consumption_boost_percent
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            project_id,
            is_co_location,
            shared_grid_connection,
            80.0,  # 80% Curtailment-Reduktion
            True,  # PV-geführtes Peak-Shaving aktiv
            15.0   # 15% Eigenverbrauchs-Boost
        ))
        print(f"   [OK] Standard-Co-Location-Konfiguration fr Projekt {project_id} erstellt")


def main():
    """Hauptfunktion für Migration"""
    db_path = 'instance/bess.db'
    if not os.path.exists('instance'):
        os.makedirs('instance')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("=" * 60)
        print("Roadmap Stufe 2.1 Migration startet...")
        print("=" * 60)
        
        # Tabellen erstellen
        create_co_location_config_table(cursor)
        create_co_location_history_table(cursor)
        
        # Bestehende Projekte initialisieren
        cursor.execute("SELECT id, pv_power, bess_power FROM project WHERE pv_power IS NOT NULL OR bess_power IS NOT NULL")
        projects = cursor.fetchall()
        
        for project_id, pv_power, bess_power in projects:
            if pv_power or bess_power:
                initialize_default_co_location(cursor, project_id, pv_power or 0, bess_power or 0)
        
        conn.commit()
        
        print("=" * 60)
        print("[OK] Migration erfolgreich abgeschlossen!")
        print("=" * 60)
        print(f"[INFO] {len(projects)} Projekte initialisiert")
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"[FEHLER] Fehler bei Migration: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        conn.close()


if __name__ == '__main__':
    main()




