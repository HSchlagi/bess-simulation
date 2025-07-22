#!/usr/bin/env python3
"""
Test-Skript für Customer-API
"""

import requests
import json

def test_customer_api():
    """Testet die Customer-API"""
    
    base_url = "http://127.0.0.1:5000"
    
    print("🧪 Teste Customer-API...")
    print("=" * 50)
    
    # Test 1: Kunde abrufen
    print("1. Teste GET /api/customers/3")
    try:
        response = requests.get(f"{base_url}/api/customers/3")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            customer = response.json()
            print(f"   ✅ Kunde gefunden: {customer.get('name')}")
        else:
            print(f"   ❌ Fehler: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    print()
    
    # Test 2: Kunde aktualisieren
    print("2. Teste PUT /api/customers/3")
    try:
        update_data = {
            "name": "Heinz Schlagintweit",
            "company": "Schlagintweit & Co Elektrotechnik u. Planungs KG",
            "contact": "office@instanet.at",
            "phone": "+43 123 456 789"
        }
        
        response = requests.put(
            f"{base_url}/api/customers/3",
            headers={"Content-Type": "application/json"},
            data=json.dumps(update_data)
        )
        
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Update erfolgreich: {result}")
        else:
            print(f"   ❌ Update fehlgeschlagen: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    print()
    print("🏁 Test abgeschlossen!")

if __name__ == "__main__":
    test_customer_api() 