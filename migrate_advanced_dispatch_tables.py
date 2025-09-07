#!/usr/bin/env python3
"""
Migration für Advanced Dispatch & Grid Services Tabellen
Erstellt die erforderlichen Datenbanktabellen für das erweiterte Dispatch-System
"""

import sqlite3
import os
from datetime import datetime

def migrate_advanced_dispatch_tables():
    """Erstellt die Advanced Dispatch Tabellen"""
    
    db_path = 'instance/bess.db'
    
    # Datenbank-Verzeichnis erstellen falls nicht vorhanden
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🚀 Starte Migration für Advanced Dispatch & Grid Services...")
    
    try:
        # 1. Marktpreise-Tabelle (erweitert)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_prices_advanced (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                market_type VARCHAR(50) NOT NULL,
                price_eur_mwh REAL NOT NULL,
                volume_mwh REAL DEFAULT 0,
                region VARCHAR(10) DEFAULT 'AT',
                source VARCHAR(100),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_market_timestamp (timestamp),
                INDEX idx_market_type (market_type)
            )
        """)
        print("✅ Tabelle 'market_prices_advanced' erstellt")
        
        # 2. Dispatch-Entscheidungen
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dispatch_decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                timestamp DATETIME NOT NULL,
                power_mw REAL NOT NULL,
                market_type VARCHAR(50) NOT NULL,
                price_eur_mwh REAL NOT NULL,
                revenue_eur REAL NOT NULL,
                soc_before_pct REAL,
                soc_after_pct REAL,
                reason TEXT,
                optimization_type VARCHAR(50) DEFAULT 'arbitrage',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id),
                INDEX idx_dispatch_project (project_id),
                INDEX idx_dispatch_timestamp (timestamp),
                INDEX idx_dispatch_market (market_type)
            )
        """)
        print("✅ Tabelle 'dispatch_decisions' erstellt")
        
        # 3. Grid-Services
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS grid_services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                service_type VARCHAR(50) NOT NULL,
                power_mw REAL NOT NULL,
                duration_hours REAL NOT NULL,
                revenue_eur REAL NOT NULL,
                status VARCHAR(20) DEFAULT 'active',
                start_time DATETIME,
                end_time DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id),
                INDEX idx_grid_project (project_id),
                INDEX idx_grid_service_type (service_type),
                INDEX idx_grid_status (status)
            )
        """)
        print("✅ Tabelle 'grid_services' erstellt")
        
        # 4. VPP-Portfolio
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vpp_portfolios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                total_power_mw REAL NOT NULL,
                total_capacity_mwh REAL NOT NULL,
                project_ids TEXT NOT NULL, -- JSON-Array der Projekt-IDs
                status VARCHAR(20) DEFAULT 'active',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Tabelle 'vpp_portfolios' erstellt")
        
        # 5. VPP-Optimierungen
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vpp_optimizations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                portfolio_id INTEGER NOT NULL,
                optimization_timestamp DATETIME NOT NULL,
                total_power_mw REAL NOT NULL,
                total_revenue_eur REAL NOT NULL,
                average_price_eur_mwh REAL NOT NULL,
                unit_count INTEGER NOT NULL,
                optimization_results TEXT, -- JSON mit detaillierten Ergebnissen
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (portfolio_id) REFERENCES vpp_portfolios (id),
                INDEX idx_vpp_opt_portfolio (portfolio_id),
                INDEX idx_vpp_opt_timestamp (optimization_timestamp)
            )
        """)
        print("✅ Tabelle 'vpp_optimizations' erstellt")
        
        # 6. Demand Response Events
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS demand_response_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                event_name VARCHAR(100),
                start_time DATETIME NOT NULL,
                duration_hours REAL NOT NULL,
                power_reduction_mw REAL NOT NULL,
                compensation_eur_mwh REAL NOT NULL,
                expected_revenue_eur REAL NOT NULL,
                status VARCHAR(20) DEFAULT 'scheduled',
                actual_power_reduction_mw REAL,
                actual_revenue_eur REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id),
                INDEX idx_dr_project (project_id),
                INDEX idx_dr_start_time (start_time),
                INDEX idx_dr_status (status)
            )
        """)
        print("✅ Tabelle 'demand_response_events' erstellt")
        
        # 7. Grid Code Compliance
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS grid_compliance_checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                check_timestamp DATETIME NOT NULL,
                frequency_compliant BOOLEAN,
                voltage_compliant BOOLEAN,
                power_factor_compliant BOOLEAN,
                response_time_compliant BOOLEAN,
                ramp_rate_compliant BOOLEAN,
                overall_compliance_pct REAL,
                compliance_status VARCHAR(20),
                current_conditions TEXT, -- JSON mit aktuellen Bedingungen
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id),
                INDEX idx_compliance_project (project_id),
                INDEX idx_compliance_timestamp (check_timestamp),
                INDEX idx_compliance_status (compliance_status)
            )
        """)
        print("✅ Tabelle 'grid_compliance_checks' erstellt")
        
        # 8. Advanced Dispatch Konfiguration
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS advanced_dispatch_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                config_type VARCHAR(50) NOT NULL,
                config_key VARCHAR(100) NOT NULL,
                config_value TEXT NOT NULL,
                description TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id),
                UNIQUE(project_id, config_type, config_key),
                INDEX idx_config_project (project_id),
                INDEX idx_config_type (config_type)
            )
        """)
        print("✅ Tabelle 'advanced_dispatch_config' erstellt")
        
        # Demo-Daten einfügen
        insert_demo_data(cursor)
        
        conn.commit()
        print("✅ Migration erfolgreich abgeschlossen!")
        
    except Exception as e:
        print(f"❌ Fehler bei der Migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def insert_demo_data(cursor):
    """Fügt Demo-Daten für Advanced Dispatch ein"""
    
    print("📊 Füge Demo-Daten ein...")
    
    # Demo-Marktpreise
    demo_market_prices = [
        ('2025-01-01 00:00:00', 'spot', 45.50, 1000, 'AT', 'demo'),
        ('2025-01-01 01:00:00', 'spot', 42.30, 1000, 'AT', 'demo'),
        ('2025-01-01 02:00:00', 'spot', 38.90, 1000, 'AT', 'demo'),
        ('2025-01-01 03:00:00', 'spot', 35.20, 1000, 'AT', 'demo'),
        ('2025-01-01 04:00:00', 'spot', 32.10, 1000, 'AT', 'demo'),
        ('2025-01-01 05:00:00', 'spot', 28.80, 1000, 'AT', 'demo'),
        ('2025-01-01 06:00:00', 'spot', 31.50, 1000, 'AT', 'demo'),
        ('2025-01-01 07:00:00', 'spot', 38.90, 1000, 'AT', 'demo'),
        ('2025-01-01 08:00:00', 'spot', 52.30, 1000, 'AT', 'demo'),
        ('2025-01-01 09:00:00', 'spot', 68.70, 1000, 'AT', 'demo'),
        ('2025-01-01 10:00:00', 'spot', 75.20, 1000, 'AT', 'demo'),
        ('2025-01-01 11:00:00', 'spot', 82.10, 1000, 'AT', 'demo'),
        ('2025-01-01 12:00:00', 'spot', 88.50, 1000, 'AT', 'demo'),
        ('2025-01-01 13:00:00', 'spot', 85.30, 1000, 'AT', 'demo'),
        ('2025-01-01 14:00:00', 'spot', 78.90, 1000, 'AT', 'demo'),
        ('2025-01-01 15:00:00', 'spot', 72.40, 1000, 'AT', 'demo'),
        ('2025-01-01 16:00:00', 'spot', 68.20, 1000, 'AT', 'demo'),
        ('2025-01-01 17:00:00', 'spot', 75.80, 1000, 'AT', 'demo'),
        ('2025-01-01 18:00:00', 'spot', 89.30, 1000, 'AT', 'demo'),
        ('2025-01-01 19:00:00', 'spot', 95.70, 1000, 'AT', 'demo'),
        ('2025-01-01 20:00:00', 'spot', 92.10, 1000, 'AT', 'demo'),
        ('2025-01-01 21:00:00', 'spot', 78.50, 1000, 'AT', 'demo'),
        ('2025-01-01 22:00:00', 'spot', 65.20, 1000, 'AT', 'demo'),
        ('2025-01-01 23:00:00', 'spot', 52.80, 1000, 'AT', 'demo'),
    ]
    
    cursor.executemany("""
        INSERT INTO market_prices_advanced (timestamp, market_type, price_eur_mwh, volume_mwh, region, source)
        VALUES (?, ?, ?, ?, ?, ?)
    """, demo_market_prices)
    print("✅ Demo-Marktpreise eingefügt")
    
    # Demo-Intraday-Preise
    demo_intraday_prices = [
        ('2025-01-01 00:00:00', 'intraday', 48.20, 500, 'AT', 'demo'),
        ('2025-01-01 01:00:00', 'intraday', 45.10, 500, 'AT', 'demo'),
        ('2025-01-01 02:00:00', 'intraday', 41.50, 500, 'AT', 'demo'),
        ('2025-01-01 03:00:00', 'intraday', 38.80, 500, 'AT', 'demo'),
        ('2025-01-01 04:00:00', 'intraday', 35.90, 500, 'AT', 'demo'),
        ('2025-01-01 05:00:00', 'intraday', 32.40, 500, 'AT', 'demo'),
        ('2025-01-01 06:00:00', 'intraday', 35.20, 500, 'AT', 'demo'),
        ('2025-01-01 07:00:00', 'intraday', 42.60, 500, 'AT', 'demo'),
        ('2025-01-01 08:00:00', 'intraday', 58.90, 500, 'AT', 'demo'),
        ('2025-01-01 09:00:00', 'intraday', 75.30, 500, 'AT', 'demo'),
        ('2025-01-01 10:00:00', 'intraday', 82.80, 500, 'AT', 'demo'),
        ('2025-01-01 11:00:00', 'intraday', 89.50, 500, 'AT', 'demo'),
        ('2025-01-01 12:00:00', 'intraday', 95.20, 500, 'AT', 'demo'),
        ('2025-01-01 13:00:00', 'intraday', 92.10, 500, 'AT', 'demo'),
        ('2025-01-01 14:00:00', 'intraday', 85.70, 500, 'AT', 'demo'),
        ('2025-01-01 15:00:00', 'intraday', 79.20, 500, 'AT', 'demo'),
        ('2025-01-01 16:00:00', 'intraday', 74.80, 500, 'AT', 'demo'),
        ('2025-01-01 17:00:00', 'intraday', 82.40, 500, 'AT', 'demo'),
        ('2025-01-01 18:00:00', 'intraday', 95.90, 500, 'AT', 'demo'),
        ('2025-01-01 19:00:00', 'intraday', 102.30, 500, 'AT', 'demo'),
        ('2025-01-01 20:00:00', 'intraday', 98.70, 500, 'AT', 'demo'),
        ('2025-01-01 21:00:00', 'intraday', 84.20, 500, 'AT', 'demo'),
        ('2025-01-01 22:00:00', 'intraday', 70.80, 500, 'AT', 'demo'),
        ('2025-01-01 23:00:00', 'intraday', 58.40, 500, 'AT', 'demo'),
    ]
    
    cursor.executemany("""
        INSERT INTO market_prices_advanced (timestamp, market_type, price_eur_mwh, volume_mwh, region, source)
        VALUES (?, ?, ?, ?, ?, ?)
    """, demo_intraday_prices)
    print("✅ Demo-Intraday-Preise eingefügt")
    
    # Demo-VPP-Portfolio
    cursor.execute("""
        INSERT INTO vpp_portfolios (name, description, total_power_mw, total_capacity_mwh, project_ids, status)
        VALUES ('Demo VPP Portfolio', 'Demo-Portfolio für Advanced Dispatch Tests', 10.0, 40.0, '[1,2,3]', 'active')
    """)
    print("✅ Demo-VPP-Portfolio erstellt")
    
    # Demo-Demand Response Event
    cursor.execute("""
        INSERT INTO demand_response_events (project_id, event_name, start_time, duration_hours, power_reduction_mw, compensation_eur_mwh, expected_revenue_eur, status)
        VALUES (1, 'Demo Demand Response Event', '2025-01-01 18:00:00', 2.0, 1.5, 50.0, 150.0, 'scheduled')
    """)
    print("✅ Demo-Demand Response Event erstellt")
    
    # Demo-Grid-Services
    cursor.execute("""
        INSERT INTO grid_services (project_id, service_type, power_mw, duration_hours, revenue_eur, status, start_time, end_time)
        VALUES (1, 'frequency_regulation', 1.0, 1.0, 25.0, 'active', '2025-01-01 00:00:00', '2025-01-01 01:00:00')
    """)
    cursor.execute("""
        INSERT INTO grid_services (project_id, service_type, power_mw, duration_hours, revenue_eur, status, start_time, end_time)
        VALUES (1, 'voltage_support', 0.6, 1.0, 8.0, 'active', '2025-01-01 00:00:00', '2025-01-01 01:00:00')
    """)
    print("✅ Demo-Grid-Services erstellt")
    
    # Demo-Compliance-Check
    cursor.execute("""
        INSERT INTO grid_compliance_checks (project_id, check_timestamp, frequency_compliant, voltage_compliant, power_factor_compliant, response_time_compliant, ramp_rate_compliant, overall_compliance_pct, compliance_status, current_conditions)
        VALUES (1, '2025-01-01 12:00:00', 1, 1, 1, 1, 1, 100.0, 'compliant', '{"frequency_hz": 50.0, "voltage_pu": 1.0, "power_factor": 1.0}')
    """)
    print("✅ Demo-Compliance-Check erstellt")

if __name__ == "__main__":
    migrate_advanced_dispatch_tables()
