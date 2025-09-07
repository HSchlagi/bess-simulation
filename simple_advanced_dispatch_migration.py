#!/usr/bin/env python3
"""
Einfache Migration für Advanced Dispatch Tabellen
"""

import sqlite3
import os

def create_advanced_dispatch_tables():
    """Erstellt die Advanced Dispatch Tabellen"""
    
    db_path = 'instance/bess.db'
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🚀 Erstelle Advanced Dispatch Tabellen...")
    
    try:
        # Marktpreise-Tabelle
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_prices_advanced (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                market_type VARCHAR(50) NOT NULL,
                price_eur_mwh REAL NOT NULL,
                volume_mwh REAL DEFAULT 0,
                region VARCHAR(10) DEFAULT 'AT',
                source VARCHAR(100),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Tabelle 'market_prices_advanced' erstellt")
        
        # Dispatch-Entscheidungen
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
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Tabelle 'dispatch_decisions' erstellt")
        
        # Grid-Services
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
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Tabelle 'grid_services' erstellt")
        
        # VPP-Portfolio
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vpp_portfolios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                total_power_mw REAL NOT NULL,
                total_capacity_mwh REAL NOT NULL,
                project_ids TEXT NOT NULL,
                status VARCHAR(20) DEFAULT 'active',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Tabelle 'vpp_portfolios' erstellt")
        
        # Demand Response Events
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
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Tabelle 'demand_response_events' erstellt")
        
        # Demo-Daten einfügen
        cursor.execute("""
            INSERT OR IGNORE INTO market_prices_advanced (timestamp, market_type, price_eur_mwh, volume_mwh, region, source)
            VALUES ('2025-01-01 12:00:00', 'spot', 60.0, 1000, 'AT', 'demo')
        """)
        
        cursor.execute("""
            INSERT OR IGNORE INTO market_prices_advanced (timestamp, market_type, price_eur_mwh, volume_mwh, region, source)
            VALUES ('2025-01-01 12:00:00', 'intraday', 65.0, 500, 'AT', 'demo')
        """)
        
        print("✅ Demo-Daten eingefügt")
        
        conn.commit()
        print("✅ Migration erfolgreich abgeschlossen!")
        
    except Exception as e:
        print(f"❌ Fehler bei der Migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    create_advanced_dispatch_tables()
