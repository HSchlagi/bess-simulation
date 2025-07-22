#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_data_overview_api():
    """Testet die Datenübersicht-API"""
    
    base_url = "http://localhost:5000"
    
    print("🧪 Teste Datenübersicht-API...")
    
    # Test 1: Datenübersicht für Projekt 1
    try:
        response = requests.get(f"{base_url}/api/projects/1/data-overview")
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Antwort: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ Fehler: {response.text}")
            
    except Exception as e:
        print(f"❌ Fehler beim API-Test: {e}")
    
    # Test 2: Projekte-API
    try:
        response = requests.get(f"{base_url}/api/projects")
        print(f"\n📡 Projekte API Status: {response.status_code}")
        
        if response.status_code == 200:
            projects = response.json()
            print(f"✅ Projekte: {json.dumps(projects, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ Fehler: {response.text}")
            
    except Exception as e:
        print(f"❌ Fehler beim Projekte-Test: {e}")

if __name__ == "__main__":
    test_data_overview_api() 