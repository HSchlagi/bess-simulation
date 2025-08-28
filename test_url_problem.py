#!/usr/bin/env python3
"""
Test-Script für das URL-Problem
"""

import requests
import json

def test_url_problem():
    """Testet das URL-Problem mit id=null"""
    
    try:
        print("🧪 Teste URL-Problem...")
        
        # 1. Teste URL mit id=null
        print("1. Teste URL mit id=null...")
        response = requests.get('http://127.0.0.1:5000/edit_project?id=null')
        
        if response.status_code == 200:
            print("✅ Seite geladen (sollte aber Fehler anzeigen)")
        else:
            print(f"❌ Seite nicht geladen: {response.status_code}")
        
        # 2. Teste API mit id=null
        print("2. Teste API mit id=null...")
        response = requests.get('http://127.0.0.1:5000/api/projects/null')
        
        if response.status_code == 404:
            print("✅ API gibt korrekt 404 zurück")
        else:
            print(f"❌ API gibt unerwarteten Status zurück: {response.status_code}")
        
        # 3. Teste URL mit gültiger ID
        print("3. Teste URL mit gültiger ID...")
        response = requests.get('http://127.0.0.1:5000/edit_project?id=1')
        
        if response.status_code == 200:
            print("✅ Seite mit gültiger ID geladen")
        else:
            print(f"❌ Seite mit gültiger ID nicht geladen: {response.status_code}")
        
        # 4. Teste URL mit Formulardaten
        print("4. Teste URL mit Formulardaten...")
        test_url = 'http://127.0.0.1:5000/edit_project?name=Test&bess_size=100&customer_id='
        response = requests.get(test_url)
        
        if response.status_code == 200:
            print("✅ Seite mit Formulardaten geladen")
        else:
            print(f"❌ Seite mit Formulardaten nicht geladen: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Fehler beim Testen: {e}")

if __name__ == "__main__":
    test_url_problem()
