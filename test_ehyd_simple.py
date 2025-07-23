#!/usr/bin/env python3
"""
Einfacher EHYD-Test ohne API-Aufrufe
"""

from ehyd_data_fetcher import EHYDDataFetcher
import sqlite3
from datetime import datetime

def test_ehyd_simple():
    """Testet die EHYD-Integration direkt"""
    
    print("🌊 Teste EHYD-Integration (direkt)...")
    print("=" * 60)
    
    # Test 1: EHYD Data Fetcher
    print("📋 Test 1: EHYD Data Fetcher")
    try:
        fetcher = EHYDDataFetcher()
        rivers = fetcher.get_rivers()
        print(f"✅ {len(rivers)} Flüsse verfügbar:")
        for key, name in rivers.items():
            print(f"  - {key}: {name}")
    except Exception as e:
        print(f"❌ Fehler: {e}")
    
    print("\n" + "=" * 60)
    
    # Test 2: Stationen für Donau
    print("📡 Test 2: Stationen für Donau")
    try:
        stations = fetcher.get_stations_by_river('donau')
        print(f"✅ {len(stations)} Stationen für Donau:")
        for station in stations[:3]:
            print(f"  - {station['name']} (ID: {station['id']})")
    except Exception as e:
        print(f"❌ Fehler: {e}")
    
    print("\n" + "=" * 60)
    
    # Test 3: Demo-Daten generieren
    print("📊 Test 3: Demo-Daten generieren")
    try:
        demo_data = fetcher.get_demo_data('donau', 7)
        print(f"✅ Demo-Daten generiert:")
        print(f"  📊 Fluss: {demo_data['river_name']}")
        print(f"  📈 Datenpunkte: {demo_data['total_data_points']}")
        print(f"  📍 Stationen: {demo_data['stations_count']}")
        print(f"  📅 Zeitraum: {demo_data['start_date']} bis {demo_data['end_date']}")
        print(f"  🎭 Demo: {demo_data['demo']}")
    except Exception as e:
        print(f"❌ Fehler: {e}")
    
    print("\n" + "=" * 60)
    
    # Test 4: Datenbank-Verbindung
    print("💾 Test 4: Datenbank-Verbindung")
    try:
        conn = sqlite3.connect('instance/bess.db')
        cursor = conn.cursor()
        
        # Prüfe water_level Tabelle
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='water_level'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("✅ water_level Tabelle existiert")
            
            # Prüfe Datensätze
            cursor.execute("SELECT COUNT(*) FROM water_level")
            count = cursor.fetchone()[0]
            print(f"📊 Aktuelle Datensätze: {count}")
            
            if count > 0:
                # Zeige erste Datensätze
                cursor.execute("SELECT timestamp, water_level_cm, station_name, river_name FROM water_level LIMIT 3")
                rows = cursor.fetchall()
                print("📈 Erste Datensätze:")
                for i, row in enumerate(rows):
                    print(f"  {i+1}. {row[0]} - {row[2]}: {row[1]} cm ({row[3]})")
        else:
            print("❌ water_level Tabelle existiert nicht")
        
        conn.close()
    except Exception as e:
        print(f"❌ Datenbankfehler: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 EHYD-Integration Test abgeschlossen!")

if __name__ == "__main__":
    test_ehyd_simple() 