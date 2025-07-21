#!/usr/bin/env python3
"""
Skript zum Hinzufügen der neuen Spalten für sonstige Kosten zur Project-Tabelle
"""

import sqlite3
import os

def add_other_costs_columns():
    """Fügt die neuen Spalten für sonstige Kosten zur Project-Tabelle hinzu"""
    
    # Pfad zur Datenbank
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'bess.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Datenbank nicht gefunden: {db_path}")
        return False
    
    try:
        # Verbindung zur Datenbank herstellen
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Überprüfe bestehende Spalten...")
        
        # Überprüfe ob die Spalten bereits existieren
        cursor.execute("PRAGMA table_info(project)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"Bestehende Spalten: {columns}")
        
        # Füge sonstige Investitionskosten hinzu
        if 'other_investment' not in columns:
            print("➕ Füge Spalte 'other_investment' hinzu...")
            cursor.execute("ALTER TABLE project ADD COLUMN other_investment REAL")
            print("✅ Spalte 'other_investment' hinzugefügt")
        else:
            print("ℹ️ Spalte 'other_investment' existiert bereits")
        
        # Füge sonstige Betriebskosten hinzu
        if 'other_operation_cost' not in columns:
            print("➕ Füge Spalte 'other_operation_cost' hinzu...")
            cursor.execute("ALTER TABLE project ADD COLUMN other_operation_cost REAL")
            print("✅ Spalte 'other_operation_cost' hinzugefügt")
        else:
            print("ℹ️ Spalte 'other_operation_cost' existiert bereits")
        
        # Änderungen speichern
        conn.commit()
        
        # Überprüfe die finale Tabellenstruktur
        cursor.execute("PRAGMA table_info(project)")
        final_columns = [column[1] for column in cursor.fetchall()]
        print(f"📋 Finale Spalten: {final_columns}")
        
        conn.close()
        print("🎉 Datenbank-Migration erfolgreich abgeschlossen!")
        return True
        
    except Exception as e:
        print(f"❌ Fehler bei der Datenbank-Migration: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starte Datenbank-Migration für sonstige Kosten...")
    success = add_other_costs_columns()
    
    if success:
        print("✅ Migration erfolgreich!")
    else:
        print("❌ Migration fehlgeschlagen!") 