#!/usr/bin/env python3
"""
Test-Skript für den Datenimport
"""

import requests
import json
from datetime import datetime

def test_import_data():
    """Testet den Datenimport direkt"""
    
    print("🔍 Teste Datenimport...")
    print("=" * 50)
    
    # Test-Daten erstellen (mit korrigierten 2024-Daten)
    test_data = {
        'data_type': 'load_profile',
        'profile_name': 'Test-Lastprofil 2024',
        'data': [
            {'timestamp': '2024-02-21 12:07:12', 'value': 53.50},
            {'timestamp': '2024-03-30 03:50:24', 'value': 90.16},
            {'timestamp': '2024-04-09 10:33:36', 'value': 100.44},
            {'timestamp': '2024-02-13 22:48:00', 'value': 45.95},
            {'timestamp': '2024-02-21 23:52:48', 'value': 54.00}
        ]
    }
    
    print("1. Test-Daten vorbereitet:")
    print(f"   Datenart: {test_data['data_type']}")
    print(f"   Profilname: {test_data['profile_name']}")
    print(f"   Anzahl Datensätze: {len(test_data['data'])}")
    
    try:
        # Import-Request senden
        print("\n2. Import-Request senden...")
        response = requests.post(
            'http://127.0.0.1:5000/api/import-data',
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Erfolg: {result.get('success')}")
            print(f"   Nachricht: {result.get('message', 'Keine Nachricht')}")
        else:
            print(f"   ❌ Fehler: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Server nicht erreichbar - ist der Server gestartet?")
    except Exception as e:
        print(f"   ❌ Fehler: {e}")
    
    print("\n3. Datenbank nach Import prüfen...")
    try:
        # Lastprofile abrufen
        response = requests.get('http://127.0.0.1:5000/api/projects/1/load-profiles')
        if response.status_code == 200:
            data = response.json()
            print(f"   Lastprofile: {data}")
        else:
            print(f"   ❌ Fehler beim Abrufen der Lastprofile: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Fehler: {e}")

if __name__ == "__main__":
    test_import_data() 