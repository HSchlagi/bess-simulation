#!/usr/bin/env python3
"""
Excel-Datei im exakten Format der Benutzer-Datei erstellen
"""

import pandas as pd
from datetime import datetime, timedelta

def create_exact_format_excel():
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
    
    # Realistische Lastwerte
    berg_loads = [80.5, 90.3, 75.8, 85.2] * 24  # 4 Werte pro Stunde, 24 Stunden
    pump2_loads = [20.0, 25.0, 18.0, 22.0] * 24
    pump3_loads = [10.0, 12.0, 8.0, 11.0] * 24
    pump9_loads = [30.0, 35.0, 28.0, 32.0] * 24
    
    # Energie-Werte (kWh = kW * 0.25h für 15-Minuten-Intervalle)
    berg_energy = [round(load * 0.25, 6) for load in berg_loads]
    pump2_energy = [round(load * 0.25, 6) for load in pump2_loads]
    pump3_energy = [round(load * 0.25, 6) for load in pump3_loads]
    pump9_energy = [round(load * 0.25, 6) for load in pump9_loads]
    
    # Gesamtwerte
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
    filename = 'exact_format_load_profile.xlsx'
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
    
    print(f"✅ Exact-Format-Excel-Datei erstellt: {filename}")
    print(f"📊 Datenpunkte: {len(timestamps)} (15-Minuten-Intervalle)")
    print(f"📅 Zeitraum: {start_date.strftime('%d.%m.%Y %H:%M')} - {end_date.strftime('%d.%m.%Y %H:%M')}")
    print(f"🏭 Stationen: Bergbahn, Pumpstation 2, 3, 9")
    print(f"⚡ Gesamtlast: {min(total_kw):.2f} - {max(total_kw):.2f} kW")
    print(f"📋 Sheets: Lastprofilimport, Bereinigt")
    
    return filename

if __name__ == "__main__":
    print("🎯 Exact-Format-Excel-Datei erstellen...")
    print("=" * 50)
    
    create_exact_format_excel()
    
    print("\n🎉 Exact-Format-Excel-Datei erstellt!")
    print("📁 Verwende diese Datei zum Testen") 