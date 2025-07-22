#!/usr/bin/env python3
"""
Test-Skript für APG-Integration
"""

import requests
import json
from datetime import datetime, timedelta

def test_apg_integration():
    """Testet die APG-Integration"""
    
    base_url = "http://127.0.0.1:5000"
    
    print("🧪 Teste APG-Integration...")
    print("=" * 50)
    
    # Test 1: Spot-Preise abrufen
    print("1. Teste Spot-Preise API")
    try:
        data = {
            "time_range": "today",
            "start_date": datetime.now().strftime("%Y-%m-%d"),
            "end_date": datetime.now().strftime("%Y-%m-%d")
        }
        
        response = requests.post(
            f"{base_url}/api/spot-prices",
            headers={"Content-Type": "application/json"},
            data=json.dumps(data)
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            prices = response.json()
            print(f"   ✅ {len(prices)} Preise erhalten")
            
            if prices:
                first_price = prices[0]
                print(f"   Erster Preis: {first_price.get('price')} €/MWh")
                print(f"   Quelle: {first_price.get('source', 'Unbekannt')}")
                print(f"   Markt: {first_price.get('market', 'Unbekannt')}")
                
                # Statistiken
                price_values = [p['price'] for p in prices]
                avg_price = sum(price_values) / len(price_values)
                max_price = max(price_values)
                min_price = min(price_values)
                
                print(f"   Durchschnitt: {avg_price:.2f} €/MWh")
                print(f"   Maximum: {max_price:.2f} €/MWh")
                print(f"   Minimum: {min_price:.2f} €/MWh")
            else:
                print("   ⚠️ Keine Preise erhalten")
        else:
            print(f"   ❌ Fehler: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    print()
    
    # Test 2: APG Data Fetcher direkt testen
    print("2. Teste APG Data Fetcher direkt")
    try:
        from apg_data_fetcher import APGDataFetcher
        
        fetcher = APGDataFetcher()
        today = datetime.now()
        
        demo_data = fetcher.get_demo_data_based_on_apg(today, today)
        print(f"   ✅ {len(demo_data)} Demo-Daten generiert")
        
        if demo_data:
            first_data = demo_data[0]
            print(f"   Erste Daten: {first_data['price']} €/MWh")
            print(f"   Quelle: {first_data['source']}")
            print(f"   Region: {first_data['region']}")
            
    except ImportError as e:
        print(f"   ❌ Import-Fehler: {e}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    print()
    print("🏁 APG-Integration Test abgeschlossen!")

if __name__ == "__main__":
    test_apg_integration() 