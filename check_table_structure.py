#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

def check_table_structure():
    """Prüft die Struktur der Tabellen"""
    
    db_path = 'instance/bess.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Datenbank nicht gefunden: {db_path}")
        return
    
    print(f"✅ Datenbank gefunden: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Tabellen auflisten
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"\n📋 Tabellen-Struktur:")
        for table in tables:
            table_name = table[0]
            print(f"\n🔍 Tabelle: {table_name}")
            
            # Spalten der Tabelle anzeigen
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            for col in columns:
                col_id, col_name, col_type, not_null, default_val, pk = col
                print(f"  - {col_name} ({col_type}) {'NOT NULL' if not_null else 'NULL'} {'PK' if pk else ''}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Fehler beim Prüfen der Tabellen-Struktur: {e}")

if __name__ == "__main__":
    check_table_structure() 