#!/usr/bin/env python3
"""
Hinzufügen der fehlenden Kunden
"""

import sqlite3

def add_missing_customers():
    """Fügt die fehlenden Kunden hinzu"""
    
    try:
        conn = sqlite3.connect('instance/bess.db')
        cursor = conn.cursor()
        
        # Prüfe welche Kunden bereits existieren
        cursor.execute("SELECT name FROM customer")
        existing_customers = [row[0] for row in cursor.fetchall()]
        
        print("Bestehende Kunden:", existing_customers)
        
        # Fehlende Kunden hinzufügen
        missing_customers = [
            ("Dr. Manuel Pfeil", "Pfeil Energieberatung"),
            # Weitere Kunden können hier hinzugefügt werden
        ]
        
        for name, company in missing_customers:
            if name not in existing_customers:
                cursor.execute(
                    "INSERT INTO customer (name, company) VALUES (?, ?)",
                    (name, company)
                )
                print(f"✅ Kunde hinzugefügt: {name} ({company})")
            else:
                print(f"ℹ️ Kunde bereits vorhanden: {name}")
        
        conn.commit()
        
        # Alle Kunden anzeigen
        cursor.execute("SELECT * FROM customer")
        customers = cursor.fetchall()
        print(f"\n📋 Alle Kunden ({len(customers)}):")
        for customer in customers:
            print(f"   - {customer[1]} ({customer[2]})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Fehler: {e}")

if __name__ == "__main__":
    add_missing_customers()
