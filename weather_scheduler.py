#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wetterdaten-Scheduler für BESS Simulation
========================================

Automatischer Scheduler für Wetterdaten-Import von OpenWeatherMap und PVGIS.
Führt regelmäßige Imports für PV-Prognosen und BESS-Simulationen durch.

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

# Weather API Fetcher importieren
from weather_api_fetcher import WeatherAPIFetcher

class WeatherScheduler:
    """Hauptklasse für Wetterdaten-Scheduler"""
    
    def __init__(self):
        self.fetcher = WeatherAPIFetcher()
        self.locations = self.load_locations()
        self.last_run = {}
        
        logger.info("🌤️ Wetterdaten-Scheduler initialisiert")
    
    def load_locations(self):
        """Lade konfigurierte Standorte für Wetterdaten-Import"""
        # Standard-Standorte für Österreich
        default_locations = [
            {
                'name': 'Wien',
                'latitude': 48.2082,
                'longitude': 16.3738,
                'priority': 'high'
            },
            {
                'name': 'Salzburg',
                'latitude': 47.8095,
                'longitude': 13.0550,
                'priority': 'medium'
            },
            {
                'name': 'Graz',
                'latitude': 47.0707,
                'longitude': 15.4395,
                'priority': 'medium'
            },
            {
                'name': 'Linz',
                'latitude': 48.3069,
                'longitude': 14.2858,
                'priority': 'medium'
            },
            {
                'name': 'Innsbruck',
                'latitude': 47.2692,
                'longitude': 11.4041,
                'priority': 'low'
            }
        ]
        
        # Versuche Standorte aus Konfigurationsdatei zu laden
        config_file = 'weather_locations.json'
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    custom_locations = json.load(f)
                    logger.info(f"📁 {len(custom_locations)} Standorte aus {config_file} geladen")
                    return custom_locations
            except Exception as e:
                logger.warning(f"⚠️ Fehler beim Laden der Standorte: {e}")
        
        logger.info(f"📁 {len(default_locations)} Standard-Standorte geladen")
        return default_locations
    
    def save_locations(self):
        """Speichere Standorte in Konfigurationsdatei"""
        config_file = 'weather_locations.json'
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.locations, f, indent=2, ensure_ascii=False)
            logger.info(f"💾 Standorte in {config_file} gespeichert")
        except Exception as e:
            logger.error(f"❌ Fehler beim Speichern der Standorte: {e}")
    
    def import_current_weather(self):
        """Importiere aktuelle Wetterdaten für alle Standorte"""
        logger.info("🌤️ Starte aktuellen Wetterdaten-Import...")
        
        success_count = 0
        error_count = 0
        
        for location in self.locations:
            try:
                logger.info(f"📍 Importiere Wetterdaten für {location['name']}")
                
                weather_data = self.fetcher.get_weather_for_location(
                    location['latitude'],
                    location['longitude'],
                    location['name']
                )
                
                if weather_data['status'] == 'success':
                    success_count += 1
                    logger.info(f"✅ {location['name']}: {weather_data['current']['temperature']}°C")
                else:
                    error_count += 1
                    logger.warning(f"⚠️ {location['name']}: {weather_data.get('message', 'Unbekannter Fehler')}")
                
                # Rate Limiting
                time.sleep(1)
                
            except Exception as e:
                error_count += 1
                logger.error(f"❌ {location['name']}: {e}")
        
        logger.info(f"🌤️ Aktueller Import abgeschlossen: {success_count} erfolgreich, {error_count} Fehler")
        return success_count, error_count
    
    def import_forecast_weather(self):
        """Importiere Wettervorhersage für alle Standorte"""
        logger.info("🔮 Starte Wettervorhersage-Import...")
        
        success_count = 0
        error_count = 0
        
        for location in self.locations:
            try:
                logger.info(f"📍 Importiere Vorhersage für {location['name']}")
                
                forecast_data = self.fetcher.get_openweather_forecast(
                    location['latitude'],
                    location['longitude'],
                    5  # 5 Tage Vorhersage
                )
                
                if forecast_data:
                    success_count += 1
                    logger.info(f"✅ {location['name']}: {len(forecast_data)} Vorhersage-Datenpunkte")
                else:
                    error_count += 1
                    logger.warning(f"⚠️ {location['name']}: Keine Vorhersage-Daten")
                
                # Rate Limiting
                time.sleep(1)
                
            except Exception as e:
                error_count += 1
                logger.error(f"❌ {location['name']}: {e}")
        
        logger.info(f"🔮 Vorhersage-Import abgeschlossen: {success_count} erfolgreich, {error_count} Fehler")
        return success_count, error_count
    
    def import_historical_weather(self):
        """Importiere historische Wetterdaten für alle Standorte"""
        logger.info("📊 Starte historischen Wetterdaten-Import...")
        
        success_count = 0
        error_count = 0
        
        # Letzte 7 Tage
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y%m%d')
        
        for location in self.locations:
            try:
                logger.info(f"📍 Importiere historische Daten für {location['name']}")
                
                historical_data = self.fetcher.get_pvgis_weather(
                    location['latitude'],
                    location['longitude'],
                    start_date,
                    end_date
                )
                
                if historical_data:
                    success_count += 1
                    logger.info(f"✅ {location['name']}: {len(historical_data)} historische Datenpunkte")
                else:
                    error_count += 1
                    logger.warning(f"⚠️ {location['name']}: Keine historischen Daten")
                
                # Rate Limiting
                time.sleep(2)  # PVGIS ist langsamer
                
            except Exception as e:
                error_count += 1
                logger.error(f"❌ {location['name']}: {e}")
        
        logger.info(f"📊 Historischer Import abgeschlossen: {success_count} erfolgreich, {error_count} Fehler")
        return success_count, error_count
    
    def health_check(self):
        """Gesundheitscheck der Wetter-APIs"""
        logger.info("🔍 Führe Wetter-API Gesundheitscheck durch...")
        
        try:
            test_result = self.fetcher.test_api_connection()
            
            if test_result['overall'] == 'success':
                logger.info("✅ Wetter-APIs funktionieren korrekt")
            elif test_result['overall'] == 'partial':
                logger.warning("⚠️ Wetter-APIs teilweise verfügbar")
            else:
                logger.error("❌ Wetter-APIs nicht verfügbar")
            
            # Detaillierte API-Status
            for api_name, api_status in test_result.items():
                if api_name != 'overall':
                    status_icon = "✅" if api_status['status'] == 'success' else "❌"
                    logger.info(f"  {status_icon} {api_name}: {api_status['message']}")
            
            return test_result['overall'] == 'success'
            
        except Exception as e:
            logger.error(f"❌ Gesundheitscheck fehlgeschlagen: {e}")
            return False
    
    def cleanup_old_data(self):
        """Bereinige alte Wetterdaten (älter als 30 Tage)"""
        logger.info("🧹 Starte Bereinigung alter Wetterdaten...")
        
        # Hier würde normalerweise die Datenbank-Bereinigung stattfinden
        # Für jetzt nur Logging
        logger.info("🧹 Bereinigung abgeschlossen (Demo-Modus)")
        return True
    
    def setup_schedule(self):
        """Konfiguriere den Zeitplan für automatische Imports"""
        logger.info("⏰ Konfiguriere Wetterdaten-Zeitplan...")
        
        # Aktuelle Wetterdaten - alle 3 Stunden
        schedule.every(3).hours.do(self.import_current_weather)
        
        # Wettervorhersage - täglich um 06:00 Uhr
        schedule.every().day.at("06:00").do(self.import_forecast_weather)
        
        # Historische Daten - täglich um 02:00 Uhr
        schedule.every().day.at("02:00").do(self.import_historical_weather)
        
        # Gesundheitscheck - alle 6 Stunden
        schedule.every(6).hours.do(self.health_check)
        
        # Bereinigung - wöchentlich am Sonntag um 03:00 Uhr
        schedule.every().sunday.at("03:00").do(self.cleanup_old_data)
        
        logger.info("⏰ Zeitplan konfiguriert:")
        logger.info("  - Aktuelle Wetterdaten: alle 3 Stunden")
        logger.info("  - Wettervorhersage: täglich 06:00 Uhr")
        logger.info("  - Historische Daten: täglich 02:00 Uhr")
        logger.info("  - Gesundheitscheck: alle 6 Stunden")
        logger.info("  - Bereinigung: Sonntag 03:00 Uhr")
    
    def run_scheduler(self):
        """Starte den Scheduler"""
        logger.info("🚀 Wetterdaten-Scheduler gestartet")
        
        # Ersten Import sofort durchführen
        logger.info("🌤️ Führe ersten Import durch...")
        self.import_current_weather()
        
        # Scheduler-Loop
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Prüfe jede Minute
                
        except KeyboardInterrupt:
            logger.info("⏹️ Wetterdaten-Scheduler gestoppt")
        except Exception as e:
            logger.error(f"❌ Scheduler-Fehler: {e}")

def main():
    """Hauptfunktion"""
    print("🌤️ Wetterdaten-Scheduler für BESS Simulation")
    print("=" * 50)
    
    scheduler = WeatherScheduler()
    
    # Zeitplan konfigurieren
    scheduler.setup_schedule()
    
    # Gesundheitscheck durchführen
    if scheduler.health_check():
        print("✅ Wetter-APIs verfügbar - Scheduler startet")
    else:
        print("⚠️ Wetter-APIs teilweise nicht verfügbar - Scheduler startet trotzdem")
    
    # Scheduler starten
    scheduler.run_scheduler()

if __name__ == "__main__":
    main()
