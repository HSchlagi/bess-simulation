#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migration: Bezugsjahr (reference_year) zu MarketPriceConfig hinzufügen
"""

import sqlite3
import os
from datetime import datetime

def add_reference_year_column():
    """Fügt reference_year Spalte zur market_price_config Tabelle hinzu"""
    db_path = 'instance/bess.db'
    
    if not os.path.exists(db_path):
        print(f"[FEHLER] Datenbank nicht gefunden: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Prüfe ob Spalte bereits existiert
        cursor.execute("PRAGMA table_info(market_price_config)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'reference_year' in columns:
            print("[OK] Spalte 'reference_year' existiert bereits")
            conn.close()
            return True
        
        # Füge Spalte hinzu
        cursor.execute("""
            ALTER TABLE market_price_config
            ADD COLUMN reference_year INTEGER DEFAULT NULL
        """)
        
        # Setze Standardwert auf aktuelles Jahr für bestehende Einträge
        current_year = datetime.now().year
        cursor.execute("""
            UPDATE market_price_config
            SET reference_year = ?
            WHERE reference_year IS NULL
        """, (current_year,))
        
        conn.commit()
        print(f"[OK] Spalte 'reference_year' erfolgreich hinzugefügt (Standard: {current_year})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"[FEHLER] Fehler beim Hinzufügen der Spalte: {e}")
        conn.rollback()
        conn.close()
        return False

if __name__ == '__main__':
    print("Starte Migration: Bezugsjahr hinzufuegen...")
    if add_reference_year_column():
        print("[OK] Migration erfolgreich abgeschlossen!")
    else:
        print("[FEHLER] Migration fehlgeschlagen!")

