#!/usr/bin/env python3
"""
Test-Skript für Projektdaten
Überprüft, ob alle Projektfelder korrekt geladen werden
"""

import requests
import json

def test_project_data():
    """Testet die Projektdaten-API"""
    
    base_url = "http://127.0.0.1:5000"
    
    print("🔍 Teste Projektdaten-API...")
    print("=" * 60)
    
    try:
        # Alle Projekte abrufen
        response = requests.get(f"{base_url}/api/projects")
        if response.status_code == 200:
            projects = response.json()
            print(f"✅ {len(projects)} Projekte gefunden")
            
            for project in projects:
                print(f"\n📋 Projekt: {project['name']} (ID: {project['id']})")
                print(f"   - Standort: {project.get('location', 'Nicht angegeben')}")
                print(f"   - Kunde: {project.get('customer', {}).get('name', 'Kein Kunde')}")
                print(f"   - BESS Size: {project.get('bess_size', 'Nicht gesetzt')} kWh")
                print(f"   - BESS Power: {project.get('bess_power', 'Nicht gesetzt')} kW")
                print(f"   - PV Power: {project.get('pv_power', 'Nicht gesetzt')} kW")
                print(f"   - Current Electricity Cost: {project.get('current_electricity_cost', 'Nicht gesetzt')} Ct/kWh")
                print(f"   - BESS Cost: {project.get('bess_cost', 'Nicht gesetzt')} €")
                print(f"   - PV Cost: {project.get('pv_cost', 'Nicht gesetzt')} €")
                
                # Einzelnes Projekt testen
                project_response = requests.get(f"{base_url}/api/projects/{project['id']}")
                if project_response.status_code == 200:
                    project_detail = project_response.json()
                    print(f"   ✅ Einzelnes Projekt korrekt geladen")
                    print(f"   - Current Electricity Cost (Detail): {project_detail.get('current_electricity_cost', 'Nicht gesetzt')}")
                else:
                    print(f"   ❌ Fehler beim Laden des einzelnen Projekts: {project_response.status_code}")
        
        else:
            print(f"❌ Fehler beim Abrufen der Projekte: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Server nicht erreichbar. Bitte starten Sie den Server mit 'python run.py'")
    except Exception as e:
        print(f"❌ Fehler: {e}")

if __name__ == "__main__":
    test_project_data()
