#!/usr/bin/env python3
import sqlite3
import os

# Pfad zur Datenbank
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'bess.db')

print("=== DATENBANK-WERTE KORRIGIEREN ===")
print(f"Datenbank: {db_path}")

try:
    # Verbindung zur Datenbank
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Aktuelle Werte anzeigen
    print("\n--- AKTUELLE WERTE ---")
    cursor.execute("SELECT bess_size, bess_power, pv_power, bess_investment, pv_investment FROM project WHERE id = 1")
    current = cursor.fetchone()
    if current:
        print(f"BESS Size: {current[0]}")
        print(f"BESS Power: {current[1]}")
        print(f"PV Power: {current[2]}")
        print(f"BESS Investment: {current[3]}")
        print(f"PV Investment: {current[4]}")
    
    # Werte korrigieren
    print("\n--- WERTE KORRIGIEREN ---")
    update_query = """
    UPDATE project SET 
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
    cursor.execute("SELECT bess_size, bess_power, pv_power, bess_investment, pv_investment FROM project WHERE id = 1")
    new_values = cursor.fetchone()
    if new_values:
        print(f"BESS Size: {new_values[0]}")
        print(f"BESS Power: {new_values[1]}")
        print(f"PV Power: {new_values[2]}")
        print(f"BESS Investment: {new_values[3]}")
        print(f"PV Investment: {new_values[4]}")
    
    print("\n✅ Datenbank erfolgreich aktualisiert!")
    
except Exception as e:
    print(f"❌ Fehler: {e}")
finally:
    if conn:
        conn.close() 