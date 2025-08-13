#!/usr/bin/env python3
import sqlite3

# Datenbank verbinden
conn = sqlite3.connect('instance/bess.db')
cursor = conn.cursor()

# Teste Lastdaten
cursor.execute("""
    SELECT COUNT(*) FROM load_value lv 
    JOIN load_profile lp ON lv.load_profile_id = lp.id 
    WHERE lp.project_id = 1 
    AND lv.timestamp >= '2024-01-01' 
    AND lv.timestamp <= '2024-12-31'
""")
load_count = cursor.fetchone()[0]
print(f"Lastdaten für 2024: {load_count}")

# Teste PV-Daten
cursor.execute("""
    SELECT COUNT(*) FROM pvsol_export 
    WHERE project_id = 1 
    AND timestamp >= '2024-01-01' 
    AND timestamp <= '2024-12-31'
""")
pv_count = cursor.fetchone()[0]
print(f"PV-Daten für 2024: {pv_count}")

# Teste Wasserkraft-Daten
cursor.execute("""
    SELECT COUNT(*) FROM hydro_power 
    WHERE project_id = 1 
    AND timestamp >= '2024-01-01' 
    AND timestamp <= '2024-12-31'
""")
hydro_count = cursor.fetchone()[0]
print(f"Wasserkraft-Daten für 2024: {hydro_count}")

# Teste erste Datenpunkte
cursor.execute("""
    SELECT lv.timestamp, lv.power_kw 
    FROM load_value lv 
    JOIN load_profile lp ON lv.load_profile_id = lp.id 
    WHERE lp.project_id = 1 
    ORDER BY lv.timestamp 
    LIMIT 3
""")
load_samples = cursor.fetchall()
print(f"Erste Lastdaten: {load_samples}")

conn.close()
