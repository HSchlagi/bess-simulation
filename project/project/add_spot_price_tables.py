#!/usr/bin/env python3
"""
Datenbank-Migration: Spot-Preis Tabellen hinzufügen
"""

import sqlite3
import os

def add_spot_price_tables():
    """Fügt die Spot-Preis Tabellen zur Datenbank hinzu"""
    
    # Datenbank-Pfad
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'bess.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Datenbank nicht gefunden: {db_path}")
        return False
    
    try:
        # Verbindung zur Datenbank
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Prüfen ob Tabellen bereits existieren
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [table[0] for table in cursor.fetchall()]
        
        # SpotPrice Tabelle
        if 'spot_price' not in existing_tables:
            print("🔄 Erstelle SpotPrice Tabelle...")
            cursor.execute("""
                CREATE TABLE spot_price (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    price_eur_mwh FLOAT NOT NULL,
                    source VARCHAR(50),
                    region VARCHAR(10),
                    price_type VARCHAR(20),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Index für bessere Performance
            cursor.execute("""
                CREATE INDEX idx_spot_timestamp ON spot_price (timestamp)
            """)
            print("✅ SpotPrice Tabelle erstellt")
        else:
            print("✅ SpotPrice Tabelle existiert bereits")
        
        # SpotPriceConfig Tabelle
        if 'spot_price_config' not in existing_tables:
            print("🔄 Erstelle SpotPriceConfig Tabelle...")
            cursor.execute("""
                CREATE TABLE spot_price_config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source VARCHAR(50) NOT NULL,
                    region VARCHAR(10) DEFAULT 'AT',
                    update_frequency VARCHAR(20) DEFAULT 'daily',
                    api_key VARCHAR(200),
                    is_active BOOLEAN DEFAULT 1,
                    last_update DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✅ SpotPriceConfig Tabelle erstellt")
        else:
            print("✅ SpotPriceConfig Tabelle existiert bereits")
        
        # EconomicAnalysis Tabelle
        if 'economic_analysis' not in existing_tables:
            print("🔄 Erstelle EconomicAnalysis Tabelle...")
            cursor.execute("""
                CREATE TABLE economic_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    analysis_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    analysis_type VARCHAR(50),
                    annual_arbitrage_potential FLOAT,
                    optimal_cycles_per_year INTEGER,
                    avg_price_spread FLOAT,
                    annual_peak_shaving_savings FLOAT,
                    peak_hours_per_day FLOAT,
                    avg_peak_price FLOAT,
                    total_investment FLOAT,
                    annual_savings FLOAT,
                    payback_period_years FLOAT,
                    roi_percentage FLOAT,
                    bess_capacity_kwh FLOAT,
                    bess_power_kw FLOAT,
                    efficiency FLOAT DEFAULT 0.9,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES project (id)
                )
            """)
            print("✅ EconomicAnalysis Tabelle erstellt")
        else:
            print("✅ EconomicAnalysis Tabelle existiert bereits")
        
        # Standard-Konfiguration einfügen
        cursor.execute("SELECT COUNT(*) FROM spot_price_config")
        config_count = cursor.fetchone()[0]
        
        if config_count == 0:
            print("🔄 Füge Standard-Konfiguration hinzu...")
            cursor.execute("""
                INSERT INTO spot_price_config (source, region, update_frequency, is_active)
                VALUES ('ENTSO-E', 'AT', 'daily', 1)
            """)
            print("✅ Standard-Konfiguration hinzugefügt")
        
        # Änderungen speichern
        conn.commit()
        
        # Bestätigung anzeigen
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("\n📋 Aktuelle Tabellen:")
        for table in tables:
            print(f"  - {table[0]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Erstellen der Tabellen: {e}")
        return False
    
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🚀 Starte Spot-Preis Tabellen Migration...")
    success = add_spot_price_tables()
    
    if success:
        print("\n🎉 Migration erfolgreich abgeschlossen!")
        print("\n📊 Verfügbare Features:")
        print("  • Spot-Preis Import (ENTSO-E, APG, EPEX)")
        print("  • Arbitrage-Berechnungen")
        print("  • Peak-Shaving Analysen")
        print("  • ROI-Berechnungen")
        print("  • Wirtschaftlichkeits-Analysen")
    else:
        print("\n💥 Migration fehlgeschlagen!") 