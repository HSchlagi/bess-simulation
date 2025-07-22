#!/usr/bin/env python3
"""
Sehr einfache Test-Excel-Datei erstellen
"""

import pandas as pd
from datetime import datetime, timedelta

def create_simple_test_excel():
    """Erstellt eine sehr einfache Test-Excel-Datei"""
    
    # Einfache Daten
    data = {
        'Datum': ['01.01.2024 00:00', '01.01.2024 00:15', '01.01.2024 00:30', '01.01.2024 00:45'],
        'kW': [100.5, 120.3, 95.8, 110.2],
        'kWh': [25.1, 30.1, 23.9, 27.6]
    }
    
    df = pd.DataFrame(data)
    
    filename = 'simple_test.xlsx'
    df.to_excel(filename, index=False)
    
    print(f"✅ Einfache Test-Excel-Datei erstellt: {filename}")
    print(f"📊 Datenpunkte: {len(data['Datum'])}")
    print(f"📋 Spalten: {list(data.keys())}")
    
    return filename

def create_multi_station_test_excel():
    """Erstellt eine Multi-Station-Test-Excel-Datei"""
    
    # Multi-Station-Daten
    data = {
        'Datum': ['01.01.2024 00:00', '01.01.2024 00:15', '01.01.2024 00:30', '01.01.2024 00:45'],
        'Berg kW': [80.5, 90.3, 75.8, 85.2],
        'Pumpstation 2 kW': [20.0, 25.0, 18.0, 22.0],
        'Pumpstation 3 kW': [10.0, 12.0, 8.0, 11.0],
        'kW Gesamt': [110.5, 127.3, 101.8, 118.2]
    }
    
    df = pd.DataFrame(data)
    
    filename = 'multi_station_test.xlsx'
    df.to_excel(filename, index=False)
    
    print(f"✅ Multi-Station-Test-Excel-Datei erstellt: {filename}")
    print(f"📊 Datenpunkte: {len(data['Datum'])}")
    print(f"🏭 Stationen: Berg, Pumpstation 2, Pumpstation 3, Gesamt")
    
    return filename

if __name__ == "__main__":
    print("🎯 Test-Excel-Dateien erstellen...")
    print("=" * 40)
    
    create_simple_test_excel()
    print()
    create_multi_station_test_excel()
    
    print("\n🎉 Test-Dateien erstellt!")
    print("📁 Verwende diese Dateien zum Debugging") 