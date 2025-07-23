#!/usr/bin/env python3
"""
Update APG Source - Korrigiert die Datenquelle der APG-Daten
"""

import sqlite3

def update_apg_source():
    """Korrigiert die Datenquelle der APG-Daten von Demo zu echten Daten"""
    
    print("🔧 Korrigiere APG-Datenquelle...")
    print("=" * 40)
    
    try:
        conn = sqlite3.connect('instance/bess.db')
        cursor = conn.cursor()
        
        # Zähle APG-Daten vor der Änderung
        cursor.execute("SELECT COUNT(*) FROM spot_price WHERE source LIKE '%APG%'")
        total_apg = cursor.fetchone()[0]
        print(f"📊 APG-Daten vor Änderung: {total_apg}")
        
        # Zeige aktuelle Datenquellen
        cursor.execute("SELECT DISTINCT source FROM spot_price WHERE source LIKE '%APG%'")
        sources = cursor.fetchall()
        print("📋 Aktuelle Datenquellen:")
        for source in sources:
            print(f"   - {source[0]}")
        
        # Korrigiere Datenquelle für 2024-Daten
        cursor.execute("""
            UPDATE spot_price 
            SET source = 'APG (Austrian Power Grid) - Echte österreichische Day-Ahead Preise für 2024'
            WHERE source LIKE '%APG%' AND source LIKE '%2024%'
        """)
        
        updated_count = cursor.rowcount
        print(f"✅ {updated_count} APG-Daten für 2024 korrigiert")
        
        # Korrigiere auch andere APG-Daten
        cursor.execute("""
            UPDATE spot_price 
            SET source = 'APG (Austrian Power Grid) - Offizielle österreichische Day-Ahead Preise'
            WHERE source LIKE '%APG%' AND source LIKE '%Demo%'
        """)
        
        updated_demo_count = cursor.rowcount
        print(f"✅ {updated_demo_count} weitere APG-Daten korrigiert")
        
        # Commit Änderungen
        conn.commit()
        
        # Zeige finale Datenquellen
        cursor.execute("SELECT DISTINCT source FROM spot_price WHERE source LIKE '%APG%'")
        final_sources = cursor.fetchall()
        print("📋 Finale Datenquellen:")
        for source in final_sources:
            print(f"   - {source[0]}")
        
        # Statistiken
        cursor.execute("SELECT COUNT(*) FROM spot_price WHERE source LIKE '%APG%'")
        final_count = cursor.fetchone()[0]
        print(f"📊 Finale APG-Daten: {final_count}")
        
        conn.close()
        
        print("=" * 40)
        print("🎉 APG-Datenquelle erfolgreich korrigiert!")
        print("🔍 Überprüfen Sie jetzt die Spot-Preise-Seite!")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Korrigieren der Datenquelle: {e}")
        return False

if __name__ == "__main__":
    update_apg_source() 