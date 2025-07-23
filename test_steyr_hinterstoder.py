#!/usr/bin/env python3
"""
Test-Skript für Steyr in Hinterstoder
"""

from ehyd_data_fetcher import EHYDDataFetcher

def test_steyr_hinterstoder():
    """Testet die Steyr-Messstationen in Hinterstoder"""
    
    print("🏔️ Teste Steyr in Hinterstoder...")
    print("=" * 60)
    
    fetcher = EHYDDataFetcher()
    
    # Test 1: Steyr Fluss
    print("🌊 Test 1: Steyr Fluss")
    try:
        stations = fetcher.get_stations_by_river('steyr')
        print(f"✅ {len(stations)} Steyr-Messstationen:")
        for station in stations:
            print(f"  - {station['name']} (ID: {station['id']})")
            
        # Suche nach Hinterstoder
        hinterstoder_stations = [s for s in stations if 'Hinterstoder' in s['name']]
        if hinterstoder_stations:
            print(f"\n🎯 Hinterstoder-Messstationen gefunden:")
            for station in hinterstoder_stations:
                print(f"  ✅ {station['name']} (ID: {station['id']})")
        else:
            print("❌ Keine Hinterstoder-Messstationen gefunden")
            
    except Exception as e:
        print(f"❌ Fehler: {e}")
    
    print("\n" + "=" * 60)
    
    # Test 2: Steyrbach
    print("🏔️ Test 2: Steyrbach")
    try:
        stations = fetcher.get_stations_by_river('steyrbach')
        print(f"✅ {len(stations)} Steyrbach-Messstationen:")
        for station in stations:
            print(f"  - {station['name']} (ID: {station['id']})")
            
        # Suche nach Hinterstoder
        hinterstoder_stations = [s for s in stations if 'Hinterstoder' in s['name']]
        if hinterstoder_stations:
            print(f"\n🎯 Hinterstoder-Messstationen gefunden:")
            for station in hinterstoder_stations:
                print(f"  ✅ {station['name']} (ID: {station['id']})")
        else:
            print("❌ Keine Hinterstoder-Messstationen gefunden")
            
    except Exception as e:
        print(f"❌ Fehler: {e}")
    
    print("\n" + "=" * 60)
    
    # Test 3: Pießling
    print("🏔️ Test 3: Pießling")
    try:
        stations = fetcher.get_stations_by_river('pießling')
        print(f"✅ {len(stations)} Pießling-Messstationen:")
        for station in stations:
            print(f"  - {station['name']} (ID: {station['id']})")
            
        # Suche nach Hinterstoder
        hinterstoder_stations = [s for s in stations if 'Hinterstoder' in s['name']]
        if hinterstoder_stations:
            print(f"\n🎯 Hinterstoder-Messstationen gefunden:")
            for station in hinterstoder_stations:
                print(f"  ✅ {station['name']} (ID: {station['id']})")
        else:
            print("❌ Keine Hinterstoder-Messstationen gefunden")
            
    except Exception as e:
        print(f"❌ Fehler: {e}")
    
    print("\n" + "=" * 60)
    
    # Test 4: Demo-Daten für Steyr Hinterstoder
    print("📊 Test 4: Demo-Daten für Steyr Hinterstoder")
    try:
        demo_data = fetcher.get_demo_data('steyr', 7)
        print(f"✅ Demo-Daten für Steyr generiert:")
        print(f"  📊 Fluss: {demo_data['river_name']}")
        print(f"  📈 Datenpunkte: {demo_data['total_data_points']}")
        print(f"  📍 Stationen: {demo_data['stations_count']}")
        print(f"  📅 Zeitraum: {demo_data['start_date']} bis {demo_data['end_date']}")
        
        # Zeige Hinterstoder-Daten
        hinterstoder_data = [d for d in demo_data['water_levels'] if 'Hinterstoder' in d['station_name']]
        if hinterstoder_data:
            print(f"\n🎯 Hinterstoder-Datenpunkte: {len(hinterstoder_data)}")
            print("📈 Erste 5 Hinterstoder-Datenpunkte:")
            for i, data in enumerate(hinterstoder_data[:5]):
                print(f"  {i+1}. {data['timestamp']} - {data['station_name']}: {data['water_level_cm']} cm")
        else:
            print("❌ Keine Hinterstoder-Daten gefunden")
            
    except Exception as e:
        print(f"❌ Fehler: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Steyr Hinterstoder Test abgeschlossen!")

if __name__ == "__main__":
    test_steyr_hinterstoder() 