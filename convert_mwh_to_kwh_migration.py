#!/usr/bin/env python3
"""
Migration: Referenzpreise von €/MWh auf €/kWh umstellen
"""

import sqlite3
import os

def convert_mwh_to_kwh():
    """Konvertiert alle Referenzpreise von €/MWh auf €/kWh"""
    
    db_path = 'instance/bess.db'
    
    if not os.path.exists(db_path):
        print("❌ Datenbank nicht gefunden:", db_path)
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Aktuelle Referenzpreise (€/MWh):")
        cursor.execute("SELECT id, name, price_type, price_eur_mwh FROM reference_price ORDER BY price_type")
        current_prices = cursor.fetchall()
        
        for price in current_prices:
            print(f"  - ID {price[0]}: {price[1]} ({price[2]}) - {price[3]} €/MWh")
        
        print(f"\n🔄 Konvertiere von €/MWh auf €/kWh (Division durch 1000)...")
        
        # Alle Preise umrechnen: €/MWh → €/kWh (Division durch 1000)
        cursor.execute("UPDATE reference_price SET price_eur_mwh = price_eur_mwh / 1000")
        updated_count = cursor.rowcount
        
        print(f"✅ {updated_count} Referenzpreise konvertiert")
        
        # Bestätigung anzeigen
        cursor.execute("SELECT id, name, price_type, price_eur_mwh FROM reference_price ORDER BY price_type")
        new_prices = cursor.fetchall()
        
        print(f"\n📋 Neue Referenzpreise (€/kWh):")
        for price in new_prices:
            print(f"  - ID {price[0]}: {price[1]} ({price[2]}) - {price[3]:.3f} €/kWh")
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Fehler bei der Migration: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starte Migration: €/MWh → €/kWh")
    success = convert_mwh_to_kwh()
    
    if success:
        print("\n✅ Migration erfolgreich abgeschlossen")
    else:
        print("\n❌ Migration fehlgeschlagen") 