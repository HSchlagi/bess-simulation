#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ENTSO-E Scheduler für BESS Simulation
====================================

Automatischer Scheduler für ENTSO-E Marktdaten-Import.
Führt regelmäßige Imports für europäische Strommarkt-Daten durch.

Autor: Ing. Heinz Schlagintweit
Datum: Januar 2025
"""

import schedule
import time
import logging
import sys
import os
from datetime import datetime, timedelta
import json

# BESS-Simulation Module importieren
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)-15s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# ENTSO-E API Fetcher importieren
from entsoe_api_fetcher import ENTSOEAPIFetcher

class ENTSOEScheduler:
    """Hauptklasse für ENTSO-E Scheduler"""
    
    def __init__(self):
        self.fetcher = ENTSOEAPIFetcher()
        self.countries = self.load_countries()
        self.last_run = {}
        
        logger.info("🌍 ENTSO-E Scheduler initialisiert")
    
    def load_countries(self):
        """Lade konfigurierte Länder für ENTSO-E Import"""
        # Standard-Länder für europäische Märkte
        default_countries = [
            {
                'code': 'AT',
                'name': 'Austria',
                'priority': 'high'
            },
            {
                'code': 'DE',
                'name': 'Germany',
                'priority': 'high'
            },
            {
                'code': 'CH',
                'name': 'Switzerland',
                'priority': 'medium'
            },
            {
                'code': 'IT',
                'name': 'Italy',
                'priority': 'medium'
            },
            {
                'code': 'CZ',
                'name': 'Czech Republic',
                'priority': 'low'
            },
            {
                'code': 'SK',
                'name': 'Slovakia',
                'priority': 'low'
            }
        ]
        
        # Versuche Länder aus Konfigurationsdatei zu laden
        config_file = 'entsoe_countries.json'
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    custom_countries = json.load(f)
                    logger.info(f"📁 {len(custom_countries)} Länder aus {config_file} geladen")
                    return custom_countries
            except Exception as e:
                logger.warning(f"⚠️ Fehler beim Laden der Länder: {e}")
        
        logger.info(f"📁 {len(default_countries)} Standard-Länder geladen")
        return default_countries
    
    def save_countries(self):
        """Speichere Länder in Konfigurationsdatei"""
        config_file = 'entsoe_countries.json'
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.countries, f, indent=2, ensure_ascii=False)
            logger.info(f"💾 Länder in {config_file} gespeichert")
        except Exception as e:
            logger.error(f"❌ Fehler beim Speichern der Länder: {e}")
    
    def import_day_ahead_prices(self):
        """Importiere Day-Ahead Preise für alle Länder"""
        logger.info("🌍 Starte Day-Ahead Preise Import...")
        
        success_count = 0
        error_count = 0
        
        for country in self.countries:
            try:
                logger.info(f"📍 Importiere Day-Ahead Preise für {country['name']} ({country['code']})")
                
                prices = self.fetcher.get_day_ahead_prices(country['code'])
                
                if prices:
                    success_count += 1
                    latest_price = prices[-1].price_eur_mwh if prices else 0
                    logger.info(f"✅ {country['name']}: {len(prices)} Preise, neuester: {latest_price} €/MWh")
                else:
                    error_count += 1
                    logger.warning(f"⚠️ {country['name']}: Keine Day-Ahead Preise")
                
                # Rate Limiting
                time.sleep(2)
                
            except Exception as e:
                error_count += 1
                logger.error(f"❌ {country['name']}: {e}")
        
        logger.info(f"🌍 Day-Ahead Import abgeschlossen: {success_count} erfolgreich, {error_count} Fehler")
        return success_count, error_count
    
    def import_intraday_prices(self):
        """Importiere Intraday Preise für alle Länder"""
        logger.info("⚡ Starte Intraday Preise Import...")
        
        success_count = 0
        error_count = 0
        
        for country in self.countries:
            try:
                logger.info(f"📍 Importiere Intraday Preise für {country['name']} ({country['code']})")
                
                prices = self.fetcher.get_intraday_prices(country['code'])
                
                if prices:
                    success_count += 1
                    latest_price = prices[-1].price_eur_mwh if prices else 0
                    logger.info(f"✅ {country['name']}: {len(prices)} Preise, neuester: {latest_price} €/MWh")
                else:
                    error_count += 1
                    logger.warning(f"⚠️ {country['name']}: Keine Intraday Preise")
                
                # Rate Limiting
                time.sleep(2)
                
            except Exception as e:
                error_count += 1
                logger.error(f"❌ {country['name']}: {e}")
        
        logger.info(f"⚡ Intraday Import abgeschlossen: {success_count} erfolgreich, {error_count} Fehler")
        return success_count, error_count
    
    def import_generation_data(self):
        """Importiere Generation-Daten für alle Länder"""
        logger.info("🏭 Starte Generation-Daten Import...")
        
        success_count = 0
        error_count = 0
        
        for country in self.countries:
            try:
                logger.info(f"📍 Importiere Generation-Daten für {country['name']} ({country['code']})")
                
                generation = self.fetcher.get_generation_data(country['code'])
                
                if generation:
                    success_count += 1
                    latest_generation = generation[-1].price_eur_mwh if generation else 0
                    logger.info(f"✅ {country['name']}: {len(generation)} Datenpunkte, neueste: {latest_generation} MW")
                else:
                    error_count += 1
                    logger.warning(f"⚠️ {country['name']}: Keine Generation-Daten")
                
                # Rate Limiting
                time.sleep(3)  # Generation-Daten sind größer
                
            except Exception as e:
                error_count += 1
                logger.error(f"❌ {country['name']}: {e}")
        
        logger.info(f"🏭 Generation Import abgeschlossen: {success_count} erfolgreich, {error_count} Fehler")
        return success_count, error_count
    
    def health_check(self):
        """Gesundheitscheck der ENTSO-E API"""
        logger.info("🔍 Führe ENTSO-E API Gesundheitscheck durch...")
        
        try:
            test_result = self.fetcher.test_api_connection()
            
            if test_result['status'] == 'success':
                logger.info("✅ ENTSO-E API funktioniert korrekt")
            elif test_result['status'] == 'demo':
                logger.warning("⚠️ ENTSO-E API im Demo-Modus")
            else:
                logger.error("❌ ENTSO-E API nicht verfügbar")
            
            logger.info(f"  Status: {test_result['status']}")
            logger.info(f"  Message: {test_result['message']}")
            
            return test_result['status'] in ['success', 'demo']
            
        except Exception as e:
            logger.error(f"❌ Gesundheitscheck fehlgeschlagen: {e}")
            return False
    
    def cleanup_old_data(self):
        """Bereinige alte ENTSO-E Daten (älter als 30 Tage)"""
        logger.info("🧹 Starte Bereinigung alter ENTSO-E Daten...")
        
        # Hier würde normalerweise die Datenbank-Bereinigung stattfinden
        # Für jetzt nur Logging
        logger.info("🧹 Bereinigung abgeschlossen (Demo-Modus)")
        return True
    
    def setup_schedule(self):
        """Konfiguriere den Zeitplan für automatische Imports"""
        logger.info("⏰ Konfiguriere ENTSO-E Zeitplan...")
        
        # Day-Ahead Preise - täglich um 13:00 Uhr (nach Auktion)
        schedule.every().day.at("13:00").do(self.import_day_ahead_prices)
        
        # Intraday Preise - alle 4 Stunden
        schedule.every(4).hours.do(self.import_intraday_prices)
        
        # Generation-Daten - täglich um 06:00 Uhr
        schedule.every().day.at("06:00").do(self.import_generation_data)
        
        # Gesundheitscheck - alle 8 Stunden
        schedule.every(8).hours.do(self.health_check)
        
        # Bereinigung - wöchentlich am Montag um 02:00 Uhr
        schedule.every().monday.at("02:00").do(self.cleanup_old_data)
        
        logger.info("⏰ ENTSO-E Zeitplan konfiguriert:")
        logger.info("  - Day-Ahead Preise: täglich 13:00 Uhr")
        logger.info("  - Intraday Preise: alle 4 Stunden")
        logger.info("  - Generation-Daten: täglich 06:00 Uhr")
        logger.info("  - Gesundheitscheck: alle 8 Stunden")
        logger.info("  - Bereinigung: Montag 02:00 Uhr")
    
    def run_scheduler(self):
        """Starte den Scheduler"""
        logger.info("🚀 ENTSO-E Scheduler gestartet")
        
        # Ersten Import sofort durchführen
        logger.info("🌍 Führe ersten Import durch...")
        self.import_day_ahead_prices()
        
        # Scheduler-Loop
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Prüfe jede Minute
                
        except KeyboardInterrupt:
            logger.info("⏹️ ENTSO-E Scheduler gestoppt")
        except Exception as e:
            logger.error(f"❌ Scheduler-Fehler: {e}")

def main():
    """Hauptfunktion"""
    print("🌍 ENTSO-E Scheduler für BESS Simulation")
    print("=" * 50)
    
    scheduler = ENTSOEScheduler()
    
    # Zeitplan konfigurieren
    scheduler.setup_schedule()
    
    # Gesundheitscheck durchführen
    if scheduler.health_check():
        print("✅ ENTSO-E API verfügbar - Scheduler startet")
    else:
        print("⚠️ ENTSO-E API teilweise nicht verfügbar - Scheduler startet trotzdem")
    
    # Scheduler starten
    scheduler.run_scheduler()

if __name__ == "__main__":
    main()
