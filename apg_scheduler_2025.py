#!/usr/bin/env python3
"""
APG Scheduler für automatische 2025-Daten
Lädt täglich aktuelle österreichische Spot-Preise
"""

import schedule
import time
import sqlite3
from datetime import datetime, timedelta
import logging
import sys
import os

# Füge das Projekt-Verzeichnis zum Python-Pfad hinzu
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from awattar_data_fetcher import AWattarDataFetcher
from apg_data_fetcher import APGDataFetcher

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/apg_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class APGScheduler2025:
    """Scheduler für automatische APG-Daten für 2025"""
    
    def __init__(self):
        self.awattar_fetcher = AWattarDataFetcher()
        self.apg_fetcher = APGDataFetcher()
        self.db_path = 'instance/bess.db'
        
    def import_daily_awattar_data(self):
        """Importiert täglich aWattar-Daten (funktioniert zuverlässig)"""
        try:
            logger.info("🔄 Starte täglichen aWattar-Import...")
            
            # Hole aktuelle Marktdaten
            market_data = self.awattar_fetcher.fetch_market_data()
            
            if not market_data.get('success') or not market_data.get('data'):
                logger.error("❌ Keine aWattar-Daten verfügbar")
                return False
            
            # aWattar API gibt Daten in data.data zurück
            awattar_data = market_data['data'].get('data', [])
            
            if not awattar_data:
                logger.warning("⚠️ Leere aWattar-Daten")
                return False
            
            # Datenbank verbinden
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            imported_count = 0
            updated_count = 0
            
            for item in awattar_data:
                try:
                    timestamp = datetime.fromtimestamp(item['start_timestamp'] / 1000)
                    price = item['marketprice']
                    
                    # Prüfe ob Eintrag bereits existiert
                    cursor.execute("""
                        SELECT id FROM spot_price 
                        WHERE timestamp = ? AND source = 'aWattar (Live)'
                    """, (timestamp,))
                    
                    existing = cursor.fetchone()
                    
                    if existing:
                        # Update existierenden Eintrag
                        cursor.execute("""
                            UPDATE spot_price 
                            SET price_eur_mwh = ?, created_at = datetime('now')
                            WHERE id = ?
                        """, (price, existing[0]))
                        updated_count += 1
                    else:
                        # Neuen Eintrag erstellen
                        cursor.execute("""
                            INSERT INTO spot_price (timestamp, price_eur_mwh, source, region, price_type, created_at)
                            VALUES (?, ?, 'aWattar (Live)', 'AT', 'Day-Ahead', datetime('now'))
                        """, (timestamp, price))
                        imported_count += 1
                        
                except Exception as e:
                    logger.error(f"⚠️ Fehler bei Datenpunkt {item}: {e}")
                    continue
            
            # Commit Änderungen
            conn.commit()
            conn.close()
            
            logger.info(f"✅ aWattar-Import abgeschlossen: {imported_count} neue, {updated_count} aktualisierte Einträge")
            return True
            
        except Exception as e:
            logger.error(f"❌ Fehler beim aWattar-Import: {e}")
            return False
    
    def import_daily_apg_data(self):
        """Importiert täglich APG-Daten (Fallback)"""
        try:
            logger.info("🔄 Starte täglichen APG-Import...")
            
            # Versuche APG-Daten zu laden
            apg_data = self.apg_fetcher.fetch_current_prices()
            
            if not apg_data:
                logger.warning("⚠️ Keine APG-Daten verfügbar, verwende realistische Demo-Daten")
                return self.import_realistic_demo_data()
            
            # Datenbank verbinden
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            imported_count = 0
            
            for price_entry in apg_data:
                try:
                    timestamp = datetime.fromisoformat(price_entry['timestamp'])
                    price = price_entry['price']
                    source = price_entry.get('source', 'APG (Live)')
                    
                    # Prüfe ob Eintrag bereits existiert
                    cursor.execute("""
                        SELECT id FROM spot_price 
                        WHERE timestamp = ? AND source = ?
                    """, (timestamp, source))
                    
                    existing = cursor.fetchone()
                    
                    if not existing:
                        # Neuen Eintrag erstellen
                        cursor.execute("""
                            INSERT INTO spot_price (timestamp, price_eur_mwh, source, region, price_type, created_at)
                            VALUES (?, ?, ?, 'AT', 'Day-Ahead', datetime('now'))
                        """, (timestamp, price, source))
                        imported_count += 1
                        
                except Exception as e:
                    logger.error(f"⚠️ Fehler bei APG-Datenpunkt {price_entry}: {e}")
                    continue
            
            # Commit Änderungen
            conn.commit()
            conn.close()
            
            logger.info(f"✅ APG-Import abgeschlossen: {imported_count} neue Einträge")
            return True
            
        except Exception as e:
            logger.error(f"❌ Fehler beim APG-Import: {e}")
            return False
    
    def import_realistic_demo_data(self):
        """Importiert realistische Demo-Daten basierend auf 2024-Mustern"""
        try:
            logger.info("🔄 Generiere realistische Demo-Daten für 2025...")
            
            import random
            from datetime import datetime, timedelta
            
            # Datenbank verbinden
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Generiere 7 Tage realistische Preise
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            prices = []
            
            for day in range(7):
                current_date = start_date + timedelta(days=day)
                
                for hour in range(24):
                    # Realistische österreichische Strompreis-Muster (2025)
                    base_price = 50  # Basis-Preis
                    
                    # Tageszeit-Schwankungen (höher am Tag, niedriger nachts)
                    if 6 <= hour <= 22:  # Tag
                        time_factor = 1.2 + 0.3 * (hour - 6) / 16
                    else:  # Nacht
                        time_factor = 0.6 + 0.2 * (hour / 6)
                    
                    # Wochentag-Schwankungen
                    weekday = current_date.weekday()
                    if weekday < 5:  # Werktag
                        weekday_factor = 1.1
                    else:  # Wochenende
                        weekday_factor = 0.9
                    
                    # Zufällige Schwankungen
                    random_factor = random.uniform(0.8, 1.3)
                    
                    # Finaler Preis
                    final_price = base_price * time_factor * weekday_factor * random_factor
                    final_price = max(10, min(150, final_price))  # Realistische Grenzen
                    
                    timestamp = current_date.replace(hour=hour)
                    
                    # Prüfe ob Eintrag bereits existiert
                    cursor.execute("""
                        SELECT id FROM spot_price 
                        WHERE timestamp = ? AND source = 'Demo (2025-Muster)'
                    """, (timestamp,))
                    
                    existing = cursor.fetchone()
                    
                    if not existing:
                        cursor.execute("""
                            INSERT INTO spot_price (timestamp, price_eur_mwh, source, region, price_type, created_at)
                            VALUES (?, ?, 'Demo (2025-Muster)', 'AT', 'Day-Ahead', datetime('now'))
                        """, (timestamp, round(final_price, 2)))
                        prices.append({
                            'timestamp': timestamp,
                            'price': round(final_price, 2)
                        })
            
            # Commit Änderungen
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Demo-Daten generiert: {len(prices)} Einträge")
            return True
            
        except Exception as e:
            logger.error(f"❌ Fehler beim Generieren der Demo-Daten: {e}")
            return False
    
    def cleanup_old_data(self):
        """Löscht alte Daten (älter als 30 Tage)"""
        try:
            logger.info("🧹 Starte Bereinigung alter Daten...")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Lösche Daten älter als 30 Tage
            cutoff_date = datetime.now() - timedelta(days=30)
            cursor.execute("""
                DELETE FROM spot_price 
                WHERE timestamp < ? AND source LIKE '%Demo%'
            """, (cutoff_date,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Bereinigung abgeschlossen: {deleted_count} alte Einträge gelöscht")
            return True
            
        except Exception as e:
            logger.error(f"❌ Fehler bei der Bereinigung: {e}")
            return False
    
    def get_database_stats(self):
        """Zeigt Datenbank-Statistiken"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Gesamtstatistiken
            cursor.execute("SELECT COUNT(*) FROM spot_price")
            total_count = cursor.fetchone()[0]
            
            # Statistiken nach Quelle
            cursor.execute("""
                SELECT source, COUNT(*) as count, 
                       AVG(price_eur_mwh) as avg_price,
                       MAX(price_eur_mwh) as max_price,
                       MIN(price_eur_mwh) as min_price
                FROM spot_price 
                GROUP BY source
                ORDER BY count DESC
            """)
            
            sources = cursor.fetchall()
            
            # 2025-Daten
            cursor.execute("SELECT COUNT(*) FROM spot_price WHERE timestamp LIKE '2025%'")
            count_2025 = cursor.fetchone()[0]
            
            conn.close()
            
            logger.info("📊 DATENBANK-STATISTIKEN:")
            logger.info(f"   Gesamte Einträge: {total_count}")
            logger.info(f"   2025-Daten: {count_2025}")
            logger.info("   Nach Quelle:")
            for source, count, avg_price, max_price, min_price in sources:
                logger.info(f"     {source}: {count} Einträge, Ø {avg_price:.2f} €/MWh ({min_price:.2f}-{max_price:.2f})")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Fehler bei Statistiken: {e}")
            return False

def main():
    """Hauptfunktion - Startet den Scheduler"""
    logger.info("🚀 APG Scheduler 2025 gestartet...")
    
    scheduler = APGScheduler2025()
    
    # Zeige aktuelle Statistiken
    scheduler.get_database_stats()
    
    # Scheduler-Jobs definieren
    schedule.every().day.at("13:00").do(scheduler.import_daily_awattar_data)  # 13:00 Uhr
    schedule.every().day.at("14:00").do(scheduler.import_daily_apg_data)      # 14:00 Uhr (Fallback)
    schedule.every().day.at("15:00").do(scheduler.cleanup_old_data)           # 15:00 Uhr
    schedule.every().day.at("16:00").do(scheduler.get_database_stats)         # 16:00 Uhr
    
    # Sofortiger Test-Import
    logger.info("🔄 Führe sofortigen Test-Import durch...")
    scheduler.import_daily_awattar_data()
    
    logger.info("⏰ Scheduler läuft... (Strg+C zum Beenden)")
    logger.info("📅 Geplante Jobs:")
    logger.info("   13:00 - aWattar-Import")
    logger.info("   14:00 - APG-Import (Fallback)")
    logger.info("   15:00 - Datenbereinigung")
    logger.info("   16:00 - Statistiken")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Prüfe jede Minute
    except KeyboardInterrupt:
        logger.info("🛑 Scheduler gestoppt")

if __name__ == "__main__":
    main()

