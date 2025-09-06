#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
aWattar Scheduler für BESS Simulation
Automatischer Import von österreichischen Strompreisen
"""

import schedule
import time
import logging
from datetime import datetime, timedelta
from typing import Optional
import sys
import os

# Flask App Context für Datenbankzugriff
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
    handlers=[
        logging.FileHandler('logs/awattar_scheduler.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class AWattarScheduler:
    """Scheduler für automatischen aWattar-Datenimport"""
    
    def __init__(self):
        self.fetcher = None
        self.app = None
        self.is_running = False
        self.last_run = None
        self.error_count = 0
        self.max_errors = 5
        
    def initialize(self):
        """Initialisiert den Scheduler mit Flask App Context"""
        try:
            from app import create_app
            from awattar_data_fetcher import awattar_fetcher
            
            self.app = create_app()
            self.fetcher = awattar_fetcher
            
            logger.info("aWattar Scheduler erfolgreich initialisiert")
            return True
            
        except Exception as e:
            logger.error(f"Fehler bei der Initialisierung: {e}")
            return False
    
    def import_daily_prices(self):
        """Importiert die Preise für den nächsten Tag (aWattar übermittelt um 14:00 für nächsten Tag)"""
        if not self.app or not self.fetcher:
            logger.error("Scheduler nicht initialisiert")
            return False
        
        try:
            with self.app.app_context():
                # aWattar übermittelt um 14:00 die Preise für den nächsten Tag
                # Daher importieren wir morgen und übermorgen
                tomorrow = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
                day_after_tomorrow = tomorrow + timedelta(days=1)
                
                logger.info(f"Starte täglichen Import für {tomorrow.date()} (nächster Tag)")
                
                result = self.fetcher.fetch_and_save(
                    start_date=tomorrow,
                    end_date=day_after_tomorrow
                )
                
                if result['success']:
                    saved_count = result['save_result']['saved_count']
                    logger.info(f"Täglicher Import erfolgreich: {saved_count} Preise für {tomorrow.date()} importiert")
                    self.error_count = 0  # Reset error counter
                    self.last_run = datetime.now()
                    return True
                else:
                    logger.error(f"Täglicher Import fehlgeschlagen: {result['error']}")
                    self.error_count += 1
                    return False
                    
        except Exception as e:
            logger.error(f"Fehler beim täglichen Import: {e}")
            self.error_count += 1
            return False
    
    def import_today_prices(self):
        """Importiert die Preise für den aktuellen Tag (falls noch nicht vorhanden)"""
        if not self.app or not self.fetcher:
            logger.error("Scheduler nicht initialisiert")
            return False
        
        try:
            with self.app.app_context():
                # Heute als Zeitraum
                today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                tomorrow = today + timedelta(days=1)
                
                logger.info(f"Starte Import für {today.date()} (aktueller Tag)")
                
                result = self.fetcher.fetch_and_save(
                    start_date=today,
                    end_date=tomorrow
                )
                
                if result['success']:
                    saved_count = result['save_result']['saved_count']
                    logger.info(f"Import für heute erfolgreich: {saved_count} Preise für {today.date()} importiert")
                    return True
                else:
                    logger.error(f"Import für heute fehlgeschlagen: {result['error']}")
                    return False
                    
        except Exception as e:
            logger.error(f"Fehler beim Import für heute: {e}")
            return False
    
    def import_historical_prices(self, days_back: int = 7):
        """Importiert historische Preise für die letzten N Tage"""
        if not self.app or not self.fetcher:
            logger.error("Scheduler nicht initialisiert")
            return False
        
        try:
            with self.app.app_context():
                end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                start_date = end_date - timedelta(days=days_back)
                
                logger.info(f"Starte historischen Import für {days_back} Tage")
                
                result = self.fetcher.fetch_and_save(
                    start_date=start_date,
                    end_date=end_date
                )
                
                if result['success']:
                    saved_count = result['save_result']['saved_count']
                    logger.info(f"Historischer Import erfolgreich: {saved_count} Preise importiert")
                    return True
                else:
                    logger.error(f"Historischer Import fehlgeschlagen: {result['error']}")
                    return False
                    
        except Exception as e:
            logger.error(f"Fehler beim historischen Import: {e}")
            return False
    
    def cleanup_old_data(self, days_to_keep: int = 30):
        """Löscht alte aWattar-Daten (älter als N Tage)"""
        if not self.app:
            logger.error("Scheduler nicht initialisiert")
            return False
        
        try:
            with self.app.app_context():
                from models import db, SpotPrice
                
                cutoff_date = datetime.now() - timedelta(days=days_to_keep)
                
                # Alte aWattar-Daten löschen
                deleted_count = SpotPrice.query.filter(
                    SpotPrice.source == 'aWATTAR',
                    SpotPrice.timestamp < cutoff_date
                ).delete()
                
                db.session.commit()
                
                logger.info(f"Cleanup abgeschlossen: {deleted_count} alte Datensätze gelöscht")
                return True
                
        except Exception as e:
            logger.error(f"Fehler beim Cleanup: {e}")
            return False
    
    def health_check(self):
        """Führt einen Health Check der aWattar-Integration durch"""
        if not self.app or not self.fetcher:
            logger.error("Scheduler nicht initialisiert")
            return False
        
        try:
            with self.app.app_context():
                # API-Test
                api_response = self.fetcher.fetch_market_data()
                
                if not api_response['success']:
                    logger.warning(f"Health Check: API-Verbindung fehlgeschlagen - {api_response['error']}")
                    return False
                
                # Datenbank-Test
                from models import SpotPrice
                latest_price = SpotPrice.query.filter(
                    SpotPrice.source == 'aWATTAR'
                ).order_by(SpotPrice.timestamp.desc()).first()
                
                if not latest_price:
                    logger.warning("Health Check: Keine aWattar-Daten in der Datenbank")
                    return False
                
                # Prüfe ob letzter Preis nicht zu alt ist (max. 2 Tage)
                if latest_price.timestamp < datetime.now() - timedelta(days=2):
                    logger.warning(f"Health Check: Letzter Preis zu alt - {latest_price.timestamp}")
                    return False
                
                logger.info("Health Check erfolgreich")
                return True
                
        except Exception as e:
            logger.error(f"Fehler beim Health Check: {e}")
            return False
    
    def setup_schedule(self):
        """Konfiguriert den automatischen Zeitplan"""
        if not self.initialize():
            return False
        
        # Täglicher Import um 14:00 Uhr (für nächsten Tag nach Day-Ahead-Markt)
        schedule.every().day.at("14:00").do(self.import_daily_prices)
        
        # Zusätzlicher Import um 15:00 Uhr (für aktuellen Tag, falls noch nicht vorhanden)
        schedule.every().day.at("15:00").do(self.import_today_prices)
        
        # Wöchentlicher historischer Import (Sonntag um 16:00)
        schedule.every().sunday.at("16:00").do(self.import_historical_prices, days_back=7)
        
        # Wöchentlicher Cleanup (Sonntag um 16:00)
        schedule.every().sunday.at("16:00").do(self.cleanup_old_data, days_to_keep=30)
        
        # Stündlicher Health Check
        schedule.every().hour.do(self.health_check)
        
        logger.info("Zeitplan konfiguriert:")
        logger.info("  - Täglicher Import: 14:00 Uhr (für nächsten Tag)")
        logger.info("  - Zusätzlicher Import: 15:00 Uhr (für aktuellen Tag)")
        logger.info("  - Wöchentlicher historischer Import: Sonntag 16:00 Uhr")
        logger.info("  - Wöchentlicher Cleanup: Sonntag 16:00 Uhr")
        logger.info("  - Stündlicher Health Check")
        
        return True
    
    def run(self):
        """Startet den Scheduler"""
        if not self.setup_schedule():
            logger.error("Scheduler konnte nicht gestartet werden")
            return
        
        self.is_running = True
        logger.info("aWattar Scheduler gestartet")
        
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
                # Stoppe bei zu vielen Fehlern
                if self.error_count >= self.max_errors:
                    logger.error(f"Scheduler gestoppt nach {self.max_errors} Fehlern")
                    break
                    
        except KeyboardInterrupt:
            logger.info("Scheduler durch Benutzer gestoppt")
        except Exception as e:
            logger.error(f"Unerwarteter Fehler im Scheduler: {e}")
        finally:
            self.is_running = False
            logger.info("aWattar Scheduler beendet")
    
    def stop(self):
        """Stoppt den Scheduler"""
        self.is_running = False
        logger.info("Scheduler-Stop angefordert")
    
    def get_status(self):
        """Gibt den aktuellen Status des Schedulers zurück"""
        return {
            'is_running': self.is_running,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'error_count': self.error_count,
            'max_errors': self.max_errors,
            'next_jobs': [str(job) for job in schedule.jobs]
        }


def main():
    """Hauptfunktion für direkten Aufruf"""
    print("aWattar Scheduler für BESS Simulation")
    print("=====================================")
    
    scheduler = AWattarScheduler()
    
    try:
        scheduler.run()
    except KeyboardInterrupt:
        print("\nScheduler wird beendet...")
        scheduler.stop()


if __name__ == "__main__":
    main()
