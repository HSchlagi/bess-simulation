#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vereinfachtes Migration-Script für BESS-Simulation Erweiterung
Erstellt neue Tabellen und Standard-Use-Cases ohne SQLAlchemy
"""

import sqlite3
import os
from datetime import datetime, date

def create_tables():
    """Erstellt die neuen Tabellen in der SQLite-Datenbank"""
    db_path = 'instance/bess.db'
    
    if not os.path.exists(db_path):
        print(f"Datenbank nicht gefunden: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # UseCase Tabelle
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS use_case (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                scenario_type VARCHAR(50),
                pv_power_mwp FLOAT DEFAULT 0.0,
                hydro_power_kw FLOAT DEFAULT 0.0,
                hydro_energy_mwh_year FLOAT DEFAULT 0.0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # RevenueModel Tabelle
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS revenue_model (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                name VARCHAR(100) NOT NULL,
                revenue_type VARCHAR(50),
                price_eur_mwh FLOAT DEFAULT 0.0,
                availability_hours FLOAT DEFAULT 8760,
                efficiency_factor FLOAT DEFAULT 1.0,
                description TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES project (id)
            )
        ''')
        
        # RevenueActivation Tabelle
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS revenue_activation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                revenue_model_id INTEGER,
                timestamp DATETIME NOT NULL,
                activation_duration_hours FLOAT,
                power_mw FLOAT,
                revenue_eur FLOAT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (revenue_model_id) REFERENCES revenue_model (id)
            )
        ''')
        
        # GridTariff Tabelle
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS grid_tariff (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                tariff_type VARCHAR(50),
                base_price_eur_mwh FLOAT NOT NULL,
                spot_multiplier FLOAT DEFAULT 1.0,
                region VARCHAR(50),
                valid_from DATE,
                valid_to DATE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # LegalCharges Tabelle
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS legal_charges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                charge_type VARCHAR(50),
                amount_eur_mwh FLOAT NOT NULL,
                region VARCHAR(50),
                valid_from DATE,
                valid_to DATE,
                description TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # RenewableSubsidy Tabelle
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS renewable_subsidy (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                technology_type VARCHAR(50),
                subsidy_eur_mwh FLOAT DEFAULT 0.0,
                region VARCHAR(50),
                year INTEGER,
                max_capacity_mw FLOAT,
                description TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # BatteryDegradation Tabelle
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS battery_degradation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                year INTEGER NOT NULL,
                capacity_factor FLOAT DEFAULT 1.0,
                cycles_per_year INTEGER DEFAULT 0,
                degradation_rate FLOAT DEFAULT 0.0,
                remaining_capacity_kwh FLOAT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES project (id)
            )
        ''')
        
        # RegulatoryChanges Tabelle
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS regulatory_changes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                change_type VARCHAR(50),
                old_value_eur_mwh FLOAT,
                new_value_eur_mwh FLOAT,
                change_year INTEGER,
                region VARCHAR(50),
                description TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # GridConstraints Tabelle
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS grid_constraints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                constraint_type VARCHAR(50),
                max_power_mw FLOAT NOT NULL,
                time_period VARCHAR(50),
                description TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES project (id)
            )
        ''')
        
        # LoadShiftingPlan Tabelle
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS load_shifting_plan (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                name VARCHAR(100) NOT NULL,
                plan_date DATE NOT NULL,
                optimization_target VARCHAR(50),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES project (id)
            )
        ''')
        
        # LoadShiftingValue Tabelle
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS load_shifting_value (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                load_shifting_plan_id INTEGER,
                timestamp DATETIME NOT NULL,
                charge_power_mw FLOAT DEFAULT 0.0,
                discharge_power_mw FLOAT DEFAULT 0.0,
                battery_soc_percent FLOAT,
                spot_price_eur_mwh FLOAT,
                cost_eur FLOAT,
                revenue_eur FLOAT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (load_shifting_plan_id) REFERENCES load_shifting_plan (id)
            )
        ''')
        
        # Project Tabelle erweitern
        cursor.execute('''
            ALTER TABLE project ADD COLUMN use_case_id INTEGER
        ''')
        
        cursor.execute('''
            ALTER TABLE project ADD COLUMN simulation_year INTEGER DEFAULT 2024
        ''')
        
        conn.commit()
        print("✓ Alle Tabellen erfolgreich erstellt")
        return True
        
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("✓ Tabellen bereits vorhanden")
            return True
        else:
            print(f"❌ Fehler beim Erstellen der Tabellen: {e}")
            return False
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False
    finally:
        conn.close()

def insert_standard_data():
    """Fügt Standard-Daten ein"""
    db_path = 'instance/bess.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Standard-Use-Cases
        use_cases = [
            ('UC1', 'Verbrauch ohne Eigenerzeugung', 'consumption_only', 0.0, 0.0, 0.0),
            ('UC2', 'Verbrauch + PV (1,95 MWp)', 'pv_consumption', 1.95, 0.0, 0.0),
            ('UC3', 'Verbrauch + PV + Wasserkraft (650 kW, 2700 MWh/a)', 'pv_hydro_consumption', 1.95, 650.0, 2700.0)
        ]
        
        for uc in use_cases:
            cursor.execute('''
                INSERT OR IGNORE INTO use_case (name, description, scenario_type, pv_power_mwp, hydro_power_kw, hydro_energy_mwh_year)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', uc)
        
        # Standard-Netzentgelte
        grid_tariffs = [
            ('AT Bezug Standard', 'consumption', 25.0, 1.2, 'AT', '2024-01-01', '2025-12-31'),
            ('AT Einspeisung Standard', 'feed_in', 15.0, 0.8, 'AT', '2024-01-01', '2025-12-31')
        ]
        
        for gt in grid_tariffs:
            cursor.execute('''
                INSERT OR IGNORE INTO grid_tariff (name, tariff_type, base_price_eur_mwh, spot_multiplier, region, valid_from, valid_to)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', gt)
        
        # Standard-Gesetzesabgaben
        legal_charges = [
            ('Stromabgabe 2024', 'electricity_tax', 1.0, 'AT', '2024-01-01', '2024-12-31', 'Stromabgabe in Österreich 2024'),
            ('Stromabgabe 2025+', 'electricity_tax', 15.0, 'AT', '2025-01-01', '2030-12-31', 'Stromabgabe in Österreich ab 2025'),
            ('Netzverlustentgelt AT', 'network_loss', 8.5, 'AT', '2024-01-01', '2025-12-31', 'Netzverlustentgelt Österreich'),
            ('Clearinggebühr EPEX', 'clearing_fee', 0.15, 'AT', '2024-01-01', '2025-12-31', 'Clearinggebühr EPEX Spotmarkt')
        ]
        
        for lc in legal_charges:
            cursor.execute('''
                INSERT OR IGNORE INTO legal_charges (name, charge_type, amount_eur_mwh, region, valid_from, valid_to, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', lc)
        
        # Standard-Förderungen
        renewable_subsidies = [
            ('PV Förderung 2024', 'pv', 0.0, 'AT', 2024, 1000.0, 'PV Förderung Österreich 2024 (0 EUR/MWh)'),
            ('BESS Förderung 2024', 'bess', 0.0, 'AT', 2024, 100.0, 'BESS Förderung Österreich 2024 (0 EUR/MWh)')
        ]
        
        for rs in renewable_subsidies:
            cursor.execute('''
                INSERT OR IGNORE INTO renewable_subsidy (name, technology_type, subsidy_eur_mwh, region, year, max_capacity_mw, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', rs)
        
        # Gesetzliche Änderungen
        regulatory_changes = [
            ('Stromabgabe Erhöhung 2025', 'tax_increase', 1.0, 15.0, 2025, 'AT', 'Erhöhung der Stromabgabe von 1 EUR auf 15 EUR/MWh ab 2025')
        ]
        
        for rc in regulatory_changes:
            cursor.execute('''
                INSERT OR IGNORE INTO regulatory_changes (name, change_type, old_value_eur_mwh, new_value_eur_mwh, change_year, region, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', rc)
        
        conn.commit()
        print("✓ Standard-Daten erfolgreich eingefügt")
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Einfügen der Standard-Daten: {e}")
        return False
    finally:
        conn.close()

def main():
    """Hauptfunktion für die Migration"""
    print("=== BESS-Simulation Datenbank-Migration (Vereinfacht) ===")
    print(f"Startzeit: {datetime.now()}")
    
    # Tabellen erstellen
    print("\n1. Erstelle neue Datenbank-Tabellen...")
    if not create_tables():
        print("❌ Migration fehlgeschlagen")
        return
    
    # Standard-Daten einfügen
    print("\n2. Füge Standard-Daten ein...")
    if not insert_standard_data():
        print("❌ Migration fehlgeschlagen")
        return
    
    print("\n✓ Migration erfolgreich abgeschlossen!")
    print(f"Endzeit: {datetime.now()}")

if __name__ == "__main__":
    main() 