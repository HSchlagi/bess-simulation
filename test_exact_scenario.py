#!/usr/bin/env python3
"""
Test-Script für das genaue Szenario
"""

import requests
import json
import time

def test_exact_scenario():
    """Testet das genaue Szenario: 2 setzen, speichern, neu laden"""
    
    project_id = 1  # BESS Hinterstoder
    
    try:
        print("🧪 Teste genaues Szenario...")
        
        # 1. Aktuellen Zustand laden
        print("1. Lade aktuellen Zustand...")
        response = requests.get(f'http://127.0.0.1:5000/api/projects/{project_id}')
        
        if response.status_code == 200:
            project = response.json()
            print(f"✅ Aktueller Zustand geladen")
            print(f"   daily_cycles vor Test: {project.get('daily_cycles')}")
            
            # 2. Setze daily_cycles auf 2.0 (wie im Frontend)
            print("2. Setze daily_cycles auf 2.0...")
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
                "daily_cycles": 2.0,  # Hier setzen wir 2.0
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
                print("✅ Projekt mit daily_cycles=2.0 gespeichert")
                
                # 3. Sofort prüfen (wie direkt nach dem Speichern)
                print("3. Prüfe sofort nach Speichern...")
                response = requests.get(f'http://127.0.0.1:5000/api/projects/{project_id}')
                
                if response.status_code == 200:
                    project = response.json()
                    daily_cycles = project.get('daily_cycles')
                    print(f"   daily_cycles direkt nach Speichern: {daily_cycles}")
                    
                    if daily_cycles == 2.0:
                        print("✅ daily_cycles korrekt auf 2.0 gesetzt!")
                    else:
                        print(f"❌ daily_cycles falsch: erwartet 2.0, erhalten {daily_cycles}")
                
                # 4. Kurz warten und dann prüfen (wie nach dem Navigieren)
                print("4. Warte kurz und prüfe erneut...")
                time.sleep(1)
                
                response = requests.get(f'http://127.0.0.1:5000/api/projects/{project_id}')
                
                if response.status_code == 200:
                    project = response.json()
                    daily_cycles = project.get('daily_cycles')
                    print(f"   daily_cycles nach Wartezeit: {daily_cycles}")
                    
                    if daily_cycles == 2.0:
                        print("✅ daily_cycles bleibt korrekt auf 2.0!")
                    else:
                        print(f"❌ daily_cycles hat sich geändert: erwartet 2.0, erhalten {daily_cycles}")
                        
                        # 5. Vollständige Analyse
                        print("5. Vollständige Projekt-Analyse:")
                        print(f"   Name: {project.get('name')}")
                        print(f"   BESS Size: {project.get('bess_size')}")
                        print(f"   BESS Power: {project.get('bess_power')}")
                        print(f"   PV Power: {project.get('pv_power')}")
                        print(f"   Daily Cycles: {project.get('daily_cycles')} (TYP: {type(project.get('daily_cycles'))})")
                        print(f"   Current Electricity Cost: {project.get('current_electricity_cost')}")
                
                # 6. Setze auf 1.5 (wie im Frontend)
                print("6. Setze daily_cycles auf 1.5...")
                update_data['daily_cycles'] = 1.5
                
                response = requests.put(
                    f'http://127.0.0.1:5000/api/projects/{project_id}',
                    json=update_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    print("✅ Projekt mit daily_cycles=1.5 gespeichert")
                    
                    # 7. Prüfe nach dem Setzen auf 1.5
                    response = requests.get(f'http://127.0.0.1:5000/api/projects/{project_id}')
                    
                    if response.status_code == 200:
                        project = response.json()
                        daily_cycles = project.get('daily_cycles')
                        print(f"   daily_cycles nach Setzen auf 1.5: {daily_cycles}")
                        
                        if daily_cycles == 1.5:
                            print("✅ daily_cycles korrekt auf 1.5 gesetzt!")
                        else:
                            print(f"❌ daily_cycles falsch: erwartet 1.5, erhalten {daily_cycles}")
            else:
                print(f"❌ Fehler beim Speichern: {response.status_code}")
                print(f"   Antwort: {response.text}")
        else:
            print(f"❌ Fehler beim Laden: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Fehler beim Testen: {e}")

if __name__ == "__main__":
    test_exact_scenario()
