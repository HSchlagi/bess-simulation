#!/usr/bin/env python3
"""
Demo-Excel-Datei für Lastprofile erstellen
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def create_demo_load_profile_excel():
    """Erstellt eine Demo-Excel-Datei mit Lastprofil-Daten"""
    
    # Zeitraum: 1 Woche, stündliche Daten
    start_date = datetime(2024, 1, 1, 0, 0)
    end_date = start_date + timedelta(days=7)
    
    # Zeitstempel generieren
    timestamps = []
    current = start_date
    while current < end_date:
        timestamps.append(current)
        current += timedelta(hours=1)
    
    # Realistische Lastwerte generieren (kW)
    base_load = 500  # Basislast
    peak_load = 1200  # Spitzenlast
    
    load_values = []
    for i, timestamp in enumerate(timestamps):
        # Tageszeit-Effekt
        hour = timestamp.hour
        if 6 <= hour <= 9:  # Morgenpeak
            time_factor = 1.8
        elif 18 <= hour <= 21:  # Abendpeak
            time_factor = 2.0
        elif 23 <= hour or hour <= 5:  # Nachttal
            time_factor = 0.6
        else:  # Normal
            time_factor = 1.2
        
        # Wochentag-Effekt
        weekday = timestamp.weekday()
        if weekday >= 5:  # Wochenende
            time_factor *= 0.7
        
        # Zufällige Variation (±20%)
        random_factor = random.uniform(0.8, 1.2)
        
        # Finaler Lastwert
        load = base_load + (peak_load - base_load) * time_factor * random_factor
        load_values.append(round(load, 2))
    
    # DataFrame erstellen
    df = pd.DataFrame({
        'Datum': [ts.strftime('%d.%m.%Y') for ts in timestamps],
        'Zeit': [ts.strftime('%H:%M') for ts in timestamps],
        'Last_kW': load_values,
        'Energie_kWh': [round(load * 1, 2) for load in load_values]  # 1 Stunde
    })
    
    # Excel-Datei speichern
    filename = 'demo_load_profile.xlsx'
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Lastprofil', index=False)
        
        # Zusätzliches Sheet mit alternativem Format
        df_alt = pd.DataFrame({
            'Timestamp': timestamps,
            'Power_kW': load_values,
            'Energy_kWh': [round(load * 1, 2) for load in load_values]
        })
        df_alt.to_excel(writer, sheet_name='Alternative', index=False)
        
        # Multi-Station Sheet (wie in deinem Screenshot)
        df_multi = pd.DataFrame({
            'Hössbahn Berg Datum': [ts.strftime('%d.%m.%Y') for ts in timestamps],
            'Hössbahn Berg Zeit': [ts.strftime('%H:%M') for ts in timestamps],
            'Hössbahn Berg kW': [round(load * 0.4, 2) for load in load_values],
            'Hössbahn Berg kWh': [round(load * 0.4, 2) for load in load_values],
            'Pumpstation 1 Datum': [ts.strftime('%d.%m.%Y') for ts in timestamps],
            'Pumpstation 1 Zeit': [ts.strftime('%H:%M') for ts in timestamps],
            'Pumpstation 1 kW': [round(load * 0.3, 2) for load in load_values],
            'Pumpstation 1 kWh': [round(load * 0.3, 2) for load in load_values],
            'Pumpstation 2 Datum': [ts.strftime('%d.%m.%Y') for ts in timestamps],
            'Pumpstation 2 Zeit': [ts.strftime('%H:%M') for ts in timestamps],
            'Pumpstation 2 kW': [round(load * 0.3, 2) for load in load_values],
            'Pumpstation 2 kWh': [round(load * 0.3, 2) for load in load_values]
        })
        df_multi.to_excel(writer, sheet_name='Multi-Station', index=False)
    
    print(f"✅ Demo-Excel-Datei erstellt: {filename}")
    print(f"📊 Datenpunkte: {len(timestamps)}")
    print(f"📅 Zeitraum: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}")
    print(f"⚡ Lastbereich: {min(load_values):.2f} - {max(load_values):.2f} kW")
    print(f"📋 Sheets: Lastprofil, Alternative, Multi-Station")
    
    return filename

def create_simple_load_profile_excel():
    """Erstellt eine einfache Demo-Excel-Datei"""
    
    # Einfache Daten
    data = {
        'Datum': ['01.01.2024', '01.01.2024', '01.01.2024', '01.01.2024'],
        'Zeit': ['00:00', '01:00', '02:00', '03:00'],
        'Leistung_kW': [500.5, 480.2, 520.8, 495.3],
        'Energie_kWh': [500.5, 480.2, 520.8, 495.3]
    }
    
    df = pd.DataFrame(data)
    
    filename = 'simple_load_profile.xlsx'
    df.to_excel(filename, index=False)
    
    print(f"✅ Einfache Demo-Excel-Datei erstellt: {filename}")
    print(f"📊 Datenpunkte: {len(data['Datum'])}")
    
    return filename

if __name__ == "__main__":
    print("🎯 Demo-Excel-Dateien für Lastprofile erstellen...")
    print("=" * 50)
    
    # Beide Dateien erstellen
    create_demo_load_profile_excel()
    print()
    create_simple_load_profile_excel()
    
    print("\n🎉 Demo-Dateien erstellt!")
    print("📁 Verwende diese Dateien zum Testen des Excel-Imports") 