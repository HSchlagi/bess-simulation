#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script zum Exportieren von Use Cases aus der Datenbank
"""

import sqlite3
import json
import os
import sys

# Windows Encoding-Fix
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def export_use_cases(project_id=None):
    """Exportiert Use Cases aus der Datenbank"""
    db_path = 'instance/bess.db'
    
    if not os.path.exists(db_path):
        print(f"[FEHLER] Datenbank nicht gefunden: {db_path}")
        return None
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Use Cases abfragen
        if project_id:
            cursor.execute("""
                SELECT id, project_id, name, description, scenario_type,
                       pv_power_mwp, hydro_power_kw, hydro_energy_mwh_year,
                       wind_power_kw, bess_size_mwh, bess_power_mw
                FROM use_case
                WHERE project_id = ?
                ORDER BY project_id, name
            """, (project_id,))
        else:
            cursor.execute("""
                SELECT id, project_id, name, description, scenario_type,
                       pv_power_mwp, hydro_power_kw, hydro_energy_mwh_year,
                       wind_power_kw, bess_size_mwh, bess_power_mw
                FROM use_case
                ORDER BY project_id, name
            """)
        
        use_cases = cursor.fetchall()
        
        if not use_cases:
            print("[WARNUNG] Keine Use Cases gefunden!")
            return None
        
        # Projekte abfragen für bessere Lesbarkeit
        cursor.execute("SELECT id, name FROM project")
        projects = {pid: pname for pid, pname in cursor.fetchall()}
        
        # Daten strukturieren
        export_data = []
        for uc in use_cases:
            uc_id, project_id_val, name, description, scenario_type, \
            pv_power_mwp, hydro_power_kw, hydro_energy_mwh_year, \
            wind_power_kw, bess_size_mwh, bess_power_mw = uc
            
            project_name = projects.get(project_id_val, f"Projekt ID {project_id_val}")
            
            export_data.append({
                'id': uc_id,
                'project_id': project_id_val,
                'project_name': project_name,
                'name': name,
                'description': description,
                'scenario_type': scenario_type,
                'pv_power_mwp': pv_power_mwp,
                'hydro_power_kw': hydro_power_kw,
                'hydro_energy_mwh_year': hydro_energy_mwh_year,
                'wind_power_kw': wind_power_kw,
                'bess_size_mwh': bess_size_mwh,
                'bess_power_mw': bess_power_mw
            })
        
        return export_data
        
    except Exception as e:
        print(f"[FEHLER] Fehler beim Exportieren: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        conn.close()

def print_use_cases(use_cases):
    """Gibt Use Cases formatiert aus"""
    if not use_cases:
        return
    
    print("=" * 60)
    print("Exportierte Use Cases")
    print("=" * 60)
    
    current_project = None
    for uc in use_cases:
        if current_project != uc['project_id']:
            current_project = uc['project_id']
            print(f"\n[Projekt] ID: {uc['project_id']} - {uc['project_name']}")
            print("-" * 60)
        
        print(f"\n  {uc['name']}: {uc['description']}")
        print(f"    Typ: {uc['scenario_type']}")
        if uc['pv_power_mwp'] > 0:
            print(f"    PV: {uc['pv_power_mwp']} MWp")
        if uc['hydro_power_kw'] > 0:
            print(f"    Wasserkraft: {uc['hydro_power_kw']} kW ({uc['hydro_energy_mwh_year']} MWh/a)")
        if uc['wind_power_kw'] > 0:
            print(f"    Wind: {uc['wind_power_kw']} kW")
        if uc['bess_size_mwh'] > 0:
            print(f"    BESS: {uc['bess_size_mwh']} MWh / {uc['bess_power_mw']} MW")

def generate_sql_import(use_cases):
    """Generiert SQL-Befehle zum Importieren der Use Cases"""
    if not use_cases:
        return
    
    print("\n" + "=" * 60)
    print("SQL-Befehle zum Importieren auf dem Server")
    print("=" * 60)
    print("\n-- WICHTIG: Bestehende Use Cases werden NICHT gelöscht!")
    print("-- Verwenden Sie DELETE FROM use_case WHERE project_id = X; falls nötig\n")
    
    for uc in use_cases:
        print(f"-- Use Case für Projekt {uc['project_id']} ({uc['project_name']})")
        print(f"INSERT OR REPLACE INTO use_case (")
        print(f"    id, project_id, name, description, scenario_type,")
        print(f"    pv_power_mwp, hydro_power_kw, hydro_energy_mwh_year,")
        print(f"    wind_power_kw, bess_size_mwh, bess_power_mw")
        print(f") VALUES (")
        print(f"    {uc['id']}, {uc['project_id']}, '{uc['name']}', '{uc['description']}', '{uc['scenario_type']}',")
        print(f"    {uc['pv_power_mwp']}, {uc['hydro_power_kw']}, {uc['hydro_energy_mwh_year']},")
        print(f"    {uc['wind_power_kw']}, {uc['bess_size_mwh']}, {uc['bess_power_mw']}")
        print(f");\n")

def save_to_json(use_cases, filename='use_cases_export.json'):
    """Speichert Use Cases als JSON-Datei"""
    if not use_cases:
        return
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(use_cases, f, indent=2, ensure_ascii=False)
    
    print(f"\n[OK] Use Cases in {filename} gespeichert")

if __name__ == '__main__':
    import sys
    
    project_id = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else None
    
    use_cases = export_use_cases(project_id)
    
    if use_cases:
        print_use_cases(use_cases)
        generate_sql_import(use_cases)
        save_to_json(use_cases)
        print("\n" + "=" * 60)
        print("[INFO] Naechste Schritte:")
        print("   1. Kopieren Sie die SQL-Befehle")
        print("   2. Auf dem Server: sqlite3 instance/bess.db")
        print("   3. Fuehren Sie die SQL-Befehle aus")
        print("   4. Oder verwenden Sie die JSON-Datei mit einem Import-Script")
        print("=" * 60)

