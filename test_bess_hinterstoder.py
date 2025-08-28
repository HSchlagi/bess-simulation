#!/usr/bin/env python3
"""
Test-Script für BESS Hinterstoder daily_cycles Problem
"""

import requests
import json

def test_bess_hinterstoder():
    """Testet das daily_cycles Feld für BESS Hinterstoder"""
    
    project_id = 1  # BESS Hinterstoder
    
    try:
        print("🧪 Teste BESS Hinterstoder daily_cycles...")
        
        # 1. Aktuelles Projekt laden
        print("1. Lade aktuelles Projekt...")
        response = requests.get(f'http://127.0.0.1:5000/api/projects/{project_id}')
        
        if response.status_code == 200:
            project = response.json()
            print(f"✅ Projekt geladen: {project['name']}")
            print(f"   Aktuelle daily_cycles: {project.get('daily_cycles')}")
            print(f"   BESS Size: {project.get('bess_size')}")
            print(f"   BESS Power: {project.get('bess_power')}")
            
            # 2. Projekt mit daily_cycles = 2.0 aktualisieren
            print("2. Aktualisiere daily_cycles auf 2.0...")
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
                "daily_cycles": 2.0,
                "current_electricity_cost": 12.5,
                "bess_cost": 1680000,
                "pv_cost": 1650000,
                "hp_cost": None,
                "wind_cost": None,
                "hydro_cost": 2300000,
                "other_cost": 500000
            }
            
            response = requests.put(
                f'http://127.0.0.1:5000/api/projects/{project_id}',
                json=update_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Projekt aktualisiert")
                print(f"   Antwort: {result}")
                
                # 3. Projekt erneut laden und prüfen
                print("3. Prüfe aktualisierte daily_cycles...")
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
                        
                        # 4. Datenbank direkt prüfen
                        print("4. Prüfe alle Projektfelder...")
                        for key, value in project.items():
                            if key == 'daily_cycles':
                                print(f"   {key}: {value} (TYP: {type(value)})")
                            elif key in ['bess_size', 'bess_power', 'pv_power', 'current_electricity_cost']:
                                print(f"   {key}: {value}")
                else:
                    print(f"❌ Fehler beim Laden des aktualisierten Projekts: {response.status_code}")
            else:
                print(f"❌ Fehler beim Aktualisieren: {response.status_code}")
                print(f"   Antwort: {response.text}")
        else:
            print(f"❌ Fehler beim Laden des Projekts: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Fehler beim Testen: {e}")

if __name__ == "__main__":
    test_bess_hinterstoder()
