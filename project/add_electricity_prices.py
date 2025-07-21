#!/usr/bin/env python3
"""
Migration: Strompreis-Felder zu Customer-Tabelle hinzufügen
"""

import sqlite3
from datetime import datetime, date

def add_electricity_price_fields():
    """Fügt Strompreis-Felder zur Customer-Tabelle hinzu"""
    
    # Datenbankverbindung
    db_path = 'instance/bess.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔌 Starte Strompreis-Migration...")
        
        # Prüfen ob Felder bereits existieren
        cursor.execute("PRAGMA table_info(customer)")
        columns = [column[1] for column in cursor.fetchall()]
        
        new_columns = [
            ('electricity_price', 'REAL'),
            ('grid_fees', 'REAL'),
            ('taxes', 'REAL'),
            ('total_electricity_price', 'REAL'),
            ('tariff_type', 'TEXT'),
            ('high_tariff_price', 'REAL'),
            ('low_tariff_price', 'REAL'),
            ('price_increase_rate', 'REAL'),
            ('last_price_update', 'DATE'),
            ('discount_rate', 'REAL'),
            ('calculation_period', 'INTEGER'),
            ('updated_at', 'TIMESTAMP')
        ]
        
        added_columns = []
        for column_name, column_type in new_columns:
            if column_name not in columns:
                cursor.execute(f"ALTER TABLE customer ADD COLUMN {column_name} {column_type}")
                added_columns.append(column_name)
                print(f"  ✅ Spalte '{column_name}' hinzugefügt")
            else:
                print(f"  ℹ️  Spalte '{column_name}' existiert bereits")
        
        # Standardwerte für bestehende Kunden setzen
        if added_columns:
            print("\n💰 Setze Standardwerte für bestehende Kunden...")
            
            # Aktuelle Durchschnittspreise in Deutschland (2024)
            default_values = {
                'electricity_price': 30.0,      # 30 ct/kWh
                'grid_fees': 7.0,               # 7 ct/kWh
                'taxes': 5.0,                   # 5 ct/kWh
                'total_electricity_price': 42.0, # 42 ct/kWh
                'tariff_type': 'single',
                'high_tariff_price': 35.0,      # 35 ct/kWh
                'low_tariff_price': 25.0,       # 25 ct/kWh
                'price_increase_rate': 3.0,     # 3% jährlich
                'last_price_update': date.today().isoformat(),
                'discount_rate': 5.0,           # 5%
                'calculation_period': 20,       # 20 Jahre
                'updated_at': datetime.now().isoformat()
            }
            
            # Nur die neuen Spalten aktualisieren
            update_fields = []
            update_values = []
            for column_name in added_columns:
                if column_name in default_values:
                    update_fields.append(f"{column_name} = ?")
                    update_values.append(default_values[column_name])
            
            if update_fields:
                cursor.execute(f"UPDATE customer SET {', '.join(update_fields)}", update_values)
                print(f"  ✅ Standardwerte für {len(update_values)} Felder gesetzt")
        
        # Änderungen speichern
        conn.commit()
        
        # Kunden mit Strompreisen anzeigen
        cursor.execute("""
            SELECT id, name, company, electricity_price, total_electricity_price, tariff_type 
            FROM customer 
            LIMIT 5
        """)
        customers = cursor.fetchall()
        
        print(f"\n📊 {len(customers)} Kunden mit Strompreisen:")
        for customer in customers:
            print(f"  • {customer[1]} ({customer[2] or 'Privat'}) - {customer[3] or 'N/A'} ct/kWh")
        
        print("\n🎉 Strompreis-Migration erfolgreich abgeschlossen!")
        print("\n💡 Nächste Schritte:")
        print("  1. Kunden bearbeiten und individuelle Strompreise eingeben")
        print("  2. Wirtschaftlichkeitsberechnung in Projekten aktivieren")
        print("  3. Amortisationszeit und ROI berechnen")
        
    except Exception as e:
        print(f"❌ Fehler bei der Migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_electricity_price_fields() 