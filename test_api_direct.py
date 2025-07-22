#!/usr/bin/env python3
"""
Direktes API-Test-Skript
"""

import requests
import json

def test_api_direct():
    """Testet die API direkt"""
    
    print("🔍 Teste API direkt...")
    print("=" * 50)
    
    # Test-Daten für API-Request
    test_data = {
        'time_range': 'all'
    }
    
    print("1. Teste Lastprofile-API:")
    print(f"   URL: /api/projects/1/data/load_profile")
    print(f"   Data: {json.dumps(test_data)}")
    
    try:
        response = requests.post(
            'http://127.0.0.1:5000/api/projects/1/data/load_profile',
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Response: {json.dumps(result, indent=2)}")
            
            if result.get('success'):
                print(f"   ✅ Erfolg: {result.get('count', 0)} Datenpunkte")
            else:
                print(f"   ❌ Fehler: {result.get('error')}")
        else:
            print(f"   ❌ HTTP Fehler: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Server nicht erreichbar - ist der Server gestartet?")
    except Exception as e:
        print(f"   ❌ Fehler: {e}")

if __name__ == "__main__":
    test_api_direct() 