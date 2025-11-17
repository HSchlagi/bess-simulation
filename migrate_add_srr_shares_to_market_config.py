#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migration-Script: Verfügbarkeits- und Aktivierungsanteile zur market_price_config Tabelle hinzufügen
Fügt die neuen Spalten für SRL/SRE-Anteile hinzu
"""

import sqlite3
import os
from datetime import datetime

def add_srr_share_columns():
    """Fügt Verfügbarkeits- und Aktivierungsanteile zur market_price_config Tabelle hinzu"""
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
            ('srl_negative_availability_share', 'FLOAT', 'SRL- Verfügbarkeitsanteil (0.0-1.0)'),
            ('srl_positive_availability_share', 'FLOAT', 'SRL+ Verfügbarkeitsanteil (0.0-1.0)'),
            ('sre_negative_activation_share', 'FLOAT', 'SRE- Aktivierungsanteil (0.0-1.0)'),
            ('sre_positive_activation_share', 'FLOAT', 'SRE+ Aktivierungsanteil (0.0-1.0)')
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
        
        # Standardwerte für bestehende Konfigurationen setzen
        print("\n[INFO] Setze Standardwerte für bestehende Konfigurationen...")
        cursor.execute("SELECT id FROM market_price_config")
        configs = cursor.fetchall()
        
        updated_count = 0
        for config_id, in configs:
            updates = []
            values = []
            
            # Prüfe welche Werte NULL sind
            cursor.execute(f"""
                SELECT srl_negative_availability_share, srl_positive_availability_share,
                       sre_negative_activation_share, sre_positive_activation_share
                FROM market_price_config WHERE id = ?
            """, (config_id,))
            result = cursor.fetchone()
            
            if result:
                defaults = {
                    'srl_negative_availability_share': 0.2347,  # 23.47%
                    'srl_positive_availability_share': 0.4506,  # 45.06%
                    'sre_negative_activation_share': 0.4518,  # 45.18%
                    'sre_positive_activation_share': 0.2785   # 27.85%
                }
                
                for idx, (col_name, default_value) in enumerate(defaults.items()):
                    if result[idx] is None:
                        updates.append(f"{col_name} = ?")
                        values.append(default_value)
                
                if updates:
                    values.append(config_id)
                    update_sql = f"""
                        UPDATE market_price_config 
                        SET {', '.join(updates)}, updated_at = datetime('now')
                        WHERE id = ?
                    """
                    cursor.execute(update_sql, values)
                    updated_count += 1
        
        if updated_count > 0:
            conn.commit()
            print(f"[OK] {updated_count} Konfiguration(en) mit Standardwerten aktualisiert")
        else:
            print("[INFO] Alle Konfigurationen haben bereits Werte")
        
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
    print("Migration: Verfügbarkeits- und Aktivierungsanteile hinzufügen")
    print("=" * 60)
    if add_srr_share_columns():
        print("\n[OK] Migration erfolgreich abgeschlossen!")
    else:
        print("\n[FEHLER] Migration fehlgeschlagen!")

