#!/usr/bin/env python3
"""
Test-Script für daily_cycles Feld
"""

import requests
import json

def test_daily_cycles():
    """Testet das daily_cycles Feld"""
    
    # Test-Daten mit daily_cycles = 2
    test_data = {
        "name": "Test Projekt Daily Cycles",
        "bess_size": 100,
        "bess_power": 50,
        "pv_power": 75,
        "current_electricity_cost": 12.5,
        "daily_cycles": 2.0
    }
    
    try:
        print("🧪 Teste daily_cycles Feld...")
        
        # 1. Projekt erstellen
        print("1. Erstelle neues Projekt...")
        response = requests.post(
            'http://127.0.0.1:5000/api/projects',
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 201:
            result = response.json()
            project_id = result['id']
            print(f"✅ Projekt erstellt mit ID: {project_id}")
            
            # 2. Projekt laden und prüfen
            print("2. Lade Projekt und prüfe daily_cycles...")
            response = requests.get(f'http://127.0.0.1:5000/api/projects/{project_id}')
            
            if response.status_code == 200:
                project = response.json()
                daily_cycles = project.get('daily_cycles')
                print(f"✅ Projekt geladen, daily_cycles: {daily_cycles}")
                
                if daily_cycles == 2.0:
                    print("✅ daily_cycles korrekt gespeichert und geladen!")
                else:
                    print(f"❌ daily_cycles falsch: erwartet 2.0, erhalten {daily_cycles}")
                
                # 3. Projekt aktualisieren
                print("3. Aktualisiere daily_cycles auf 1.5...")
                update_data = {
                    "name": "Test Projekt Daily Cycles",
                    "bess_size": 100,
                    "bess_power": 50,
                    "pv_power": 75,
                    "current_electricity_cost": 12.5,
                    "daily_cycles": 1.5
                }
                
                response = requests.put(
                    f'http://127.0.0.1:5000/api/projects/{project_id}',
                    json=update_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    print("✅ Projekt aktualisiert")
                    
                    # 4. Projekt erneut laden und prüfen
                    print("4. Prüfe aktualisierte daily_cycles...")
                    response = requests.get(f'http://127.0.0.1:5000/api/projects/{project_id}')
                    
                    if response.status_code == 200:
                        project = response.json()
                        daily_cycles = project.get('daily_cycles')
                        print(f"✅ Projekt nach Update geladen, daily_cycles: {daily_cycles}")
                        
                        if daily_cycles == 1.5:
                            print("✅ daily_cycles Update erfolgreich!")
                        else:
                            print(f"❌ daily_cycles Update fehlgeschlagen: erwartet 1.5, erhalten {daily_cycles}")
                    else:
                        print(f"❌ Fehler beim Laden des aktualisierten Projekts: {response.status_code}")
                else:
                    print(f"❌ Fehler beim Aktualisieren: {response.status_code}")
                    print(f"   Antwort: {response.text}")
            else:
                print(f"❌ Fehler beim Laden des Projekts: {response.status_code}")
        else:
            print(f"❌ Fehler beim Erstellen: {response.status_code}")
            print(f"   Antwort: {response.text}")
            
    except Exception as e:
        print(f"❌ Fehler beim Testen: {e}")

if __name__ == "__main__":
    test_daily_cycles()
