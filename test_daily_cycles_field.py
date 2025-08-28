#!/usr/bin/env python3
"""
Test-Script für das daily_cycles Feld
"""

import requests
import json

def test_daily_cycles_field():
    """Testet das daily_cycles Feld"""
    
    base_url = "http://127.0.0.1:5000"
    
    print("🔍 Teste daily_cycles Feld...")
    
    # 1. Lade Projekt-Daten
    print("\n1️⃣ Lade Projekt-Daten...")
    response = requests.get(f"{base_url}/api/projects/1")
    
    if response.status_code == 200:
        project = response.json()
        print(f"✅ Projekt geladen: {project['name']}")
        print(f"   daily_cycles in API: {project.get('daily_cycles')}")
        print(f"   daily_cycles Typ: {type(project.get('daily_cycles'))}")
    else:
        print(f"❌ Fehler beim Laden: {response.status_code}")
        return
    
    # 2. Teste Update auf 2.5
    print("\n2️⃣ Teste Update auf 2.5...")
    update_data = {
        'name': project['name'],
        'location': project.get('location', ''),
        'customer_id': project.get('customer_id'),
        'date': project.get('date'),
        'bess_size': project.get('bess_size'),
        'bess_power': project.get('bess_power'),
        'pv_power': project.get('pv_power'),
        'hp_power': project.get('hp_power'),
        'wind_power': project.get('wind_power'),
        'hydro_power': project.get('hydro_power'),
        'other_power': project.get('other_power'),
        'current_electricity_cost': project.get('current_electricity_cost'),
        'daily_cycles': 2.5,  # Neuer Wert
        'bess_cost': project.get('bess_cost'),
        'pv_cost': project.get('pv_cost'),
        'hp_cost': project.get('hp_cost'),
        'wind_cost': project.get('wind_cost'),
        'hydro_cost': project.get('hydro_cost'),
        'other_cost': project.get('other_cost')
    }
    
    response = requests.put(f"{base_url}/api/projects/1", 
                          headers={'Content-Type': 'application/json'},
                          data=json.dumps(update_data))
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ Update erfolgreich")
        else:
            print(f"❌ Update fehlgeschlagen: {result.get('error')}")
    else:
        print(f"❌ HTTP Fehler: {response.status_code}")
    
    # 3. Lade Projekt erneut
    print("\n3️⃣ Lade Projekt erneut...")
    response = requests.get(f"{base_url}/api/projects/1")
    
    if response.status_code == 200:
        project = response.json()
        print(f"✅ Projekt neu geladen")
        print(f"   daily_cycles nach Update: {project.get('daily_cycles')}")
        print(f"   daily_cycles Typ: {type(project.get('daily_cycles'))}")
    else:
        print(f"❌ Fehler beim Neuladen: {response.status_code}")
    
    # 4. Teste Update zurück auf 2.0
    print("\n4️⃣ Teste Update zurück auf 2.0...")
    update_data['daily_cycles'] = 2.0
    
    response = requests.put(f"{base_url}/api/projects/1", 
                          headers={'Content-Type': 'application/json'},
                          data=json.dumps(update_data))
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ Update zurück erfolgreich")
        else:
            print(f"❌ Update zurück fehlgeschlagen: {result.get('error')}")
    else:
        print(f"❌ HTTP Fehler: {response.status_code}")
    
    # 5. Finale Prüfung
    print("\n5️⃣ Finale Prüfung...")
    response = requests.get(f"{base_url}/api/projects/1")
    
    if response.status_code == 200:
        project = response.json()
        print(f"✅ Finale Prüfung")
        print(f"   daily_cycles final: {project.get('daily_cycles')}")
        print(f"   daily_cycles Typ: {type(project.get('daily_cycles'))}")
        
        if project.get('daily_cycles') == 2.0:
            print("🎉 SUCCESS: daily_cycles funktioniert korrekt!")
        else:
            print("❌ PROBLEM: daily_cycles funktioniert nicht korrekt!")
    else:
        print(f"❌ Fehler bei finaler Prüfung: {response.status_code}")

if __name__ == "__main__":
    test_daily_cycles_field()
