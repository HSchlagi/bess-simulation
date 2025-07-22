#!/usr/bin/env python3
"""
Migration-Skript: Telefonnummer-Feld zur Customer-Tabelle hinzufügen
"""

import sqlite3
import os

def add_phone_column():
    """Fügt die phone-Spalte zur customer-Tabelle hinzu"""
    
    # Datenbank-Pfad
    db_path = 'instance/bess.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Datenbank nicht gefunden: {db_path}")
        return False
    
    try:
        # Verbindung zur Datenbank
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Prüfe ob die Spalte bereits existiert
        cursor.execute("PRAGMA table_info(customer)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'phone' in columns:
            print("✅ Telefonnummer-Spalte existiert bereits")
            return True
        
        # Füge die phone-Spalte hinzu
        cursor.execute("ALTER TABLE customer ADD COLUMN phone TEXT")
        
        # Commit der Änderungen
        conn.commit()
        
        print("✅ Telefonnummer-Spalte erfolgreich hinzugefügt")
        
        # Zeige die aktualisierte Tabellenstruktur
        cursor.execute("PRAGMA table_info(customer)")
        columns = cursor.fetchall()
        print("\n📋 Aktualisierte Customer-Tabelle:")
        for column in columns:
            print(f"  - {column[1]} ({column[2]})")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Hinzufügen der Telefonnummer-Spalte: {e}")
        return False
        
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🔄 Migration: Telefonnummer-Feld hinzufügen")
    print("=" * 50)
    
    success = add_phone_column()
    
    if success:
        print("\n✅ Migration erfolgreich abgeschlossen!")
    else:
        print("\n❌ Migration fehlgeschlagen!")
        exit(1) 