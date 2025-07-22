#!/usr/bin/env python3
import sqlite3
import os

# Pfad zur Datenbank
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'bess.db')

print("=== DATENBANK KOMPLETT KORRIGIEREN ===")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Alle Werte komplett neu setzen
    update_query = """
    UPDATE project SET 
        name = 'BESS-Hinterstoder',
        location = 'Hinterstoder',
        date = '2025-07-18',
        bess_size = 5000.0,
        bess_power = 5000.0,
        pv_power = 1480.0,
        hp_power = 0.0,
        wind_power = 0.0,
        hydro_power = 540.0,
        bess_investment = 1050000.0,
        pv_investment = 30000.0,
        wind_investment = 0.0,
        hydro_investment = 25000.0,
        hp_investment = 0.0,
        other_investment = 16.5,
        bess_operation_cost = 13125.0,
        pv_operation_cost = 300.0,
        wind_operation_cost = 0.0,
        hydro_operation_cost = 375.0,
        hp_operation_cost = 0.0,
        other_operation_cost = 0.0
    WHERE id = 1
    """
    
    cursor.execute(update_query)
    conn.commit()
    
    # Neue Werte anzeigen
    print("\n--- NEUE WERTE ---")
    cursor.execute("SELECT * FROM project WHERE id = 1")
    project = cursor.fetchone()
    
    if project:
        print(f"Name: {project[1]}")
        print(f"BESS Size: {project[3]}")
        print(f"BESS Power: {project[4]}")
        print(f"PV Power: {project[5]}")
        print(f"HP Power: {project[6]}")
        print(f"Wind Power: {project[7]}")
        print(f"Hydro Power: {project[8]}")
        print(f"BESS Investment: {project[9]}")
        print(f"PV Investment: {project[10]}")
        print(f"Wind Investment: {project[11]}")
        print(f"Hydro Investment: {project[12]}")
        print(f"HP Investment: {project[13]}")
        print(f"Other Investment: {project[14]}")
        print(f"BESS Operation Cost: {project[15]}")
        print(f"PV Operation Cost: {project[16]}")
        print(f"Wind Operation Cost: {project[17]}")
        print(f"Hydro Operation Cost: {project[18]}")
        print(f"HP Operation Cost: {project[19]}")
        print(f"Other Operation Cost: {project[20]}")
    
    print("\n✅ DATENBANK ERFOLGREICH KORRIGIERT!")
    
except Exception as e:
    print(f"❌ Fehler: {e}")
finally:
    if conn:
        conn.close() 