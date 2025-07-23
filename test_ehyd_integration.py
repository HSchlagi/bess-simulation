#!/usr/bin/env python3
"""
Test-Skript für EHYD-Integration
Testet die komplette EHYD-Integration mit API-Aufrufen
"""

import requests
import json
from datetime import datetime

def test_ehyd_integration():
    """Testet die komplette EHYD-Integration"""
    
    base_url = "http://127.0.0.1:5000"
    
    print("🌊 Teste EHYD-Integration...")
    print("=" * 60)
    
    # Test 1: Flüsse laden
    print("📋 Test 1: Flüsse laden")
    try:
        response = requests.get(f"{base_url}/api/ehyd/rivers")
        data = response.json()
        
        if data['success']:
            print(f"✅ {len(data['rivers'])} Flüsse geladen:")
            for key, name in data['rivers'].items():
                print(f"  - {key}: {name}")
        else:
            print(f"❌ Fehler: {data['error']}")
    except Exception as e:
        print(f"❌ Netzwerkfehler: {e}")
    
    print("\n" + "=" * 60)
    
    # Test 2: Stationen für Donau laden
    print("📡 Test 2: Stationen für Donau laden")
    try:
        response = requests.get(f"{base_url}/api/ehyd/stations/donau")
        data = response.json()
        
        if data['success']:
            print(f"✅ {len(data['stations'])} Stationen für {data['river_key']} geladen:")
            for station in data['stations'][:3]:  # Nur erste 3 anzeigen
                print(f"  - {station['name']} (ID: {station['id']})")
        else:
            print(f"❌ Fehler: {data['error']}")
    except Exception as e:
        print(f"❌ Netzwerkfehler: {e}")
    
    print("\n" + "=" * 60)
    
    # Test 3: EHYD-Daten laden (Demo)
    print("📊 Test 3: EHYD-Daten laden (Demo)")
    try:
        payload = {
            'river_key': 'donau',
            'project_id': 1,
            'profile_name': 'Test-Donau-2024',
            'start_date': '2024-01-01',
            'end_date': '2024-01-07'
        }
        
        response = requests.post(f"{base_url}/api/ehyd/fetch-data", 
                               json=payload,
                               headers={'Content-Type': 'application/json'})
        data = response.json()
        
        if data['success']:
            result = data['data']
            print(f"✅ EHYD-Daten erfolgreich geladen:")
            print(f"  📊 Fluss: {result['river_name']}")
            print(f"  📈 Datenpunkte: {result['total_data_points']}")
            print(f"  📍 Stationen: {result['stations_count']}")
            print(f"  ✅ Erfolgreich: {result['successful_stations']}")
            print(f"  💾 Gespeichert: {result['saved_count']}")
            print(f"  📅 Zeitraum: {result['start_date']} bis {result['end_date']}")
            print(f"  🔍 Quelle: {result['source']}")
            print(f"  🎭 Demo: {result['demo']}")
        else:
            print(f"❌ Fehler: {data['error']}")
    except Exception as e:
        print(f"❌ Netzwerkfehler: {e}")
    
    print("\n" + "=" * 60)
    
    # Test 4: Pegelstanddaten abrufen
    print("🌊 Test 4: Pegelstanddaten abrufen")
    try:
        response = requests.get(f"{base_url}/api/water-levels?start_date=2024-01-01&end_date=2024-01-07")
        data = response.json()
        
        if data['success']:
            print(f"✅ {len(data['data'])} Pegelstanddaten geladen")
            print(f"📋 Quelle: {data['source']}")
            print(f"💬 Nachricht: {data['message']}")
            
            if data['data']:
                print("\n📈 Erste 5 Datenpunkte:")
                for i, level in enumerate(data['data'][:5]):
                    print(f"  {i+1}. {level['timestamp']} - {level['station_name']}: {level['water_level_cm']} cm")
        else:
            print(f"❌ Fehler: {data['error']}")
    except Exception as e:
        print(f"❌ Netzwerkfehler: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 EHYD-Integration Test abgeschlossen!")

if __name__ == "__main__":
    test_ehyd_integration() 