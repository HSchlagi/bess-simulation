#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script zum Prüfen der aktuellen SRE-Werte in der Datenbank
"""

import sqlite3
import os
import sys

# Windows Encoding-Fix
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def check_sre_values():
    """Prüft die aktuellen SRE-Werte in der Datenbank"""
    db_path = 'instance/bess.db'
    
    if not os.path.exists(db_path):
        print(f"[FEHLER] Datenbank nicht gefunden: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("=" * 60)
        print("Aktuelle SRE-Werte in der Datenbank")
        print("=" * 60)
        
        # Alle Market Price Configs abfragen
        cursor.execute("""
            SELECT id, project_id, 
                   sre_negative_price, sre_positive_price,
                   sre_negative_activation_share, sre_positive_activation_share,
                   srl_negative_availability_share, srl_positive_availability_share
            FROM market_price_config
            ORDER BY project_id NULLS LAST, id
        """)
        
        configs = cursor.fetchall()
        
        if not configs:
            print("[WARNUNG] Keine Konfigurationen gefunden!")
            return
        
        for config in configs:
            config_id, project_id, sre_neg_price, sre_pos_price, \
            sre_neg_share, sre_pos_share, srl_neg_share, srl_pos_share = config
            
            project_name = "Global (Standard)" if project_id is None else f"Projekt ID: {project_id}"
            
            print(f"\n[Konfiguration] ID: {config_id} - {project_name}")
            print("-" * 60)
            print(f"SRE- Preis:        {sre_neg_price or 'NULL (Standard: 80.0)'} EUR/MWh")
            print(f"SRE+ Preis:         {sre_pos_price or 'NULL (Standard: 80.0)'} EUR/MWh")
            print(f"SRE- Aktivierungsanteil: {sre_neg_share or 'NULL (Standard: 0.4518 = 45.18%)'}")
            print(f"SRE+ Aktivierungsanteil: {sre_pos_share or 'NULL (Standard: 0.2785 = 27.85%)'}")
            print(f"SRL- Verfügbarkeitsanteil: {srl_neg_share or 'NULL (Standard: 0.2347 = 23.47%)'}")
            print(f"SRL+ Verfügbarkeitsanteil: {srl_pos_share or 'NULL (Standard: 0.4506 = 45.06%)'}")
        
        print("\n" + "=" * 60)
        print("[INFO] Um diese Werte auf den Server zu uebertragen:")
        print("   1. Notieren Sie sich die Werte fuer Ihr Projekt")
        print("   2. Auf dem Server: Ueber die UI 'Marktpreise konfigurieren' oeffnen")
        print("   3. Oder SQL-Befehle auf dem Server ausfuehren (siehe unten)")
        print("=" * 60)
        
        # SQL-Befehle generieren für das erste Projekt
        if configs:
            first_config = configs[0]
            config_id, project_id, sre_neg_price, sre_pos_price, \
            sre_neg_share, sre_pos_share, srl_neg_share, srl_pos_share = first_config
            
            if project_id:
                print("\n[SQL] Befehle fuer den Server (fuer Projekt ID {}):".format(project_id))
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
        
    except Exception as e:
        print(f"[FEHLER] Fehler: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == '__main__':
    check_sre_values()

