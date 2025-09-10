#!/usr/bin/env python3
"""
HETZNER Datenbank-Vorbereitung
Erstellt alle notwendigen Tabellen für den HETZNER-APG-Scheduler
"""

import os
import sys
import sqlite3
from datetime import datetime

def prepare_hetzner_database():
    """Bereitet die Datenbank für HETZNER vor"""
    
    print("🚀 HETZNER Datenbank-Vorbereitung")
    print("=" * 50)
    
    # Datenbank-Pfad
    db_path = 'instance/bess.db'
    
    # Sicherstellen, dass Verzeichnis existiert
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("📊 Erstelle/überprüfe Datenbank-Tabellen...")
        
        # 1. Spot-Preis-Tabelle (für APG-Daten)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS spot_price (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                price_eur_mwh FLOAT NOT NULL,
                source VARCHAR(100) DEFAULT 'APG',
                region VARCHAR(50) DEFAULT 'AT',
                price_type VARCHAR(20) DEFAULT 'Day-Ahead',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(timestamp, source, region)
            )
        """)
        print("✅ spot_price Tabelle erstellt/überprüft")
        
        # 2. APG-Scheduler-Log-Tabelle
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS apg_scheduler_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                action VARCHAR(50) NOT NULL,
                status VARCHAR(20) NOT NULL,
                message TEXT,
                records_imported INTEGER DEFAULT 0,
                error_details TEXT
            )
        """)
        print("✅ apg_scheduler_log Tabelle erstellt/überprüft")
        
        # 3. Dispatch-Simulation-Tabelle
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dispatch_simulation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                simulation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                dispatch_mode VARCHAR(50) NOT NULL,
                time_resolution_minutes INTEGER DEFAULT 60,
                year INTEGER DEFAULT 2024,
                total_revenue FLOAT DEFAULT 0,
                total_cost FLOAT DEFAULT 0,
                net_cashflow FLOAT DEFAULT 0,
                simulation_data TEXT,
                settlement_data TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ dispatch_simulation Tabelle erstellt/überprüft")
        
        # 4. Projekte-Tabelle (falls nicht vorhanden)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                capacity_kwh FLOAT DEFAULT 8000,
                power_kw FLOAT DEFAULT 2000,
                efficiency FLOAT DEFAULT 0.9,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ project Tabelle erstellt/überprüft")
        
        # 5. Investment-Costs-Tabelle
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS investment_cost (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                component_type VARCHAR(100) NOT NULL,
                cost_eur FLOAT NOT NULL,
                description TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ investment_cost Tabelle erstellt/überprüft")
        
        # 6. Load-Values-Tabelle
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS load_value (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                timestamp DATETIME NOT NULL,
                energy_kwh FLOAT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ load_value Tabelle erstellt/überprüft")
        
        # Indizes für bessere Performance
        print("📈 Erstelle Indizes...")
        
        indices = [
            "CREATE INDEX IF NOT EXISTS idx_spot_price_timestamp ON spot_price(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_spot_price_source ON spot_price(source)",
            "CREATE INDEX IF NOT EXISTS idx_spot_price_region ON spot_price(region)",
            "CREATE INDEX IF NOT EXISTS idx_apg_log_timestamp ON apg_scheduler_log(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_apg_log_action ON apg_scheduler_log(action)",
            "CREATE INDEX IF NOT EXISTS idx_dispatch_project ON dispatch_simulation(project_id)",
            "CREATE INDEX IF NOT EXISTS idx_dispatch_date ON dispatch_simulation(simulation_date)",
            "CREATE INDEX IF NOT EXISTS idx_dispatch_mode ON dispatch_simulation(dispatch_mode)",
            "CREATE INDEX IF NOT EXISTS idx_investment_project ON investment_cost(project_id)",
            "CREATE INDEX IF NOT EXISTS idx_load_project ON load_value(project_id)",
            "CREATE INDEX IF NOT EXISTS idx_load_timestamp ON load_value(timestamp)"
        ]
        
        for index_sql in indices:
            cursor.execute(index_sql)
        
        print("✅ Indizes erstellt/überprüft")
        
        # Demo-Projekt erstellen (falls nicht vorhanden)
        cursor.execute("SELECT COUNT(*) FROM project")
        project_count = cursor.fetchone()[0]
        
        if project_count == 0:
            print("📋 Erstelle Demo-Projekt...")
            cursor.execute("""
                INSERT INTO project (name, description, capacity_kwh, power_kw, efficiency)
                VALUES (?, ?, ?, ?, ?)
            """, (
                "Demo BESS Projekt",
                "Demo-Projekt für HETZNER-APG-Scheduler",
                8000,  # 8 MWh
                2000,  # 2 MW
                0.9    # 90% Effizienz
            ))
            demo_project_id = cursor.lastrowid
            
            # Demo-Investment-Costs
            demo_costs = [
                ("Batterie-System", 400000, "8 MWh Lithium-Ion Batterie"),
                ("Wechselrichter", 100000, "2 MW Wechselrichter"),
                ("Installation", 50000, "Installation und Anschluss"),
                ("Planung", 20000, "Planung und Genehmigung")
            ]
            
            for cost_type, cost, description in demo_costs:
                cursor.execute("""
                    INSERT INTO investment_cost (project_id, component_type, cost_eur, description)
                    VALUES (?, ?, ?, ?)
                """, (demo_project_id, cost_type, cost, description))
            
            print(f"✅ Demo-Projekt erstellt (ID: {demo_project_id})")
        
        # Demo-Spot-Preise erstellen (falls keine vorhanden)
        cursor.execute("SELECT COUNT(*) FROM spot_price")
        spot_price_count = cursor.fetchone()[0]
        
        if spot_price_count == 0:
            print("📊 Erstelle Demo-Spot-Preise...")
            
            # Erstelle Demo-Daten für die letzten 7 Tage
            from datetime import timedelta
            import random
            
            base_date = datetime.now() - timedelta(days=7)
            
            for day in range(7):
                for hour in range(24):
                    timestamp = base_date + timedelta(days=day, hours=hour)
                    
                    # Realistische österreichische Preise
                    base_price = 60 + 20 * (hour - 12) / 12  # Höhere Preise mittags
                    price = base_price + random.uniform(-20, 20)
                    price = max(30, min(120, price))  # Begrenzen auf realistische Werte
                    
                    cursor.execute("""
                        INSERT INTO spot_price (timestamp, price_eur_mwh, source, region, price_type)
                        VALUES (?, ?, ?, ?, ?)
                    """, (timestamp, price, 'Demo (HETZNER-Vorbereitung)', 'AT', 'Day-Ahead'))
            
            print("✅ Demo-Spot-Preise erstellt (7 Tage)")
        
        # APG-Scheduler-Log-Eintrag
        cursor.execute("""
            INSERT INTO apg_scheduler_log (action, status, message, records_imported)
            VALUES (?, ?, ?, ?)
        """, (
            "database_preparation",
            "success",
            "HETZNER-Datenbank erfolgreich vorbereitet",
            0
        ))
        
        conn.commit()
        
        # Statistiken anzeigen
        print("\n📊 Datenbank-Statistiken:")
        print("-" * 30)
        
        cursor.execute("SELECT COUNT(*) FROM project")
        projects = cursor.fetchone()[0]
        print(f"📋 Projekte: {projects}")
        
        cursor.execute("SELECT COUNT(*) FROM spot_price")
        spot_prices = cursor.fetchone()[0]
        print(f"📈 Spot-Preise: {spot_prices}")
        
        cursor.execute("SELECT COUNT(*) FROM dispatch_simulation")
        simulations = cursor.fetchone()[0]
        print(f"🔄 Dispatch-Simulationen: {simulations}")
        
        cursor.execute("SELECT COUNT(*) FROM investment_cost")
        costs = cursor.fetchone()[0]
        print(f"💰 Investment-Costs: {costs}")
        
        cursor.execute("SELECT COUNT(*) FROM apg_scheduler_log")
        logs = cursor.fetchone()[0]
        print(f"📝 APG-Scheduler-Logs: {logs}")
        
        # Tabellen-Liste
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        print(f"\n📋 Tabellen ({len(tables)}):")
        for table in tables:
            print(f"  - {table[0]}")
        
        conn.close()
        
        print("\n✅ HETZNER-Datenbank erfolgreich vorbereitet!")
        print("🚀 Bereit für APG-Scheduler-Installation")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler bei Datenbank-Vorbereitung: {e}")
        return False

if __name__ == "__main__":
    success = prepare_hetzner_database()
    sys.exit(0 if success else 1)
