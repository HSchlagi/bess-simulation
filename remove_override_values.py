#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Entfernt Override-Werte aus der market_price_config Tabelle
Damit wird die dynamische Berechnung mit Anteilen aktiviert
"""

import sqlite3
import os

def remove_override_values():
    """Entfernt Override-Werte (srl_availability_hours und sre_activation_energy_mwh)"""
    db_path = 'instance/bess.db'
    
    if not os.path.exists(db_path):
        print(f"[FEHLER] Datenbank nicht gefunden: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("[INFO] Entferne Override-Werte aus der Datenbank...")
        
        # Entferne Override-Werte
        cursor.execute("""
            UPDATE market_price_config 
            SET srl_availability_hours = NULL, 
                sre_activation_energy_mwh = NULL
            WHERE srl_availability_hours IS NOT NULL 
               OR sre_activation_energy_mwh IS NOT NULL
        """)
        
        affected = cursor.rowcount
        conn.commit()
        
        print(f"[OK] {affected} Konfiguration(en) aktualisiert")
        
        # Zeige aktuelle Werte
        cursor.execute("""
            SELECT project_id, 
                   srl_negative_availability_share,
                   srl_positive_availability_share,
                   sre_negative_activation_share,
                   sre_positive_activation_share,
                   srl_availability_hours,
                   sre_activation_energy_mwh
            FROM market_price_config
        """)
        rows = cursor.fetchall()
        
        print("\n[INFO] Aktuelle Konfigurationen:")
        for row in rows:
            project_id = row[0] if row[0] else "Global"
            print(f"  Project {project_id}:")
            print(f"    SRL- Anteil: {row[1]}")
            print(f"    SRL+ Anteil: {row[2]}")
            print(f"    SRE- Anteil: {row[3]}")
            print(f"    SRE+ Anteil: {row[4]}")
            print(f"    Override Hours: {row[5]}")
            print(f"    Override Energy: {row[6]}")
            print()
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"[FEHLER] Fehler beim Entfernen der Override-Werte: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        conn.close()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Entferne Override-Werte aus Marktpreis-Konfiguration")
    print("=" * 60)
    if remove_override_values():
        print("\n[OK] Override-Werte erfolgreich entfernt!")
        print("[INFO] Dynamische Berechnung mit Anteilen ist jetzt aktiv")
    else:
        print("\n[FEHLER] Fehler beim Entfernen der Override-Werte!")

