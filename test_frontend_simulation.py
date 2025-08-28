#!/usr/bin/env python3
"""
Test-Script für Frontend-Simulation
"""

import requests
import json

def test_frontend_simulation():
    """Simuliert das Frontend-Verhalten"""
    
    project_id = 1  # BESS Hinterstoder
    
    try:
        print("🧪 Simuliere Frontend-Verhalten...")
        
        # 1. Projekt laden (wie das Frontend es macht)
        print("1. Lade Projekt (Frontend-Simulation)...")
        response = requests.get(f'http://127.0.0.1:5000/api/projects/{project_id}')
        
        if response.status_code == 200:
            project = response.json()
            print(f"✅ Projekt geladen: {project['name']}")
            print(f"   API Response daily_cycles: {project.get('daily_cycles')}")
            print(f"   API Response Typ: {type(project.get('daily_cycles'))}")
            
            # 2. Simuliere Formular-Daten (wie das Frontend sie sendet)
            print("2. Simuliere Formular-Submit...")
            
            # Simuliere die Daten, die das Frontend sendet
            form_data = {
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
                "daily_cycles": 2.0,  # Hier setzen wir 2.0
                "current_electricity_cost": 12.5,
                "bess_cost": 1680000,
                "pv_cost": 1650000,
                "hp_cost": None,
                "wind_cost": None,
                "hydro_cost": 2300000,
                "other_cost": 500000
            }
            
            print(f"   Sende daily_cycles: {form_data['daily_cycles']}")
            
            response = requests.put(
                f'http://127.0.0.1:5000/api/projects/{project_id}',
                json=form_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Projekt aktualisiert")
                
                # 3. Sofort wieder laden (wie nach dem Speichern)
                print("3. Lade Projekt nach Update (Frontend-Simulation)...")
                response = requests.get(f'http://127.0.0.1:5000/api/projects/{project_id}')
                
                if response.status_code == 200:
                    project = response.json()
                    daily_cycles = project.get('daily_cycles')
                    print(f"✅ Projekt nach Update geladen")
                    print(f"   daily_cycles: {daily_cycles}")
                    print(f"   Typ: {type(daily_cycles)}")
                    
                    if daily_cycles == 2.0:
                        print("✅ daily_cycles korrekt auf 2.0 gesetzt!")
                    else:
                        print(f"❌ daily_cycles falsch: erwartet 2.0, erhalten {daily_cycles}")
                        
                        # 4. Vollständige API-Response analysieren
                        print("4. Vollständige API-Response:")
                        for key, value in project.items():
                            if key == 'daily_cycles':
                                print(f"   {key}: {value} (TYP: {type(value)})")
                            elif key in ['bess_size', 'bess_power', 'pv_power', 'current_electricity_cost']:
                                print(f"   {key}: {value}")
                else:
                    print(f"❌ Fehler beim Laden nach Update: {response.status_code}")
            else:
                print(f"❌ Fehler beim Aktualisieren: {response.status_code}")
                print(f"   Antwort: {response.text}")
        else:
            print(f"❌ Fehler beim Laden: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Fehler beim Testen: {e}")

if __name__ == "__main__":
    test_frontend_simulation()
