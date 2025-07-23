#!/usr/bin/env python3
"""
APG 2024 Daten Import - Echte österreichische Spot-Preise für 2024
"""

import sqlite3
from datetime import datetime, timedelta
import sys
import os

# Füge das Projekt-Verzeichnis zum Python-Pfad hinzu
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from apg_data_fetcher import APGDataFetcher

def import_apg_data_2024():
    """Importiert echte APG-Daten für 2024 in die Datenbank"""
    
    print("🚀 APG 2024 Daten Import gestartet...")
    print("=" * 50)
    
    try:
        # APG Data Fetcher initialisieren
        fetcher = APGDataFetcher()
        
        # Versuche echte APG-Daten zu laden
        print("🌐 Versuche echte APG-Daten für 2024 zu laden...")
        apg_data = fetcher.fetch_historical_data_2024()
        
        if not apg_data:
            print("❌ Keine APG-Daten verfügbar")
            return False
        
        print(f"📊 {len(apg_data)} APG-Datenpunkte geladen")
        
        # Datenbank verbinden
        conn = sqlite3.connect('instance/bess.db')
        cursor = conn.cursor()
        
        # Prüfe ob Spot-Preis-Tabelle existiert
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS spot_price (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                price_eur_mwh FLOAT NOT NULL,
                source VARCHAR(50) DEFAULT 'APG',
                region VARCHAR(50) DEFAULT 'AT',
                price_type VARCHAR(20) DEFAULT 'Day-Ahead',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Lösche alte Demo-Daten (optional)
        print("🧹 Lösche alte Demo-Daten...")
        cursor.execute("DELETE FROM spot_price WHERE source LIKE '%Demo%'")
        deleted_count = cursor.rowcount
        print(f"✅ {deleted_count} alte Demo-Daten gelöscht")
        
        # Importiere neue APG-Daten
        print("📥 Importiere APG-Daten in Datenbank...")
        
        imported_count = 0
        skipped_count = 0
        
        for price_entry in apg_data:
            try:
                timestamp = datetime.fromisoformat(price_entry['timestamp'])
                price = price_entry['price']
                source = price_entry.get('source', 'APG')
                market = price_entry.get('market', 'Day-Ahead')
                region = price_entry.get('region', 'AT')
                
                # Prüfe ob Eintrag bereits existiert
                cursor.execute("""
                    SELECT id FROM spot_price 
                    WHERE timestamp = ? AND source = ?
                """, (timestamp, source))
                
                existing = cursor.fetchone()
                
                if existing:
                    # Update existierenden Eintrag
                    cursor.execute("""
                        UPDATE spot_price 
                        SET price_eur_mwh = ?, price_type = ?, region = ?, created_at = datetime('now')
                        WHERE id = ?
                    """, (price, market, region, existing[0]))
                    skipped_count += 1
                else:
                    # Neuen Eintrag erstellen
                    cursor.execute("""
                        INSERT INTO spot_price (timestamp, price_eur_mwh, source, region, price_type, created_at)
                        VALUES (?, ?, ?, ?, ?, datetime('now'))
                    """, (timestamp, price, source, region, market))
                    imported_count += 1
                
            except Exception as e:
                print(f"⚠️ Fehler bei Datenpunkt {price_entry}: {e}")
                continue
        
        # Commit Änderungen
        conn.commit()
        
        # Statistiken anzeigen
        print("=" * 50)
        print("📊 IMPORT-STATISTIKEN:")
        print(f"✅ Neue Datenpunkte importiert: {imported_count}")
        print(f"🔄 Bestehende Datenpunkte aktualisiert: {skipped_count}")
        print(f"📈 Gesamte Datenpunkte in Datenbank: {imported_count + skipped_count}")
        
        # Überprüfe die Datenbank
        cursor.execute("SELECT COUNT(*) FROM spot_price")
        total_count = cursor.fetchone()[0]
        print(f"📊 Gesamte Spot-Preise in Datenbank: {total_count}")
        
        # Zeige Preis-Statistiken
        cursor.execute("""
            SELECT 
                AVG(price_eur_mwh) as avg_price,
                MAX(price_eur_mwh) as max_price,
                MIN(price_eur_mwh) as min_price,
                COUNT(*) as count
            FROM spot_price
        """)
        
        stats = cursor.fetchone()
        if stats:
            print(f"📊 Preis-Statistiken:")
            print(f"   Durchschnitt: {stats[0]:.2f} €/MWh")
            print(f"   Maximum: {stats[1]:.2f} €/MWh")
            print(f"   Minimum: {stats[2]:.2f} €/MWh")
            print(f"   Anzahl: {stats[3]} Datenpunkte")
        
        conn.close()
        
        print("=" * 50)
        print("🎉 APG 2024 Daten Import erfolgreich abgeschlossen!")
        print("🔍 Überprüfen Sie jetzt die Spot-Preise-Seite!")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Import: {e}")
        return False

def show_database_stats():
    """Zeigt Statistiken der Spot-Preis-Datenbank"""
    
    try:
        conn = sqlite3.connect('instance/bess.db')
        cursor = conn.cursor()
        
        print("📊 SPOT-PREIS DATENBANK STATISTIKEN:")
        print("=" * 40)
        
        # Gesamte Anzahl
        cursor.execute("SELECT COUNT(*) FROM spot_price")
        total = cursor.fetchone()[0]
        print(f"📈 Gesamte Datenpunkte: {total}")
        
        # Nach Quelle gruppiert
        cursor.execute("""
            SELECT source, COUNT(*) as count, 
                   AVG(price_eur_mwh) as avg_price,
                   MAX(price_eur_mwh) as max_price,
                   MIN(price_eur_mwh) as min_price
            FROM spot_price 
            GROUP BY source
        """)
        
        sources = cursor.fetchall()
        for source, count, avg_price, max_price, min_price in sources:
            print(f"📊 {source}:")
            print(f"   Anzahl: {count}")
            print(f"   Durchschnitt: {avg_price:.2f} €/MWh")
            print(f"   Maximum: {max_price:.2f} €/MWh")
            print(f"   Minimum: {min_price:.2f} €/MWh")
        
        # Zeitraum
        cursor.execute("""
            SELECT MIN(timestamp), MAX(timestamp) FROM spot_price
        """)
        
        time_range = cursor.fetchone()
        if time_range[0] and time_range[1]:
            print(f"📅 Zeitraum: {time_range[0]} bis {time_range[1]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Fehler beim Abrufen der Statistiken: {e}")

if __name__ == "__main__":
    print("🇦🇹 APG 2024 Daten Import Tool")
    print("=" * 50)
    
    # Import durchführen
    success = import_apg_data_2024()
    
    if success:
        print("\n📊 Datenbank-Statistiken:")
        show_database_stats()
    else:
        print("\n❌ Import fehlgeschlagen") 