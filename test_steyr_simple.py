#!/usr/bin/env python3
"""
Einfacher Test für Steyr-Daten mit Jahresauswahl
"""

from ehyd_data_fetcher import EHYDDataFetcher
import sqlite3
from datetime import datetime

def test_steyr_simple():
    """Testet die Steyr-Daten direkt"""
    
    print("🏔️ Einfacher Steyr-Test...")
    print("=" * 60)
    
    # Test 1: Jahresdaten 2024
    print("📅 Test 1: Jahresdaten 2024")
    try:
        fetcher = EHYDDataFetcher()
        result = fetcher.fetch_data_for_year('steyr', 2024, 1, 'Steyr 2024')
        
        if result:
            print(f"✅ Jahresdaten 2024 erfolgreich geladen!")
            print(f"  📊 Fluss: {result['river_name']}")
            print(f"  📈 Datenpunkte: {result['total_data_points']}")
            print(f"  📍 Stationen: {result['stations_count']}")
            print(f"  ✅ Erfolgreich: {result['successful_stations']}")
            print(f"  📅 Zeitraum: {result['start_date']} bis {result['end_date']}")
            print(f"  🎭 Demo: {result['demo']}")
            print(f"  📡 Quelle: {result['source']}")
            
            # Daten in Datenbank speichern
            conn = sqlite3.connect('instance/bess.db')
            cursor = conn.cursor()
            
            saved_count = 0
            for level in result['water_levels']:
                try:
                    cursor.execute('''
                        INSERT INTO water_level 
                        (project_id, profile_name, station_id, station_name, river_name, 
                         timestamp, water_level_cm, source, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        1, 'Steyr 2024', level['station_id'], 
                        level['station_name'], level['river_name'],
                        level['timestamp'], level['water_level_cm'],
                        level['source'], datetime.now().isoformat()
                    ))
                    saved_count += 1
                except Exception as e:
                    print(f"⚠️ Fehler beim Speichern: {e}")
                    continue
            
            conn.commit()
            conn.close()
            
            print(f"💾 {saved_count} Datenpunkte in Datenbank gespeichert")
            
        else:
            print("❌ Keine Daten gefunden")
            
    except Exception as e:
        print(f"❌ Fehler: {e}")
    
    print("\n" + "=" * 60)
    
    # Test 2: Jahresdaten 2023
    print("📅 Test 2: Jahresdaten 2023")
    try:
        result = fetcher.fetch_data_for_year('steyr', 2023, 1, 'Steyr 2023')
        
        if result:
            print(f"✅ Jahresdaten 2023 erfolgreich geladen!")
            print(f"  📊 Fluss: {result['river_name']}")
            print(f"  📈 Datenpunkte: {result['total_data_points']}")
            print(f"  📍 Stationen: {result['stations_count']}")
            print(f"  ✅ Erfolgreich: {result['successful_stations']}")
            print(f"  📅 Zeitraum: {result['start_date']} bis {result['end_date']}")
            print(f"  🎭 Demo: {result['demo']}")
            print(f"  📡 Quelle: {result['source']}")
            
            # Daten in Datenbank speichern
            conn = sqlite3.connect('instance/bess.db')
            cursor = conn.cursor()
            
            saved_count = 0
            for level in result['water_levels']:
                try:
                    cursor.execute('''
                        INSERT INTO water_level 
                        (project_id, profile_name, station_id, station_name, river_name, 
                         timestamp, water_level_cm, source, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        1, 'Steyr 2023', level['station_id'], 
                        level['station_name'], level['river_name'],
                        level['timestamp'], level['water_level_cm'],
                        level['source'], datetime.now().isoformat()
                    ))
                    saved_count += 1
                except Exception as e:
                    print(f"⚠️ Fehler beim Speichern: {e}")
                    continue
            
            conn.commit()
            conn.close()
            
            print(f"💾 {saved_count} Datenpunkte in Datenbank gespeichert")
            
        else:
            print("❌ Keine Daten gefunden")
            
    except Exception as e:
        print(f"❌ Fehler: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Einfacher Steyr-Test abgeschlossen!")

if __name__ == "__main__":
    test_steyr_simple() 