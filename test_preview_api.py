#!/usr/bin/env python3
"""
Test-Skript für die Datenvorschau-API
"""

import requests
import json

def test_preview_api():
    """Testet die exakt gleiche API wie die Datenvorschau"""
    
    print("🔍 Teste Datenvorschau-API...")
    print("=" * 50)
    
    # Exakt die gleichen Parameter wie die Datenvorschau
    test_data = {
        'time_range': 'all'  # "Alle Daten" ausgewählt
    }
    
    print("1. Teste Lastprofile-API (wie Datenvorschau):")
    print(f"   URL: POST /api/projects/1/data/load_profile")
    print(f"   Headers: Content-Type: application/json")
    print(f"   Body: {json.dumps(test_data)}")
    
    try:
        response = requests.post(
            'http://127.0.0.1:5000/api/projects/1/data/load_profile',
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"\n2. Response:")
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type')}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Success: {result.get('success')}")
            print(f"   Count: {result.get('count')}")
            
            if result.get('data'):
                print(f"   Data (erste 3):")
                for i, item in enumerate(result['data'][:3]):
                    print(f"     {i+1}. {item['timestamp']}: {item['value']}")
            else:
                print(f"   ❌ Keine Daten im Response!")
        else:
            print(f"   ❌ HTTP Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Server nicht erreichbar")
    except Exception as e:
        print(f"   ❌ Fehler: {e}")
    
    print("\n3. Browser-Konsole prüfen:")
    print("   Öffnen Sie die Browser-Entwicklertools (F12)")
    print("   Gehen Sie zu 'Console' und prüfen Sie auf Fehler")
    print("   Gehen Sie zu 'Network' und prüfen Sie die API-Calls")

if __name__ == "__main__":
    test_preview_api() 