#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migration-Script für Marktpreis-Konfiguration
Erstellt die market_price_config Tabelle
"""

import sqlite3
import os
from datetime import datetime

def create_market_price_config_table():
    """Erstellt die market_price_config Tabelle in der SQLite-Datenbank"""
    db_path = 'instance/bess.db'
    
    if not os.path.exists(db_path):
        print(f"[FEHLER] Datenbank nicht gefunden: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Prüfen ob Tabelle bereits existiert
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='market_price_config'
        """)
        
        if cursor.fetchone():
            print("[OK] Tabelle 'market_price_config' existiert bereits")
            conn.close()
            return True
        
        # MarketPriceConfig Tabelle erstellen
        cursor.execute('''
            CREATE TABLE market_price_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                spot_arbitrage_price FLOAT,
                intraday_trading_price FLOAT,
                balancing_energy_price FLOAT,
                frequency_regulation_price FLOAT,
                capacity_market_price FLOAT,
                flexibility_market_price FLOAT,
                name VARCHAR(100),
                description TEXT,
                is_default BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES project (id)
            )
        ''')
        
        # Index für Performance
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_market_price_config_project 
            ON market_price_config(project_id)
        ''')
        
        conn.commit()
        print("[OK] Tabelle 'market_price_config' erfolgreich erstellt")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"[FEHLER] Fehler beim Erstellen der Tabelle: {e}")
        conn.rollback()
        conn.close()
        return False

if __name__ == '__main__':
    print("Starte Migration fuer Marktpreis-Konfiguration...")
    if create_market_price_config_table():
        print("[OK] Migration erfolgreich abgeschlossen!")
    else:
        print("[FEHLER] Migration fehlgeschlagen!")

