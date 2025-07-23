#!/usr/bin/env python3
"""
Test-Skript für Steyr Jahresauswahl
"""

import requests
import json

def test_steyr_year_selection():
    """Testet die Jahresauswahl für Steyr-Daten"""
    
    base_url = "http://127.0.0.1:5000"
    
    print("🏔️ Teste Steyr Jahresauswahl...")
    print("=" * 60)
    
    # Test 1: Jahresdaten 2024
    print("📅 Test 1: Jahresdaten 2024")
    try:
        payload = {
            "river_key": "steyr",
            "project_id": 1,
            "profile_name": "Steyr Pegelstände 2024",
            "year": 2024
        }
        
        print(f"📤 Sende Request: {json.dumps(payload, indent=2)}")
        
        response = requests.post(f"{base_url}/api/ehyd/fetch-data", 
                               json=payload,
                               headers={'Content-Type': 'application/json'})
        
        print(f"📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📥 Response Data: {json.dumps(data, indent=2)}")
            
            if data['success']:
                result = data['data']
                print(f"\n✅ Jahresdaten 2024 erfolgreich geladen!")
                print(f"  📊 Fluss: {result['river_name']}")
                print(f"  📈 Datenpunkte: {result['total_data_points']}")
                print(f"  📍 Stationen: {result['stations_count']}")
                print(f"  ✅ Erfolgreich: {result['successful_stations']}")
                print(f"  💾 Gespeichert: {result['saved_count']}")
                print(f"  📅 Zeitraum: {result['start_date']} bis {result['end_date']}")
                print(f"  🎭 Demo: {result['demo']}")
                print(f"  📡 Quelle: {result['source']}")
            else:
                print(f"❌ Fehler: {data['error']}")
        else:
            print(f"❌ Request fehlgeschlagen: {response.status_code}")
            print(f"Response Text: {response.text}")
            
    except Exception as e:
        print(f"❌ Fehler: {e}")
    
    print("\n" + "=" * 60)
    
    # Test 2: Jahresdaten 2023
    print("📅 Test 2: Jahresdaten 2023")
    try:
        payload = {
            "river_key": "steyr",
            "project_id": 1,
            "profile_name": "Steyr Pegelstände 2023",
            "year": 2023
        }
        
        print(f"📤 Sende Request: {json.dumps(payload, indent=2)}")
        
        response = requests.post(f"{base_url}/api/ehyd/fetch-data", 
                               json=payload,
                               headers={'Content-Type': 'application/json'})
        
        print(f"📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📥 Response Data: {json.dumps(data, indent=2)}")
            
            if data['success']:
                result = data['data']
                print(f"\n✅ Jahresdaten 2023 erfolgreich geladen!")
                print(f"  📊 Fluss: {result['river_name']}")
                print(f"  📈 Datenpunkte: {result['total_data_points']}")
                print(f"  📍 Stationen: {result['stations_count']}")
                print(f"  ✅ Erfolgreich: {result['successful_stations']}")
                print(f"  💾 Gespeichert: {result['saved_count']}")
                print(f"  📅 Zeitraum: {result['start_date']} bis {result['end_date']}")
                print(f"  🎭 Demo: {result['demo']}")
                print(f"  📡 Quelle: {result['source']}")
            else:
                print(f"❌ Fehler: {data['error']}")
        else:
            print(f"❌ Request fehlgeschlagen: {response.status_code}")
            print(f"Response Text: {response.text}")
            
    except Exception as e:
        print(f"❌ Fehler: {e}")
    
    print("\n" + "=" * 60)
    
    # Test 3: Demo-Daten (7 Tage)
    print("🎭 Test 3: Demo-Daten (7 Tage)")
    try:
        payload = {
            "river_key": "steyr",
            "project_id": 1,
            "profile_name": "Steyr Demo 7 Tage",
            "start_date": "2024-01-01",
            "end_date": "2024-01-07"
        }
        
        print(f"📤 Sende Request: {json.dumps(payload, indent=2)}")
        
        response = requests.post(f"{base_url}/api/ehyd/fetch-data", 
                               json=payload,
                               headers={'Content-Type': 'application/json'})
        
        print(f"📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📥 Response Data: {json.dumps(data, indent=2)}")
            
            if data['success']:
                result = data['data']
                print(f"\n✅ Demo-Daten erfolgreich geladen!")
                print(f"  📊 Fluss: {result['river_name']}")
                print(f"  📈 Datenpunkte: {result['total_data_points']}")
                print(f"  📍 Stationen: {result['stations_count']}")
                print(f"  ✅ Erfolgreich: {result['successful_stations']}")
                print(f"  💾 Gespeichert: {result['saved_count']}")
                print(f"  📅 Zeitraum: {result['start_date']} bis {result['end_date']}")
                print(f"  🎭 Demo: {result['demo']}")
                print(f"  📡 Quelle: {result['source']}")
            else:
                print(f"❌ Fehler: {data['error']}")
        else:
            print(f"❌ Request fehlgeschlagen: {response.status_code}")
            print(f"Response Text: {response.text}")
            
    except Exception as e:
        print(f"❌ Fehler: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Steyr Jahresauswahl-Test abgeschlossen!")

if __name__ == "__main__":
    test_steyr_year_selection() 