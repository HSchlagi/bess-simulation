#!/usr/bin/env python3
"""
Script zum Setzen von daily_cycles auf 2.5
"""

import requests
import json

def set_daily_cycles_to_2_5():
    """Setzt daily_cycles auf 2.5"""
    
    project_id = 1  # BESS Hinterstoder
    
    try:
        print("🔧 Setze daily_cycles auf 2.5...")
        
        # Aktualisiere das Projekt
        update_data = {
            "name": "BESS Hinterstoder",
            "location": "Hinterstoder, Österreich",
            "customer_id": 4,
            "date": "2025-07-23",
            "bess_size": 8000,
            "bess_power": 2000,
            "pv_power": 1950,
            "hp_power": None,
            "wind_power": None,
            "hydro_power": 650,
            "other_power": None,
            "daily_cycles": 2.5,  # Hier setzen wir 2.5
            "current_electricity_cost": 12.5,
            "bess_cost": 1680000,
            "pv_cost": 1650000,
            "hp_cost": None,
            "wind_cost": None,
            "hydro_cost": 2300000,
            "other_cost": 500000
        }
        
        print(f"   Sende daily_cycles: {update_data['daily_cycles']}")
        
        response = requests.put(
            f'http://127.0.0.1:5000/api/projects/{project_id}',
            json=update_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Projekt aktualisiert")
            print(f"   Antwort: {result}")
            
            # Prüfe das Ergebnis
            print("🔍 Prüfe das Ergebnis...")
            response = requests.get(f'http://127.0.0.1:5000/api/projects/{project_id}')
            
            if response.status_code == 200:
                project = response.json()
                daily_cycles = project.get('daily_cycles')
                print(f"✅ Projekt nach Update geladen")
                print(f"   daily_cycles: {daily_cycles}")
                print(f"   Typ: {type(daily_cycles)}")
                
                if daily_cycles == 2.5:
                    print("✅ daily_cycles korrekt auf 2.5 gesetzt!")
                else:
                    print(f"❌ daily_cycles falsch: erwartet 2.5, erhalten {daily_cycles}")
            else:
                print(f"❌ Fehler beim Laden: {response.status_code}")
        else:
            print(f"❌ Fehler beim Aktualisieren: {response.status_code}")
            print(f"   Antwort: {response.text}")
            
    except Exception as e:
        print(f"❌ Fehler: {e}")

if __name__ == "__main__":
    set_daily_cycles_to_2_5()
