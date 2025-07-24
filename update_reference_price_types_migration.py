#!/usr/bin/env python3
"""
Migration: Referenzpreise von Energieträgern auf BESS-Komponenten umstellen
"""

import sqlite3
import os

def update_reference_price_types():
    """Stellt Referenzpreise von Energieträgern auf BESS-Komponenten um"""
    
    db_path = 'instance/bess.db'
    
    if not os.path.exists(db_path):
        print("❌ Datenbank nicht gefunden:", db_path)
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Überprüfe aktuelle Referenzpreise...")
        
        # Aktuelle Referenzpreise anzeigen
        cursor.execute("SELECT id, name, price_type, price_eur_mwh FROM reference_price")
        current_prices = cursor.fetchall()
        
        print(f"\n📋 Aktuelle Referenzpreise ({len(current_prices)} Einträge):")
        for price in current_prices:
            print(f"  - ID {price[0]}: {price[1]} ({price[2]}) - {price[3]} €/MWh")
        
        # Neue BESS-Komponenten-Preise definieren
        new_prices = [
            {
                'name': 'BESS Standard-Preis',
                'price_type': 'bess',
                'price_eur_mwh': 120.0,
                'region': 'AT',
                'valid_from': '2025-01-01',
                'valid_until': '2025-12-31',
                'description': 'Standard-Referenzpreis für Batteriespeicher-Systeme'
            },
            {
                'name': 'Photovoltaik Standard-Preis',
                'price_type': 'photovoltaik',
                'price_eur_mwh': 85.0,
                'region': 'AT',
                'valid_from': '2025-01-01',
                'valid_until': '2025-12-31',
                'description': 'Standard-Referenzpreis für Photovoltaik-Systeme'
            },
            {
                'name': 'Wasserkraft Standard-Preis',
                'price_type': 'wasserkraft',
                'price_eur_mwh': 65.0,
                'region': 'AT',
                'valid_from': '2025-01-01',
                'valid_until': '2025-12-31',
                'description': 'Standard-Referenzpreis für Wasserkraft-Systeme'
            },
            {
                'name': 'Windkraft Standard-Preis',
                'price_type': 'windkraft',
                'price_eur_mwh': 75.0,
                'region': 'AT',
                'valid_from': '2025-01-01',
                'valid_until': '2025-12-31',
                'description': 'Standard-Referenzpreis für Windkraft-Systeme'
            },
            {
                'name': 'Wärmepumpe Standard-Preis',
                'price_type': 'waermepumpe',
                'price_eur_mwh': 95.0,
                'region': 'AT',
                'valid_from': '2025-01-01',
                'valid_until': '2025-12-31',
                'description': 'Standard-Referenzpreis für Wärmepumpen-Systeme'
            },
            {
                'name': 'Sonstiges Standard-Preis',
                'price_type': 'sonstiges',
                'price_eur_mwh': 100.0,
                'region': 'AT',
                'valid_from': '2025-01-01',
                'valid_until': '2025-12-31',
                'description': 'Standard-Referenzpreis für sonstige Komponenten'
            }
        ]
        
        print(f"\n🔄 Starte Migration zu BESS-Komponenten-Preisen...")
        
        # Alte Referenzpreise löschen
        cursor.execute("DELETE FROM reference_price")
        deleted_count = cursor.rowcount
        print(f"✅ {deleted_count} alte Referenzpreise gelöscht")
        
        # Neue BESS-Komponenten-Preise einfügen (mit korrekter Spaltenreihenfolge)
        for price_data in new_prices:
            cursor.execute("""
                INSERT INTO reference_price 
                (name, price_type, price_eur_mwh, region, valid_from, valid_until, description, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (
                price_data['name'],
                price_data['price_type'],
                price_data['price_eur_mwh'],
                price_data['region'],
                price_data['valid_from'],
                price_data['valid_until'],
                price_data['description']
            ))
        
        inserted_count = len(new_prices)
        print(f"✅ {inserted_count} neue BESS-Komponenten-Preise eingefügt")
        
        # Bestätigung anzeigen
        cursor.execute("SELECT id, name, price_type, price_eur_mwh FROM reference_price ORDER BY price_type")
        new_prices_db = cursor.fetchall()
        
        print(f"\n📋 Neue Referenzpreise ({len(new_prices_db)} Einträge):")
        for price in new_prices_db:
            print(f"  - ID {price[0]}: {price[1]} ({price[2]}) - {price[3]} €/MWh")
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Fehler bei der Migration: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starte Migration: Referenzpreise zu BESS-Komponenten")
    success = update_reference_price_types()
    
    if success:
        print("\n✅ Migration erfolgreich abgeschlossen")
    else:
        print("\n❌ Migration fehlgeschlagen") 