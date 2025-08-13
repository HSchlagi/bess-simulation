#!/usr/bin/env python3
import sqlite3

# Datenbank verbinden
conn = sqlite3.connect('instance/bess.db')
cursor = conn.cursor()

# Teste 2024 Filter
cursor.execute("""
    SELECT COUNT(*) 
    FROM load_value lv 
    JOIN load_profile lp ON lv.load_profile_id = lp.id 
    WHERE lp.project_id = 1 
    AND lv.timestamp >= '2024-01-01' 
    AND lv.timestamp <= '2024-12-31'
""")
count_2024 = cursor.fetchone()[0]
print(f"Datenpunkte für 2024: {count_2024}")

# Teste Zeitraum
cursor.execute("""
    SELECT MIN(timestamp), MAX(timestamp) 
    FROM load_value lv 
    JOIN load_profile lp ON lv.load_profile_id = lp.id 
    WHERE lp.project_id = 1 
    AND lv.timestamp >= '2024-01-01' 
    AND lv.timestamp <= '2024-12-31'
""")
time_range = cursor.fetchone()
print(f"Zeitraum: {time_range[0]} bis {time_range[1]}")

# Teste alle Daten
cursor.execute("""
    SELECT COUNT(*) 
    FROM load_value lv 
    JOIN load_profile lp ON lv.load_profile_id = lp.id 
    WHERE lp.project_id = 1
""")
count_all = cursor.fetchone()[0]
print(f"Alle Datenpunkte: {count_all}")

conn.close()
