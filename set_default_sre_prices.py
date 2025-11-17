#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setzt Standardwerte für SRE-Preise in bestehenden MarketPriceConfig Einträgen
"""

import sqlite3
import os
from datetime import datetime

def set_default_sre_prices():
    """Setzt Standardwerte für SRE-Preise in bestehenden Konfigurationen"""
    db_path = 'instance/bess.db'
    
    if not os.path.exists(db_path):
        print(f"[FEHLER] Datenbank nicht gefunden: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Standardwerte
        default_values = {
            'srl_negative_price': 18.0,  # €/MW/h
            'srl_positive_price': 18.0,  # €/MW/h
            'sre_negative_price': 80.0,  # €/MWh
            'sre_positive_price': 80.0,  # €/MWh
            'sre_activation_energy_mwh': 250.0,  # MWh/Jahr
            'srl_availability_hours': 8000.0  # Stunden/Jahr
        }
        
        # Alle bestehenden Konfigurationen holen
        cursor.execute("SELECT id, project_id, name FROM market_price_config")
        configs = cursor.fetchall()
        
        if not configs:
            print("[INFO] Keine bestehenden Konfigurationen gefunden")
            conn.close()
            return True
        
        print(f"[INFO] {len(configs)} Konfiguration(en) gefunden")
        
        updated_count = 0
        for config_id, project_id, name in configs:
            updates = []
            values = []
            
            # Prüfe welche Spalten NULL sind und setze Standardwerte
            for col_name, default_value in default_values.items():
                cursor.execute(f"""
                    SELECT {col_name} FROM market_price_config WHERE id = ?
                """, (config_id,))
                result = cursor.fetchone()
                
                if result and result[0] is None:
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
                project_info = f"Projekt {project_id}" if project_id else "Global"
                print(f"[OK] Standardwerte für {project_info} (ID: {config_id}, Name: {name or 'N/A'}) gesetzt")
        
        if updated_count > 0:
            conn.commit()
            print(f"\n[OK] {updated_count} Konfiguration(en) aktualisiert")
        else:
            print("\n[INFO] Alle Konfigurationen haben bereits Werte, keine Änderungen erforderlich")
        
        # Prüfe ob eine globale Standard-Konfiguration existiert, falls nicht erstelle eine
        cursor.execute("""
            SELECT id FROM market_price_config 
            WHERE project_id IS NULL AND is_default = 1
        """)
        global_config = cursor.fetchone()
        
        if not global_config:
            print("\n[INFO] Erstelle globale Standard-Konfiguration...")
            cursor.execute("""
                INSERT INTO market_price_config 
                (project_id, spot_arbitrage_price, intraday_trading_price, balancing_energy_price,
                 frequency_regulation_price, capacity_market_price, flexibility_market_price,
                 srl_negative_price, srl_positive_price, sre_negative_price, sre_positive_price,
                 sre_activation_energy_mwh, srl_availability_hours, name, description, is_default,
                 reference_year, created_at, updated_at)
                VALUES (NULL, 0.0074, 0.0111, 0.0231, 0.30, 0.18, 0.22,
                        18.0, 18.0, 80.0, 80.0, 250.0, 8000.0,
                        'Globale Standard-Marktpreise', 'Globale Standard-Konfiguration für alle Projekte',
                        1, ?, datetime('now'), datetime('now'))
            """, (datetime.now().year,))
            conn.commit()
            print("[OK] Globale Standard-Konfiguration erstellt")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"[FEHLER] Fehler beim Setzen der Standardwerte: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        conn.close()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Setze Standardwerte für SRE-Preise in MarketPriceConfig")
    print("=" * 60)
    if set_default_sre_prices():
        print("\n[OK] Standardwerte erfolgreich gesetzt!")
    else:
        print("\n[FEHLER] Fehler beim Setzen der Standardwerte!")

