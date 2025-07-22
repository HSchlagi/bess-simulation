#!/usr/bin/env python3
"""
Realistische Lastprofil-Excel-Datei erstellen (exakt wie Benutzer-Format)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def create_realistic_load_profile():
    """Erstellt eine Excel-Datei im exakten Format der Benutzer-Datei"""
    
    # Zeitraum: 1 Tag, 15-Minuten-Intervalle
    start_date = datetime(2024, 1, 1, 0, 0)
    end_date = start_date + timedelta(days=1)
    
    # Zeitstempel generieren (15-Minuten-Intervalle)
    timestamps = []
    current = start_date
    while current < end_date:
        timestamps.append(current)
        current += timedelta(minutes=15)
    
    # Realistische Lastwerte für verschiedene Stationen
    def generate_station_load(base_load, peak_factor, variation=0.2):
        """Generiert realistische Lastwerte für eine Station"""
        loads = []
        for i, timestamp in enumerate(timestamps):
            hour = timestamp.hour
            
            # Tageszeit-Effekt
            if 6 <= hour <= 9:  # Morgenpeak
                time_factor = 1.5
            elif 18 <= hour <= 21:  # Abendpeak
                time_factor = 1.8
            elif 23 <= hour or hour <= 5:  # Nachttal
                time_factor = 0.6
            else:  # Normal
                time_factor = 1.2
            
            # Zufällige Variation
            random_factor = random.uniform(1 - variation, 1 + variation)
            
            # Finaler Lastwert
            load = base_load * time_factor * random_factor
            loads.append(round(load, 6))  # 6 Dezimalstellen wie im Original
        
        return loads
    
    # Lastwerte für verschiedene Stationen generieren
    berg_loads = generate_station_load(80, 1.5)  # Bergbahn
    pump2_loads = generate_station_load(15, 1.3)  # Pumpstation 2
    pump3_loads = generate_station_load(7, 1.2)   # Pumpstation 3
    pump9_loads = generate_station_load(30, 1.4)  # Pumpstation 9
    
    # Energie-Werte berechnen (kWh = kW * 0.25h für 15-Minuten-Intervalle)
    berg_energy = [round(load * 0.25, 6) for load in berg_loads]
    pump2_energy = [round(load * 0.25, 6) for load in pump2_loads]
    pump3_energy = [round(load * 0.25, 6) for load in pump3_loads]
    pump9_energy = [round(load * 0.25, 6) for load in pump9_loads]
    
    # Gesamtwerte berechnen
    total_kw = [round(berg + p2 + p3 + p9, 6) for berg, p2, p3, p9 in zip(berg_loads, pump2_loads, pump3_loads, pump9_loads)]
    total_kwh = [round(berg + p2 + p3 + p9, 6) for berg, p2, p3, p9 in zip(berg_energy, pump2_energy, pump3_energy, pump9_energy)]
    
    # DataFrame erstellen (exakt wie im Screenshot)
    df = pd.DataFrame({
        # Lastprofil Berg (A-E)
        'Datum': [ts.strftime('%d.%m.%Y %H:%M') for ts in timestamps],
        'kWh': berg_energy,
        'kW': berg_loads,
        'Status': ['VALID'] * len(timestamps),
        '': [''] * len(timestamps),  # Leere Spalte E
        
        # Pumpstation 2 (F-J)
        'Datum.1': [ts.strftime('%d.%m.%Y %H:%M') for ts in timestamps],
        'kWh.1': pump2_energy,
        'kW.1': pump2_loads,
        'Status.1': ['VALID'] * len(timestamps),
        '': [''] * len(timestamps),  # Leere Spalte J
        
        # Pumpstation 3 (K-O)
        'Datum.2': [ts.strftime('%d.%m.%Y %H:%M') for ts in timestamps],
        'kWh.2': pump3_energy,
        'kW.2': pump3_loads,
        'Status.2': ['VALID'] * len(timestamps),
        '': [''] * len(timestamps),  # Leere Spalte O
        
        # Pumpstation 9 (P-T)
        'Datum.3': [ts.strftime('%d.%m.%Y %H:%M') for ts in timestamps],
        'kWh.3': pump9_energy,
        'kW.3': pump9_loads,
        'Status.3': ['VALID'] * len(timestamps),
        '': [''] * len(timestamps),  # Leere Spalte T
        
        # Viertelstundenwerte (U-Y)
        'Datum.4': [ts.strftime('%d.%m.%Y %H:%M') for ts in timestamps],
        'kWh Gesamt': total_kwh,
        'kW Gesamt': total_kw,
        'Status.4': ['VALID'] * len(timestamps),
        '': [''] * len(timestamps),  # Leere Spalte Y
        
        # Tageswerte (Z-AA) - leer für jetzt
        'Datum.5': [''] * len(timestamps),
        'kWh Gesamt.1': [''] * len(timestamps)
    })
    
    # Excel-Datei speichern
    filename = 'realistic_load_profile.xlsx'
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Lastprofilimport', index=False)
        
        # Zusätzliches Sheet mit bereinigten Daten
        clean_df = pd.DataFrame({
            'Datum': [ts.strftime('%d.%m.%Y %H:%M') for ts in timestamps],
            'Lastprofil Berg kW': berg_loads,
            'Pumpstation 2 kW': pump2_loads,
            'Pumpstation 3 kW': pump3_loads,
            'Pumpstation 9 kW': pump9_loads,
            'Gesamt kW': total_kw,
            'Gesamt kWh': total_kwh
        })
        clean_df.to_excel(writer, sheet_name='Bereinigt', index=False)
    
    print(f"✅ Realistische Lastprofil-Excel-Datei erstellt: {filename}")
    print(f"📊 Datenpunkte: {len(timestamps)} (15-Minuten-Intervalle)")
    print(f"📅 Zeitraum: {start_date.strftime('%d.%m.%Y %H:%M')} - {end_date.strftime('%d.%m.%Y %H:%M')}")
    print(f"🏭 Stationen: Bergbahn, Pumpstation 2, 3, 9")
    print(f"⚡ Gesamtlast: {min(total_kw):.2f} - {max(total_kw):.2f} kW")
    print(f"📋 Sheets: Lastprofilimport, Bereinigt")
    
    return filename

if __name__ == "__main__":
    print("🎯 Realistische Lastprofil-Excel-Datei erstellen...")
    print("=" * 60)
    
    create_realistic_load_profile()
    
    print("\n🎉 Realistische Excel-Datei erstellt!")
    print("📁 Verwende diese Datei zum Testen des Multi-Station-Imports") 