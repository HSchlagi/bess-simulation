#!/usr/bin/env python3
"""
Test-Script für Referenzpreise API
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_get_reference_prices():
    """Test: Alle Referenzpreise laden"""
    print("🔍 Teste GET /api/reference-prices")
    
    try:
        response = requests.get(f"{BASE_URL}/api/reference-prices")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            prices = response.json()
            print(f"   Anzahl Preise: {len(prices)}")
            for price in prices:
                print(f"   - ID {price['id']}: {price['name']} = {price['price_eur_mwh']} €/kWh")
        else:
            print(f"   Fehler: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Fehler: {e}")

def test_get_single_price(price_id):
    """Test: Einzelnen Preis laden"""
    print(f"\n🔍 Teste GET /api/reference-prices/{price_id}")
    
    try:
        response = requests.get(f"{BASE_URL}/api/reference-prices/{price_id}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            price = response.json()
            print(f"   Preis: {price}")
        else:
            print(f"   Fehler: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Fehler: {e}")

def test_update_price(price_id):
    """Test: Preis aktualisieren"""
    print(f"\n🔄 Teste PUT /api/reference-prices/{price_id}")
    
    update_data = {
        "name": "BESS Standard-Preis (TEST)",
        "price_type": "bess",
        "price_eur_mwh": 250.0,
        "region": "AT",
        "valid_from": "2025-01-01",
        "valid_to": "2025-12-31"
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}/api/reference-prices/{price_id}",
            headers={'Content-Type': 'application/json'},
            data=json.dumps(update_data)
        )
        print(f"   Status: {response.status_code}")
        print(f"   Gesendete Daten: {update_data}")
        
        if response.status_code == 200:
            print("   ✅ Update erfolgreich")
        else:
            print(f"   ❌ Fehler: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Fehler: {e}")

if __name__ == "__main__":
    print("🚀 Starte API-Tests für Referenzpreise")
    
    # Test 1: Alle Preise laden
    test_get_reference_prices()
    
    # Test 2: Ersten Preis laden
    test_get_single_price(1)
    
    # Test 3: Ersten Preis aktualisieren
    test_update_price(1)
    
    # Test 4: Aktualisierten Preis prüfen
    test_get_single_price(1)
    
    print("\n✅ Tests abgeschlossen") 