#!/usr/bin/env python3
"""
Datenbank-Migration: Investitionskosten-Felder hinzufügen
"""

import sqlite3
import os

def add_investment_cost_columns():
    """Fügt die Investitionskosten-Spalten zur Projekt-Tabelle hinzu"""
    
    # Datenbank-Pfad
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'bess.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Datenbank nicht gefunden: {db_path}")
        return False
    
    try:
        # Verbindung zur Datenbank
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Prüfen ob Spalten bereits existieren
        cursor.execute("PRAGMA table_info(project)")
        existing_columns = [column[1] for column in cursor.fetchall()]
        
        # Neue Spalten definieren
        new_columns = [
            ('bess_investment', 'FLOAT'),
            ('pv_investment', 'FLOAT'),
            ('wind_investment', 'FLOAT'),
            ('hydro_investment', 'FLOAT'),
            ('hp_investment', 'FLOAT'),
            ('bess_operation_cost', 'FLOAT'),
            ('pv_operation_cost', 'FLOAT'),
            ('wind_operation_cost', 'FLOAT'),
            ('hydro_operation_cost', 'FLOAT'),
            ('hp_operation_cost', 'FLOAT')
        ]
        
        # Spalten hinzufügen
        for column_name, column_type in new_columns:
            if column_name not in existing_columns:
                print(f"🔄 Füge Spalte {column_name} hinzu...")
                cursor.execute(f"ALTER TABLE project ADD COLUMN {column_name} {column_type}")
                print(f"✅ Spalte {column_name} hinzugefügt")
            else:
                print(f"✅ Spalte {column_name} existiert bereits")
        
        # Änderungen speichern
        conn.commit()
        
        # Bestätigung anzeigen
        cursor.execute("PRAGMA table_info(project)")
        columns = cursor.fetchall()
        print(f"\n📋 Projekt-Tabelle hat jetzt {len(columns)} Spalten:")
        for column in columns:
            print(f"  - {column[1]} ({column[2]})")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Hinzufügen der Spalten: {e}")
        return False
    
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🚀 Starte Investitionskosten-Migration...")
    success = add_investment_cost_columns()
    
    if success:
        print("\n🎉 Migration erfolgreich abgeschlossen!")
        print("\n💰 Verfügbare Investitionskosten-Felder:")
        print("  • BESS Investitionskosten (€)")
        print("  • PV Investitionskosten (€)")
        print("  • Windkraft Investitionskosten (€)")
        print("  • Wasserkraft Investitionskosten (€)")
        print("  • Wärmepumpe Investitionskosten (€)")
        print("\n⚙️ Verfügbare Betriebskosten-Felder:")
        print("  • BESS Betriebskosten (€/Jahr)")
        print("  • PV Betriebskosten (€/Jahr)")
        print("  • Windkraft Betriebskosten (€/Jahr)")
        print("  • Wasserkraft Betriebskosten (€/Jahr)")
        print("  • Wärmepumpe Betriebskosten (€/Jahr)")
    else:
        print("\n💥 Migration fehlgeschlagen!") 