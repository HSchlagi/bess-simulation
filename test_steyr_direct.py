#!/usr/bin/env python3
"""
Direkter Test für Steyr-Daten-Import
"""

import requests
import json

def test_steyr_direct_import():
    """Testet den direkten Import von Steyr-Daten"""
    
    base_url = "http://127.0.0.1:5000"
    
    print("🏔️ Direkter Steyr-Import Test...")
    print("=" * 60)
    
    # Test: EHYD-Daten für Steyr laden
    print("📊 Importiere Steyr-Daten für Projekt...")
    try:
        payload = {
            "river_key": "steyr",
            "project_id": 1,  # BESS Hinterstoder Projekt
            "profile_name": "Steyr Pegelstände 2024",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31"
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
                print(f"\n✅ Import erfolgreich!")
                print(f"  📊 Fluss: {result['river_name']}")
                print(f"  📈 Datenpunkte: {result['total_data_points']}")
                print(f"  📍 Stationen: {result['stations_count']}")
                print(f"  ✅ Erfolgreich: {result['successful_stations']}")
                print(f"  💾 Gespeichert: {result['saved_count']}")
                print(f"  📅 Zeitraum: {result['start_date']} bis {result['end_date']}")
                print(f"  🎭 Demo: {result['demo']}")
                
                # Test: Daten aus der Datenbank abfragen
                print(f"\n🔍 Teste Datenbank-Abfrage...")
                db_response = requests.get(f"{base_url}/api/water-levels?project_id=1&start_date=2024-01-01&end_date=2024-01-07")
                
                if db_response.status_code == 200:
                    db_data = db_response.json()
                    if db_data['success']:
                        print(f"✅ {len(db_data['data'])} Datenpunkte in der Datenbank gefunden")
                        if db_data['data']:
                            print(f"📊 Erste Datenpunkte:")
                            for i, point in enumerate(db_data['data'][:5]):
                                print(f"  {i+1}. {point['timestamp']} - {point['station_name']}: {point['water_level_cm']} cm")
                    else:
                        print(f"❌ Datenbank-Fehler: {db_data['error']}")
                else:
                    print(f"❌ Datenbank-Request fehlgeschlagen: {db_response.status_code}")
                
            else:
                print(f"❌ Import fehlgeschlagen: {data['error']}")
        else:
            print(f"❌ Request fehlgeschlagen: {response.status_code}")
            print(f"Response Text: {response.text}")
            
    except Exception as e:
        print(f"❌ Fehler: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Direkter Import-Test abgeschlossen!")

if __name__ == "__main__":
    test_steyr_direct_import() 