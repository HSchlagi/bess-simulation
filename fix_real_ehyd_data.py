#!/usr/bin/env python3
"""
Versucht echte EHYD-Daten zu laden statt Demo-Daten
"""

import requests
import json
from datetime import datetime, timedelta
from ehyd_data_fetcher import EHYDDataFetcher

def test_real_ehyd_data():
    """Testet das Laden echter EHYD-Daten"""
    
    print("🔧 Teste echte EHYD-Daten...")
    print("=" * 60)
    
    fetcher = EHYDDataFetcher()
    
    # Test 1: Versuche echte EHYD-Daten für Steyr 2024
    print("📅 Test 1: Echte EHYD-Daten für Steyr 2024")
    try:
        # Direkter API-Aufruf an EHYD
        url = "https://ehyd.gv.at/eHYD/MessstellenExtraData/EXTRADATA"
        params = {
            'stammdatenId': '208010',  # Hinterstoder
            'startDate': '2024-01-01',
            'endDate': '2024-01-31'
        }
        
        print(f"🌐 API-Aufruf: {url}")
        print(f"📋 Parameter: {params}")
        
        response = requests.get(url, params=params, timeout=30)
        print(f"📡 Response Status: {response.status_code}")
        print(f"📡 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Echte EHYD-Daten erfolgreich geladen!")
            data = response.json()
            print(f"📊 Datenpunkte: {len(data) if isinstance(data, list) else 'N/A'}")
            
            # Speichere echte Daten
            with open('real_ehyd_data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print("💾 Echte Daten in real_ehyd_data.json gespeichert")
            
        else:
            print(f"❌ API-Fehler: {response.status_code}")
            print(f"📄 Response Text: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Fehler beim API-Aufruf: {e}")
    
    print("\n" + "=" * 60)
    
    # Test 2: Teste verschiedene Stationen
    print("📅 Test 2: Verschiedene Stationen testen")
    stations_to_test = [
        {'id': '208010', 'name': 'Hinterstoder'},
        {'id': '208015', 'name': 'Steyr'},
        {'id': '208020', 'name': 'Garsten'}
    ]
    
    for station in stations_to_test:
        try:
            print(f"\n🌊 Teste Station: {station['name']} (ID: {station['id']})")
            
            url = "https://ehyd.gv.at/eHYD/MessstellenExtraData/EXTRADATA"
            params = {
                'stammdatenId': station['id'],
                'startDate': '2024-01-01',
                'endDate': '2024-01-07'
            }
            
            response = requests.get(url, params=params, timeout=10)
            print(f"📡 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    print(f"✅ {len(data)} echte Datenpunkte gefunden!")
                    
                    # Zeige erste Datenpunkte
                    for i, point in enumerate(data[:3]):
                        print(f"  📊 Punkt {i+1}: {point}")
                else:
                    print("⚠️ Keine Daten in der Antwort")
            else:
                print(f"❌ Fehler: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Fehler: {e}")
    
    print("\n" + "=" * 60)
    
    # Test 3: Teste verschiedene Zeiträume
    print("📅 Test 3: Verschiedene Zeiträume testen")
    time_ranges = [
        {'start': '2024-01-01', 'end': '2024-01-31', 'name': 'Januar 2024'},
        {'start': '2023-12-01', 'end': '2023-12-31', 'name': 'Dezember 2023'},
        {'start': '2023-06-01', 'end': '2023-06-30', 'name': 'Juni 2023'}
    ]
    
    for time_range in time_ranges:
        try:
            print(f"\n📅 Teste Zeitraum: {time_range['name']}")
            
            url = "https://ehyd.gv.at/eHYD/MessstellenExtraData/EXTRADATA"
            params = {
                'stammdatenId': '208010',  # Hinterstoder
                'startDate': time_range['start'],
                'endDate': time_range['end']
            }
            
            response = requests.get(url, params=params, timeout=10)
            print(f"📡 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    print(f"✅ {len(data)} echte Datenpunkte für {time_range['name']}")
                else:
                    print("⚠️ Keine Daten für diesen Zeitraum")
            else:
                print(f"❌ Fehler: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Fehler: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Echte EHYD-Daten Test abgeschlossen!")

if __name__ == "__main__":
    test_real_ehyd_data() 