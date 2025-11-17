#!/usr/bin/env python3
"""
Testet die Wochentags-Analyse-Funktion direkt mit Datenbank-Daten
"""

import sqlite3
import pandas as pd
import sys
import os

# Pfad zum analysis-Modul
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))
from analysis.lastprofil_analysis import calc_weekday_analysis, load_profile_from_data

# Datenbank verbinden
conn = sqlite3.connect('instance/bess.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=" * 80)
print("TEST: Wochentags-Analyse mit Datenbank-Daten")
print("=" * 80)

# Projekt "BESS Hinterstoder" finden
cursor.execute("SELECT id, name FROM project WHERE name LIKE '%Hinterstoder%'")
project = cursor.fetchone()
project_id = project[0]
print(f"\nProjekt: ID={project_id}, Name={project[1]}")

# Zeitraum: 22.04.2024 00:01 - 28.04.2024 23:59
start_date = '2024-04-22 00:01:00'
end_date = '2024-04-29 00:00:00'  # Exklusiv

print(f"\nZeitraum: {start_date} bis {end_date} (exklusiv)")

# Daten laden
query = """
SELECT lv.timestamp, lv.power_kw as value 
FROM load_value lv
JOIN load_profile lp ON lv.load_profile_id = lp.id
WHERE lp.project_id = ? 
  AND lv.timestamp >= ? 
  AND lv.timestamp < ?
ORDER BY lv.timestamp
"""

cursor.execute(query, (project_id, start_date, end_date))
rows = cursor.fetchall()

print(f"\nGeladene Datenpunkte: {len(rows)}")

# Daten formatieren
load_data = []
for row in rows:
    load_data.append({
        'timestamp': row[0],
        'value': float(row[1]) if row[1] is not None else 0.0
    })

# DataFrame erstellen
df = load_profile_from_data(load_data)
print(f"\nDataFrame erstellt: {len(df)} Zeilen")
print(f"Zeitraum im DataFrame: {df.index.min()} bis {df.index.max()}")

# Wochentag extrahieren und prüfen
df['weekday'] = df.index.dayofweek
df['weekday_name'] = df.index.day_name()

print("\nWochentage im DataFrame:")
weekday_counts = df['weekday'].value_counts().sort_index()
for wd_num, count in weekday_counts.items():
    weekday_names = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']
    wd_name = weekday_names[wd_num]
    print(f"  {wd_name} (dayofweek={wd_num}): {count} Datenpunkte")

# Speziell Sonntag prüfen
sunday_data = df[df['weekday'] == 6]
print(f"\nSonntagsdaten (dayofweek=6): {len(sunday_data)} Datenpunkte")
if len(sunday_data) > 0:
    print(f"  Erste 5 Sonntagsdaten:")
    for idx, row in sunday_data.head().iterrows():
        print(f"    {idx} - {row['P']} kW")

# Analyse durchführen
print("\n" + "=" * 80)
print("Fuehre Wochentags-Analyse durch...")
print("=" * 80)

try:
    result = calc_weekday_analysis(df)
    
    print("\nErgebnisse der Analyse:")
    print(f"  Werktage Ø: {result['workday_avg_kW']:.2f} kW")
    print(f"  Wochenende Ø: {result['weekend_avg_kW']:.2f} kW")
    print(f"  Wochenende-Drop: {result['weekend_drop_percent']:.1f}%")
    
    print("\nDaten pro Wochentag:")
    for weekday_name in ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']:
        data = result['weekdays'][weekday_name]
        print(f"  {weekday_name}:")
        print(f"    Durchschnitt: {data['mean_kW']:.2f} kW")
        print(f"    Maximum: {data['max_kW']:.2f} kW")
        print(f"    Minimum: {data['min_kW']:.2f} kW")
        
except Exception as e:
    print(f"\n[FEHLER] Analyse fehlgeschlagen: {e}")
    import traceback
    traceback.print_exc()

conn.close()
print("\n" + "=" * 80)
print("Test abgeschlossen")
print("=" * 80)



