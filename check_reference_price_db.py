#!/usr/bin/env python3
"""
Prüfe Referenzpreise direkt in der Datenbank
"""

import sqlite3
import os

def check_reference_prices():
    """Prüft die Referenzpreise direkt in der Datenbank"""
    
    db_path = 'instance/bess.db'
    
    if not os.path.exists(db_path):
        print("❌ Datenbank nicht gefunden:", db_path)
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Aktuelle Referenzpreise in der Datenbank:")
        cursor.execute("SELECT id, name, price_type, price_eur_mwh, region, valid_from, valid_to FROM reference_price ORDER BY id")
        rows = cursor.fetchall()
        
        for row in rows:
            print(f"  - ID {row[0]}: {row[1]} ({row[2]}) - {row[3]} €/kWh - {row[4]} - {row[5]} bis {row[6]}")
        
        # Teste Update direkt in der Datenbank
        print(f"\n🔄 Teste Update direkt in der Datenbank...")
        cursor.execute("""
            UPDATE reference_price 
            SET price_eur_mwh = 250.0, name = 'BESS Standard-Preis (DB-TEST)'
            WHERE id = 1
        """)
        
        updated_count = cursor.rowcount
        print(f"   Betroffene Zeilen: {updated_count}")
        
        # Commit
        conn.commit()
        print(f"   ✅ Commit durchgeführt")
        
        # Prüfe nach Update
        print(f"\n🔍 Nach Update:")
        cursor.execute("SELECT id, name, price_type, price_eur_mwh, region, valid_from, valid_to FROM reference_price WHERE id = 1")
        row = cursor.fetchone()
        if row:
            print(f"  - ID {row[0]}: {row[1]} ({row[2]}) - {row[3]} €/kWh - {row[4]} - {row[5]} bis {row[6]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Prüfe Referenzpreise in der Datenbank")
    success = check_reference_prices()
    
    if success:
        print("\n✅ Prüfung abgeschlossen")
    else:
        print("\n❌ Prüfung fehlgeschlagen") 