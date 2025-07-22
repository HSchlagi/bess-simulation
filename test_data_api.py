#!/usr/bin/env python3
"""
Test-Skript für die korrigierte Daten-API
"""

import requests
import json

def test_data_api():
    """Testet die korrigierte Daten-API"""
    
    print("🔍 Teste korrigierte Daten-API...")
    print("=" * 50)
    
    try:
        # Test-Daten für API-Request
        test_data = {
            'time_range': 'all'
        }
        
        print("1. Teste Lastprofile-Daten für Projekt 1:")
        response = requests.post(
            'http://127.0.0.1:5000/api/projects/1/data/load_profile',
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Erfolg: {result.get('success')}")
            print(f"   Anzahl Datenpunkte: {result.get('count', 0)}")
            
            if result.get('data'):
                print("   Erste 3 Datenpunkte:")
                for i, data_point in enumerate(result['data'][:3]):
                    print(f"     {i+1}. {data_point['timestamp']}: {data_point['value']} kW")
            else:
                print("   ❌ Keine Daten gefunden")
        else:
            print(f"   ❌ Fehler: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Server nicht erreichbar - ist der Server gestartet?")
    except Exception as e:
        print(f"   ❌ Fehler: {e}")

if __name__ == "__main__":
    test_data_api() 