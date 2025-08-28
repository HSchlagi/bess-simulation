#!/usr/bin/env python3
"""
Test-Script für Auto-Save System
"""

import requests
import json

def test_auto_save():
    """Testet das Auto-Save System"""
    
    # Test-Daten
    test_data = {
        "name": "Test Projekt",
        "bess_size": 100,
        "bess_power": 50,
        "pv_power": 75,
        "current_electricity_cost": 12.5
    }
    
    try:
        # Auto-Save Test
        print("🧪 Teste Auto-Save System...")
        
        response = requests.post(
            'http://127.0.0.1:5000/api/projects/auto-save',
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Auto-Save erfolgreich!")
            print(f"   Antwort: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ Auto-Save fehlgeschlagen: {response.status_code}")
            print(f"   Antwort: {response.text}")
            
    except Exception as e:
        print(f"❌ Fehler beim Testen: {e}")

def test_auto_save_restore():
    """Testet die Auto-Save Wiederherstellung"""
    
    try:
        print("\n🧪 Teste Auto-Save Wiederherstellung...")
        
        response = requests.get('http://127.0.0.1:5000/api/projects/auto-save/restore')
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Auto-Save Wiederherstellung erfolgreich!")
            print(f"   Antwort: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ Auto-Save Wiederherstellung fehlgeschlagen: {response.status_code}")
            print(f"   Antwort: {response.text}")
            
    except Exception as e:
        print(f"❌ Fehler beim Testen: {e}")

if __name__ == "__main__":
    test_auto_save()
    test_auto_save_restore()
