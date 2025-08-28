#!/usr/bin/env python3
"""
Test-Script für die elegante URL-Lösung
"""

import requests
import json

def test_elegant_solution():
    """Testet die elegante URL-Lösung"""
    
    try:
        print("🧪 Teste elegante URL-Lösung...")
        
        # 1. Teste URL mit Formulardaten aber ohne ID (BESS Hinterstoder)
        print("1. Teste URL mit Formulardaten (BESS Hinterstoder)...")
        test_url = 'http://127.0.0.1:5000/edit_project?name=BESS+Hinterstoder&location=Hinterstoder,+Österreich&customer_id=4&date=2025-07-23&bess_size=8000&bess_power=2000&pv_power=1950&hp_power=&wind_power=&hydro_power=650&other_power=&current_electricity_cost=12.5&daily_cycles=2.5&bess_cost=1680000&pv_cost=1650000&hp_cost=&wind_cost=&hydro_cost=2300000&other_cost=500000'
        
        response = requests.get(test_url)
        
        if response.status_code == 200:
            print("✅ Seite geladen")
            # Prüfe ob die Seite eine Weiterleitung zur sauberen URL macht
            if 'id=1' in response.url or 'id=1' in str(response.content):
                print("✅ Weiterleitung zur sauberen URL erkannt")
            else:
                print("⚠️ Keine Weiterleitung zur sauberen URL erkannt")
        else:
            print(f"❌ Seite nicht geladen: {response.status_code}")
        
        # 2. Teste URL mit Solar-BESS Wien
        print("2. Teste URL mit Formulardaten (Solar-BESS Wien)...")
        test_url2 = 'http://127.0.0.1:5000/edit_project?name=Solar-BESS+Wien&location=Wien,+Österreich&customer_id=1&date=2025-07-23&bess_size=200&bess_power=150&pv_power=100&hp_power=&wind_power=&hydro_power=&other_power=&current_electricity_cost=12.5&daily_cycles=1.5&bess_cost=40000&pv_cost=80000&hp_cost=&wind_cost=&hydro_cost=&other_cost='
        
        response = requests.get(test_url2)
        
        if response.status_code == 200:
            print("✅ Seite geladen")
            # Prüfe ob die Seite eine Weiterleitung zur sauberen URL macht
            if 'id=3' in response.url or 'id=3' in str(response.content):
                print("✅ Weiterleitung zur sauberen URL erkannt")
            else:
                print("⚠️ Keine Weiterleitung zur sauberen URL erkannt")
        else:
            print(f"❌ Seite nicht geladen: {response.status_code}")
        
        # 3. Teste URL mit ungültigen Daten
        print("3. Teste URL mit ungültigen Daten...")
        test_url3 = 'http://127.0.0.1:5000/edit_project?name=Unbekanntes+Projekt&location=Unbekannt&customer_id=999&date=2025-07-23&bess_size=100&bess_power=50&pv_power=75&hp_power=&wind_power=&hydro_power=&other_power=&current_electricity_cost=12.5&daily_cycles=1.5&bess_cost=20000&pv_cost=40000&hp_cost=&wind_cost=&hydro_cost=&other_cost='
        
        response = requests.get(test_url3)
        
        if response.status_code == 200:
            print("✅ Seite geladen")
            # Prüfe ob die Seite eine Weiterleitung zur Projekt-Übersicht macht
            if 'projects' in response.url or 'projects' in str(response.content):
                print("✅ Weiterleitung zur Projekt-Übersicht erkannt")
            else:
                print("⚠️ Keine Weiterleitung zur Projekt-Übersicht erkannt")
        else:
            print(f"❌ Seite nicht geladen: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Fehler beim Testen: {e}")

if __name__ == "__main__":
    test_elegant_solution()
