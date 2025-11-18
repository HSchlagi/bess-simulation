#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script zum Prüfen der SRE-Werte für ein spezifisches Projekt
"""

import sqlite3
import os
import sys

# Windows Encoding-Fix
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def check_project_sre_values(project_name_filter=None):
    """Prüft die SRE-Werte für Projekte (optional gefiltert nach Namen)"""
    db_path = 'instance/bess.db'
    
    if not os.path.exists(db_path):
        print(f"[FEHLER] Datenbank nicht gefunden: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("=" * 60)
        print("Projekte und SRE-Werte in der Datenbank")
        print("=" * 60)
        
        # Alle Projekte abfragen
        cursor.execute("""
            SELECT id, name, customer_name 
            FROM project 
            ORDER BY id
        """)
        
        projects = cursor.fetchall()
        
        if not projects:
            print("[WARNUNG] Keine Projekte gefunden!")
            return
        
        print("\nVerfuegbare Projekte:")
        print("-" * 60)
        for project_id, project_name, customer_name in projects:
            print(f"ID: {project_id} - {project_name} ({customer_name})")
        
        # Für jedes Projekt die SRE-Werte abfragen
        print("\n" + "=" * 60)
        print("SRE-Werte pro Projekt:")
        print("=" * 60)
        
        for project_id, project_name, customer_name in projects:
            # Prüfen ob Filter gesetzt ist
            if project_name_filter and project_name_filter.lower() not in project_name.lower():
                continue
            
            cursor.execute("""
                SELECT id, 
                       sre_negative_price, sre_positive_price,
                       sre_negative_activation_share, sre_positive_activation_share,
                       srl_negative_availability_share, srl_positive_availability_share
                FROM market_price_config
                WHERE project_id = ?
            """, (project_id,))
            
            config = cursor.fetchone()
            
            if config:
                config_id, sre_neg_price, sre_pos_price, \
                sre_neg_share, sre_pos_share, srl_neg_share, srl_pos_share = config
                
                print(f"\n[Projekt] ID: {project_id} - {project_name}")
                print(f"          Kunde: {customer_name}")
                print("-" * 60)
                print(f"SRE- Preis:        {sre_neg_price or 'NULL (Standard: 80.0)'} EUR/MWh")
                print(f"SRE+ Preis:         {sre_pos_price or 'NULL (Standard: 80.0)'} EUR/MWh")
                print(f"SRE- Aktivierungsanteil: {sre_neg_share or 'NULL (Standard: 0.4518 = 45.18%)'}")
                print(f"SRE+ Aktivierungsanteil: {sre_pos_share or 'NULL (Standard: 0.2785 = 27.85%)'}")
                print(f"SRL- Verfügbarkeitsanteil: {srl_neg_share or 'NULL (Standard: 0.2347 = 23.47%)'}")
                print(f"SRL+ Verfügbarkeitsanteil: {srl_pos_share or 'NULL (Standard: 0.4506 = 45.06%)'}")
                
                # SQL-Befehle generieren
                print(f"\n[SQL] Update-Befehle fuer Projekt ID {project_id}:")
                print("-" * 60)
                if sre_neg_price is not None:
                    print(f"UPDATE market_price_config SET sre_negative_price = {sre_neg_price} WHERE project_id = {project_id};")
                if sre_pos_price is not None:
                    print(f"UPDATE market_price_config SET sre_positive_price = {sre_pos_price} WHERE project_id = {project_id};")
                if sre_neg_share is not None:
                    print(f"UPDATE market_price_config SET sre_negative_activation_share = {sre_neg_share} WHERE project_id = {project_id};")
                if sre_pos_share is not None:
                    print(f"UPDATE market_price_config SET sre_positive_activation_share = {sre_pos_share} WHERE project_id = {project_id};")
                if srl_neg_share is not None:
                    print(f"UPDATE market_price_config SET srl_negative_availability_share = {srl_neg_share} WHERE project_id = {project_id};")
                if srl_pos_share is not None:
                    print(f"UPDATE market_price_config SET srl_positive_availability_share = {srl_pos_share} WHERE project_id = {project_id};")
            else:
                print(f"\n[Projekt] ID: {project_id} - {project_name}")
                print(f"          Kunde: {customer_name}")
                print("          [INFO] Keine spezifische Konfiguration gefunden - verwendet Standardwerte")
        
        print("\n" + "=" * 60)
        print("[INFO] Um Werte zu aktualisieren:")
        print("   1. Verwenden Sie die generierten SQL-Befehle")
        print("   2. Oder ueber die UI: 'Marktpreise konfigurieren'")
        print("=" * 60)
        
    except Exception as e:
        print(f"[FEHLER] Fehler: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == '__main__':
    import sys
    project_filter = sys.argv[1] if len(sys.argv) > 1 else None
    check_project_sre_values(project_filter)

