#!/usr/bin/env python3
"""
Test API Filter - Testet die Spot-Preis-API direkt
"""

import requests
import json
from datetime import datetime

def test_api_filter():
    """Testet die Spot-Preis-API mit verschiedenen Filtern"""
    
    print("🌐 Teste Spot-Preis-API Filter...")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:5000"
    
    # Test 1: 2024 (ganzes Jahr)
    print("📅 Test 1: 2024 (ganzes Jahr)")
    payload_2024 = {
        "time_range": "year",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31"
    }
    
    try:
        response = requests.post(f"{base_url}/api/spot-prices", 
                               json=payload_2024, 
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Status: {result.get('success')}")
            print(f"   📊 Datenpunkte: {len(result.get('data', []))}")
            print(f"   📋 Datenquelle: {result.get('source')}")
            print(f"   💬 Nachricht: {result.get('message')}")
        else:
            print(f"   ❌ HTTP-Fehler: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Fehler: {e}")
    
    # Test 2: Januar 2024
    print("\n📅 Test 2: Januar 2024")
    payload_jan = {
        "time_range": "month",
        "start_date": "2024-01-01",
        "end_date": "2024-01-31"
    }
    
    try:
        response = requests.post(f"{base_url}/api/spot-prices", 
                               json=payload_jan, 
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Status: {result.get('success')}")
            print(f"   📊 Datenpunkte: {len(result.get('data', []))}")
            print(f"   📋 Datenquelle: {result.get('source')}")
            print(f"   💬 Nachricht: {result.get('message')}")
        else:
            print(f"   ❌ HTTP-Fehler: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Fehler: {e}")
    
    # Test 3: Heute (2025)
    print("\n📅 Test 3: Heute (2025)")
    today = datetime.now().strftime("%Y-%m-%d")
    payload_today = {
        "time_range": "today",
        "start_date": today,
        "end_date": today
    }
    
    try:
        response = requests.post(f"{base_url}/api/spot-prices", 
                               json=payload_today, 
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Status: {result.get('success')}")
            print(f"   📊 Datenpunkte: {len(result.get('data', []))}")
            print(f"   📋 Datenquelle: {result.get('source')}")
            print(f"   💬 Nachricht: {result.get('message')}")
        else:
            print(f"   ❌ HTTP-Fehler: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Fehler: {e}")
    
    print("\n" + "=" * 50)
    print("✅ API-Filter-Test abgeschlossen!")

if __name__ == "__main__":
    test_api_filter() 