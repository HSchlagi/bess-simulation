#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migration-Script: SRE-Preise zur market_price_config Tabelle hinzufügen
Fügt die neuen Spalten für SRL/SRE-Preise und Aktivierungsenergie hinzu
"""

import sqlite3
import os
from datetime import datetime

def add_sre_price_columns():
    """Fügt SRE-Preis-Spalten zur market_price_config Tabelle hinzu"""
    db_path = 'instance/bess.db'
    
    if not os.path.exists(db_path):
        print(f"[FEHLER] Datenbank nicht gefunden: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Prüfen ob Tabelle existiert
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='market_price_config'
        """)
        
        if not cursor.fetchone():
            print("[FEHLER] Tabelle 'market_price_config' existiert nicht!")
            conn.close()
            return False
        
        # Prüfe welche Spalten bereits existieren
        cursor.execute("PRAGMA table_info(market_price_config);")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"[INFO] Vorhandene Spalten: {', '.join(column_names)}")
        
        # Neue Spalten hinzufügen (falls nicht vorhanden)
        new_columns = [
            ('srl_negative_price', 'FLOAT', 'SRL- Preis (€/MW/h)'),
            ('srl_positive_price', 'FLOAT', 'SRL+ Preis (€/MW/h)'),
            ('sre_negative_price', 'FLOAT', 'SRE- Preis (€/MWh)'),
            ('sre_positive_price', 'FLOAT', 'SRE+ Preis (€/MWh)'),
            ('sre_activation_energy_mwh', 'FLOAT', 'Aktivierungsenergie (MWh/Jahr)'),
            ('srl_availability_hours', 'FLOAT', 'Verfügbarkeitsstunden (h/Jahr)')
        ]
        
        added_count = 0
        for col_name, col_type, description in new_columns:
            if col_name not in column_names:
                try:
                    cursor.execute(f"""
                        ALTER TABLE market_price_config 
                        ADD COLUMN {col_name} {col_type}
                    """)
                    print(f"[OK] Spalte '{col_name}' ({description}) hinzugefügt")
                    added_count += 1
                except sqlite3.OperationalError as e:
                    print(f"[WARNUNG] Spalte '{col_name}' konnte nicht hinzugefügt werden: {e}")
            else:
                print(f"[INFO] Spalte '{col_name}' existiert bereits")
        
        if added_count > 0:
            conn.commit()
            print(f"[OK] {added_count} neue Spalte(n) erfolgreich hinzugefügt")
        else:
            print("[INFO] Alle Spalten existieren bereits, keine Änderungen erforderlich")
        
        # Prüfe ob reference_year Spalte existiert (falls nicht, hinzufügen)
        if 'reference_year' not in column_names:
            try:
                cursor.execute("""
                    ALTER TABLE market_price_config 
                    ADD COLUMN reference_year INTEGER
                """)
                conn.commit()
                print("[OK] Spalte 'reference_year' hinzugefügt")
            except sqlite3.OperationalError as e:
                print(f"[WARNUNG] Spalte 'reference_year' konnte nicht hinzugefügt werden: {e}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"[FEHLER] Fehler beim Hinzufügen der Spalten: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        conn.close()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Migration: SRE-Preise zur market_price_config Tabelle hinzufügen")
    print("=" * 60)
    if add_sre_price_columns():
        print("\n[OK] Migration erfolgreich abgeschlossen!")
    else:
        print("\n[FEHLER] Migration fehlgeschlagen!")

