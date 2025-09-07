#!/usr/bin/env python3
"""
Migration für CO₂-Tracking System
Erstellt alle notwendigen Tabellen und Daten für das Nachhaltigkeits-System
"""

import sqlite3
import sys
import os

# CO₂-Tracking System importieren
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from co2_tracking_system import CO2TrackingSystem

def run_migration():
    """Führt die CO₂-Tracking Migration durch"""
    
    print("🌱 CO₂-Tracking System Migration")
    print("=" * 50)
    
    # Datenbankpfad prüfen
    db_path = 'instance/bess.db'
    if not os.path.exists(db_path):
        print(f"❌ Datenbank nicht gefunden: {db_path}")
        return False
    
    try:
        # CO₂-Tracking System initialisieren
        co2_system = CO2TrackingSystem(db_path)
        
        # Tabellen erstellen
        print("📋 Erstelle CO₂-Tracking Tabellen...")
        co2_system.create_co2_tables()
        
        # Test-Daten erstellen (Demo)
        print("🧪 Erstelle Demo-Daten...")
        create_demo_data(co2_system)
        
        print("✅ CO₂-Tracking Migration erfolgreich abgeschlossen!")
        
        # Test der Migration
        print("\n🧪 Teste Migration...")
        test_migration(db_path)
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler bei der Migration: {e}")
        return False

def create_demo_data(co2_system):
    """Erstellt Demo-Daten für das CO₂-Tracking System"""
    
    from datetime import datetime, timedelta
    import random
    
    # Demo-Projekt-ID (falls vorhanden)
    project_id = 1
    
    # Demo-Daten für die letzten 30 Tage erstellen
    for i in range(30):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        
        # Zufällige Energie-Daten generieren
        energy_data = {
            'energy_stored_kwh': random.uniform(100, 500),
            'energy_discharged_kwh': random.uniform(80, 450),
            'grid_energy_kwh': random.uniform(50, 200),
            'renewable_energy_kwh': random.uniform(200, 400)
        }
        
        # CO₂-Bilanz berechnen
        co2_balance = co2_system.calculate_co2_balance(project_id, date, energy_data)
        
        # CO₂-Bilanz speichern
        co2_system.save_co2_balance(co2_balance)
    
    print(f"✅ Demo-Daten für {project_id} Tage erstellt")

def test_migration(db_path):
    """Testet die Migration"""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Tabellen prüfen
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%co2%'")
    co2_tables = [row[0] for row in cursor.fetchall()]
    print(f"✅ {len(co2_tables)} CO₂-Tabellen gefunden: {co2_tables}")
    
    # CO₂-Balance-Daten prüfen
    cursor.execute("SELECT COUNT(*) FROM co2_balance")
    co2_count = cursor.fetchone()[0]
    print(f"✅ {co2_count} CO₂-Bilanz-Einträge vorhanden")
    
    # CO₂-Faktoren prüfen
    cursor.execute("SELECT COUNT(*) FROM co2_factors")
    factors_count = cursor.fetchone()[0]
    print(f"✅ {factors_count} CO₂-Faktoren konfiguriert")
    
    # Nachhaltigkeits-Metriken generieren
    co2_system = CO2TrackingSystem(db_path)
    metrics = co2_system.generate_sustainability_metrics(
        1, '2024-01-01', '2024-12-31', 'yearly'
    )
    print(f"✅ Nachhaltigkeits-Metriken generiert: {metrics['total_energy_kwh']} kWh")
    
    # ESG-Report generieren
    esg_report = co2_system.generate_esg_report(1, 'yearly')
    print(f"✅ ESG-Report generiert: Score {esg_report['overall_esg_score']}")
    
    conn.close()
    
    print("\n🎯 Nächste Schritte:")
    print("1. CO₂-Dashboard testen: /co2")
    print("2. Demo-Daten überprüfen")
    print("3. ESG-Reports generieren")
    print("4. Benchmark-Daten analysieren")

if __name__ == '__main__':
    success = run_migration()
    sys.exit(0 if success else 1)
