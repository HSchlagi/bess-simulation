#!/usr/bin/env python3
"""
Test-Skript für Steyr API-Integration
"""

import requests
import json

def test_steyr_api():
    """Testet die Steyr API-Integration"""
    
    base_url = "http://127.0.0.1:5000"
    
    print("🏔️ Teste Steyr API-Integration...")
    print("=" * 60)
    
    # Test 1: Flüsse laden
    print("🌊 Test 1: Flüsse laden")
    try:
        response = requests.get(f"{base_url}/api/ehyd/rivers")
        data = response.json()
        
        if data['success']:
            rivers = data['rivers']
            if 'steyr' in rivers:
                print(f"✅ Steyr gefunden: {rivers['steyr']}")
            else:
                print("❌ Steyr nicht gefunden")
                print("Verfügbare Flüsse:", list(rivers.keys())[:10])
        else:
            print(f"❌ Fehler: {data['error']}")
    except Exception as e:
        print(f"❌ Netzwerkfehler: {e}")
    
    print("\n" + "=" * 60)
    
    # Test 2: Stationen für Steyr laden
    print("🏔️ Test 2: Stationen für Steyr laden")
    try:
        response = requests.get(f"{base_url}/api/ehyd/stations/steyr")
        data = response.json()
        
        if data['success']:
            stations = data['stations']
            print(f"✅ {len(stations)} Stationen für Steyr:")
            for station in stations:
                print(f"  - {station['name']} (ID: {station['id']})")
                
            # Suche nach Hinterstoder
            hinterstoder = [s for s in stations if 'Hinterstoder' in s['name']]
            if hinterstoder:
                print(f"\n🎯 Hinterstoder gefunden: {hinterstoder[0]['name']} (ID: {hinterstoder[0]['id']})")
            else:
                print("❌ Hinterstoder nicht gefunden")
        else:
            print(f"❌ Fehler: {data['error']}")
    except Exception as e:
        print(f"❌ Netzwerkfehler: {e}")
    
    print("\n" + "=" * 60)
    
    # Test 3: EHYD-Daten für Steyr laden
    print("📊 Test 3: EHYD-Daten für Steyr laden")
    try:
        payload = {
            "river_key": "steyr",
            "project_id": 1,
            "profile_name": "Steyr Test 2024",
            "start_date": "2024-01-01",
            "end_date": "2024-01-07"
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
            print(f"  🎭 Demo: {result['demo']}")
        else:
            print(f"❌ Fehler: {data['error']}")
    except Exception as e:
        print(f"❌ Netzwerkfehler: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Steyr API-Test abgeschlossen!")

if __name__ == "__main__":
    test_steyr_api() 