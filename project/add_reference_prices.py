#!/usr/bin/env python3
"""
Datenbank-Migration: Referenzpreise-Tabelle hinzufügen und initialisieren
"""

import sqlite3
import os
from datetime import datetime

def create_reference_prices_table():
    """Erstellt die Referenzpreise-Tabelle"""
    
    # Datenbank-Pfad
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'bess.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Datenbank nicht gefunden: {db_path}")
        return False
    
    try:
        # Verbindung zur Datenbank
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Prüfen ob Tabelle bereits existiert
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='reference_price'")
        if cursor.fetchone():
            print("✅ Referenzpreise-Tabelle existiert bereits")
        else:
            # Tabelle erstellen
            cursor.execute('''
                CREATE TABLE reference_price (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    technology VARCHAR(50) NOT NULL UNIQUE,
                    name VARCHAR(100) NOT NULL,
                    icon VARCHAR(50),
                    color VARCHAR(20),
                    investment_cost_min FLOAT,
                    investment_cost_max FLOAT,
                    investment_unit VARCHAR(10),
                    operation_cost_percent FLOAT,
                    example_capacity FLOAT,
                    description TEXT,
                    notes TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            print("✅ Referenzpreise-Tabelle erstellt")
        
        # Standard-Referenzpreise einfügen
        default_prices = [
            {
                'technology': 'bess',
                'name': 'BESS (Batteriespeicher)',
                'icon': 'fas fa-battery-full',
                'color': 'green',
                'investment_cost_min': 400,
                'investment_cost_max': 800,
                'investment_unit': 'kWh',
                'operation_cost_percent': 1.25,
                'example_capacity': 500,
                'description': 'Lithium-Ionen Batteriespeicher für Energiespeicherung',
                'notes': 'Preise variieren je nach Technologie und Hersteller'
            },
            {
                'technology': 'pv',
                'name': 'Photovoltaik',
                'icon': 'fas fa-solar-panel',
                'color': 'yellow',
                'investment_cost_min': 800,
                'investment_cost_max': 1200,
                'investment_unit': 'kWp',
                'operation_cost_percent': 1.0,
                'example_capacity': 30,
                'description': 'Photovoltaik-Anlage mit Modulen und Wechselrichter',
                'notes': 'Preise sinken kontinuierlich, Förderungen möglich'
            },
            {
                'technology': 'hp',
                'name': 'Wärmepumpe',
                'icon': 'fas fa-thermometer-half',
                'color': 'blue',
                'investment_cost_min': 1500,
                'investment_cost_max': 2500,
                'investment_unit': 'kW',
                'operation_cost_percent': 1.3,
                'example_capacity': 10,
                'description': 'Luft-Wasser oder Sole-Wasser Wärmepumpe',
                'notes': 'Preise abhängig von Wärmequelle und Leistung'
            },
            {
                'technology': 'wind',
                'name': 'Windkraft',
                'icon': 'fas fa-wind',
                'color': 'gray',
                'investment_cost_min': 2000,
                'investment_cost_max': 3000,
                'investment_unit': 'kW',
                'operation_cost_percent': 1.0,
                'example_capacity': 20,
                'description': 'Kleinwindanlage für lokale Stromerzeugung',
                'notes': 'Preise stark abhängig von Standort und Windverhältnissen'
            },
            {
                'technology': 'hydro',
                'name': 'Wasserkraft',
                'icon': 'fas fa-water',
                'color': 'cyan',
                'investment_cost_min': 1500,
                'investment_cost_max': 4000,
                'investment_unit': 'kW',
                'operation_cost_percent': 1.0,
                'example_capacity': 15,
                'description': 'Kleinwasserkraftwerk für lokale Stromerzeugung',
                'notes': 'Preise stark abhängig von Fallhöhe und Durchfluss'
            }
        ]
        
        # Prüfen ob bereits Daten vorhanden sind
        cursor.execute("SELECT COUNT(*) FROM reference_price")
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Standard-Daten einfügen
            for price in default_prices:
                cursor.execute('''
                    INSERT INTO reference_price (
                        technology, name, icon, color, investment_cost_min, investment_cost_max,
                        investment_unit, operation_cost_percent, example_capacity, description, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    price['technology'], price['name'], price['icon'], price['color'],
                    price['investment_cost_min'], price['investment_cost_max'], price['investment_unit'],
                    price['operation_cost_percent'], price['example_capacity'], price['description'], price['notes']
                ))
            print("✅ Standard-Referenzpreise eingefügt")
        else:
            print(f"✅ {count} Referenzpreise bereits vorhanden")
        
        # Änderungen speichern
        conn.commit()
        
        # Bestätigung anzeigen
        cursor.execute("SELECT * FROM reference_price")
        prices = cursor.fetchall()
        print(f"\n📋 {len(prices)} Referenzpreise verfügbar:")
        for price in prices:
            print(f"  • {price[2]} ({price[1]}) - {price[6]}-{price[7]} €/{price[8]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Erstellen der Referenzpreise: {e}")
        return False
    
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🚀 Starte Referenzpreise-Migration...")
    success = create_reference_prices_table()
    
    if success:
        print("\n🎉 Migration erfolgreich abgeschlossen!")
        print("\n💰 Verfügbare Referenzpreise:")
        print("  • BESS (Batteriespeicher) - 400-800 €/kWh")
        print("  • Photovoltaik - 800-1200 €/kWp")
        print("  • Wärmepumpe - 1500-2500 €/kW")
        print("  • Windkraft - 2000-3000 €/kW")
        print("  • Wasserkraft - 1500-4000 €/kW")
        print("\n📝 Diese Preise können jetzt über die Verwaltungsseite bearbeitet werden!")
    else:
        print("\n💥 Migration fehlgeschlagen!") 