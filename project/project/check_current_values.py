#!/usr/bin/env python3
import sqlite3
import os

# Pfad zur Datenbank
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'bess.db')

print("=== AKTUELLE DATENBANK-WERTE ===")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM project WHERE id = 1")
    project = cursor.fetchone()
    
    if project:
        print(f"ID: {project[0]}")
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
    else:
        print("Projekt nicht gefunden!")
        
except Exception as e:
    print(f"Fehler: {e}")
finally:
    if conn:
        conn.close() 