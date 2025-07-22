#!/usr/bin/env python3
import sqlite3
import os

# Pfad zur Datenbank
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'bess.db')

print("=== DATENBANK-STRUKTUR ===")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Tabellen-Struktur anzeigen
    cursor.execute("PRAGMA table_info(project)")
    columns = cursor.fetchall()
    
    print("\n--- SPALTEN-REIHENFOLGE ---")
    for i, col in enumerate(columns):
        print(f"{i}: {col[1]} ({col[2]})")
    
    # Aktuelle Werte anzeigen
    print("\n--- AKTUELLE WERTE ---")
    cursor.execute("SELECT * FROM project WHERE id = 1")
    project = cursor.fetchone()
    
    if project:
        for i, value in enumerate(project):
            print(f"{i}: {value}")
    
except Exception as e:
    print(f"Fehler: {e}")
finally:
    if conn:
        conn.close() 