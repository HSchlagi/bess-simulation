#!/usr/bin/env python3
"""
Skript zum Löschen der alten Spot-Preis-Daten aus der Datenbank
"""

from app import create_app, get_db

def clear_spot_price_data():
    """Löscht alle Spot-Preis-Daten aus der Datenbank"""
    app = create_app()
    
    with app.app_context():
        try:
            conn = get_db()
            cursor = conn.cursor()
            
            # Prüfe Anzahl der vorhandenen Daten
            cursor.execute("SELECT COUNT(*) FROM spot_price")
            count_before = cursor.fetchone()[0]
            print(f"📊 Vorhandene Spot-Preis-Daten: {count_before}")
            
            if count_before > 0:
                # Zeige die ersten 5 Datensätze
                cursor.execute("SELECT timestamp, source FROM spot_price ORDER BY timestamp DESC LIMIT 5")
                print("📋 Erste 5 Datensätze:")
                for row in cursor.fetchall():
                    print(f"  {row[0]} - {row[1]}")
                
                # Lösche alle Spot-Preis-Daten
                cursor.execute("DELETE FROM spot_price")
                deleted_count = cursor.rowcount
                
                # Commit der Änderungen
                conn.commit()
                
                print(f"✅ {deleted_count} Spot-Preis-Daten erfolgreich gelöscht")
                
                # Prüfe ob Tabelle jetzt leer ist
                cursor.execute("SELECT COUNT(*) FROM spot_price")
                count_after = cursor.fetchone()[0]
                print(f"📊 Verbleibende Spot-Preis-Daten: {count_after}")
                
            else:
                print("ℹ️ Keine Spot-Preis-Daten vorhanden")
                
        except Exception as e:
            print(f"❌ Fehler beim Löschen der Spot-Preis-Daten: {e}")
            conn.rollback()

if __name__ == '__main__':
    print("🧹 Bereinige Spot-Preis-Datenbank...")
    clear_spot_price_data()
    print("✅ Fertig!")
