#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migration: Roadmap Stufe 1 - Netzrestriktionen, Degradation, Second-Life
========================================================================

Erstellt die neuen Tabellen für:
- Netzrestriktionen (network_restrictions)
- Erweiterte Degradation (battery_degradation_advanced)
- Second-Life Konfiguration (second_life_config)
"""

import sqlite3
import os
import json
from datetime import datetime


def create_network_restrictions_table(cursor):
    """Erstellt die network_restrictions Tabelle"""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS network_restrictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            max_discharge_kw REAL DEFAULT 0.0,
            max_charge_kw REAL DEFAULT 0.0,
            ramp_rate_percent REAL DEFAULT 10.0,
            export_limit_kw REAL DEFAULT 0.0,
            network_level TEXT DEFAULT 'NE5',
            eeg_100h_rule_enabled BOOLEAN DEFAULT 0,
            eeg_100h_hours_per_year INTEGER DEFAULT 100,
            eeg_100h_used_hours INTEGER DEFAULT 0,
            hull_curve_enabled BOOLEAN DEFAULT 0,
            hull_curve_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES project (id)
        )
    """)
    
    # Index erstellen
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_network_restrictions_project_id 
        ON network_restrictions (project_id)
    """)
    
    print("[OK] network_restrictions Tabelle erstellt")


def create_battery_degradation_advanced_table(cursor):
    """Erstellt die battery_degradation_advanced Tabelle"""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS battery_degradation_advanced (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            initial_capacity_kwh REAL NOT NULL,
            current_capacity_kwh REAL NOT NULL,
            cycle_number INTEGER DEFAULT 0,
            dod REAL DEFAULT 0.0,
            efficiency REAL DEFAULT 0.85,
            temperature REAL DEFAULT 25.0,
            state_of_health REAL DEFAULT 100.0,
            degradation_rate_per_cycle REAL DEFAULT 0.0001,
            calendar_aging_rate REAL DEFAULT 0.02,
            is_second_life BOOLEAN DEFAULT 0,
            second_life_start_capacity REAL DEFAULT 0.85,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES project (id)
        )
    """)
    
    # Index erstellen
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_battery_degradation_advanced_project_id 
        ON battery_degradation_advanced (project_id)
    """)
    
    print("[OK] battery_degradation_advanced Tabelle erstellt")


def create_second_life_config_table(cursor):
    """Erstellt die second_life_config Tabelle"""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS second_life_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            is_second_life BOOLEAN DEFAULT 0,
            start_capacity_percent REAL DEFAULT 85.0,
            lifetime_years INTEGER DEFAULT 5,
            cost_reduction_percent REAL DEFAULT 50.0,
            degradation_multiplier REAL DEFAULT 1.5,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES project (id)
        )
    """)
    
    # Index erstellen
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_second_life_config_project_id 
        ON second_life_config (project_id)
    """)
    
    print("[OK] second_life_config Tabelle erstellt")


def create_restrictions_history_table(cursor):
    """Erstellt die restrictions_history Tabelle für Tracking"""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS restrictions_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            simulation_id INTEGER,
            timestamp TIMESTAMP NOT NULL,
            planned_power_kw REAL NOT NULL,
            actual_power_kw REAL NOT NULL,
            power_loss_kw REAL DEFAULT 0.0,
            revenue_loss_kwh REAL DEFAULT 0.0,
            restrictions_applied TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES project (id)
        )
    """)
    
    # Index erstellen
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_restrictions_history_project_id 
        ON restrictions_history (project_id, timestamp)
    """)
    
    print("[OK] restrictions_history Tabelle erstellt")


def create_degradation_history_table(cursor):
    """Erstellt die degradation_history Tabelle für Tracking"""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS degradation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            simulation_id INTEGER,
            timestamp TIMESTAMP NOT NULL,
            cycle_number INTEGER NOT NULL,
            dod REAL DEFAULT 0.0,
            temperature REAL DEFAULT 25.0,
            capacity_loss_kwh REAL DEFAULT 0.0,
            current_capacity_kwh REAL NOT NULL,
            state_of_health REAL NOT NULL,
            efficiency REAL DEFAULT 0.85,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES project (id)
        )
    """)
    
    # Index erstellen
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_degradation_history_project_id 
        ON degradation_history (project_id, timestamp)
    """)
    
    print("[OK] degradation_history Tabelle erstellt")


def initialize_default_restrictions(cursor, project_id, project_power_kw):
    """Initialisiert Standard-Netzrestriktionen für ein Projekt"""
    cursor.execute("""
        INSERT OR REPLACE INTO network_restrictions 
        (project_id, max_discharge_kw, max_charge_kw, ramp_rate_percent, 
         export_limit_kw, network_level, eeg_100h_rule_enabled)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        project_id,
        project_power_kw,
        project_power_kw,
        10.0,  # 10% Ramp-Rate
        project_power_kw * 0.8,  # 80% Exportlimit
        'NE5',  # Standard: Niederspannung
        0  # 100-h-Regel standardmäßig deaktiviert
    ))
    print(f"[OK] Standard-Netzrestriktionen für Projekt {project_id} erstellt")


def initialize_default_degradation(cursor, project_id, initial_capacity_kwh):
    """Initialisiert Standard-Degradation für ein Projekt"""
    cursor.execute("""
        INSERT OR REPLACE INTO battery_degradation_advanced
        (project_id, initial_capacity_kwh, current_capacity_kwh, 
         cycle_number, efficiency, state_of_health, degradation_rate_per_cycle, 
         calendar_aging_rate, is_second_life)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        project_id,
        initial_capacity_kwh,
        initial_capacity_kwh,
        0,  # Keine Zyklen
        0.85,  # 85% Effizienz
        100.0,  # 100% SoH
        0.0001,  # 0.01% pro Zyklus
        0.02,  # 2% pro Jahr
        0  # Keine Second-Life
    ))
    print(f"[OK] Standard-Degradation für Projekt {project_id} erstellt")


def main():
    """Hauptfunktion für Migration"""
    db_path = 'instance/bess.db'
    
    if not os.path.exists('instance'):
        os.makedirs('instance')
    
    if not os.path.exists(db_path):
        print(f"[FEHLER] Datenbank {db_path} existiert nicht!")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("=" * 60)
        print("Roadmap Stufe 1 Migration startet...")
        print("=" * 60)
        
        # Tabellen erstellen
        create_network_restrictions_table(cursor)
        create_battery_degradation_advanced_table(cursor)
        create_second_life_config_table(cursor)
        create_restrictions_history_table(cursor)
        create_degradation_history_table(cursor)
        
        # Bestehende Projekte initialisieren
        cursor.execute("SELECT id, bess_power, bess_size FROM project WHERE bess_power IS NOT NULL")
        projects = cursor.fetchall()
        
        for project_id, bess_power, bess_size in projects:
            if bess_power and bess_size:
                # Netzrestriktionen initialisieren
                initialize_default_restrictions(cursor, project_id, bess_power)
                
                # Degradation initialisieren
                initialize_default_degradation(cursor, project_id, bess_size)
        
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

