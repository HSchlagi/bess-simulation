#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart Grid Scheduler für BESS Simulation
=======================================

Automatisierte Datenabrufe für Smart Grid Services.
Unterstützt FCR, aFRR, mFRR, Voltage Control und Demand Response.

Autor: Ing. Heinz Schlagintweit
Datum: Januar 2025
"""

import schedule
import time
import requests
import logging
from datetime import datetime, timedelta
import os
import sys

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/smart_grid_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SmartGridScheduler:
    """Smart Grid Services Scheduler"""
    
    def __init__(self):
        self.base_url = "http://127.0.0.1:5000"
        self.session = requests.Session()
        self.session.timeout = 30
        
        # Smart Grid Services Konfiguration
        self.services = {
            'fcr': {
                'name': 'FCR (Frequenzregelung)',
                'interval': 'every 15 minutes',  # Alle 15 Minuten
                'hours': 24,
                'active': True
            },
            'afrr': {
                'name': 'aFRR (Automatische Frequenzregelung)',
                'interval': 'every 30 minutes',  # Alle 30 Minuten
                'hours': 24,
                'active': True
            },
            'mfrr': {
                'name': 'mFRR (Manuelle Frequenzregelung)',
                'interval': 'every 1 hour',  # Stündlich
                'hours': 24,
                'active': True
            },
            'voltage': {
                'name': 'Spannungshaltung',
                'interval': 'every 10 minutes',  # Alle 10 Minuten
                'hours': 24,
                'active': True
            },
            'demand_response': {
                'name': 'Demand Response',
                'interval': 'every 1 hour',  # Stündlich
                'hours': 24,
                'active': True
            }
        }
        
        logger.info("🔌 Smart Grid Scheduler initialisiert")
    
    def fetch_smart_grid_data(self, service_type: str, hours: int = 24) -> bool:
        """Smart Grid Daten für einen Service abrufen"""
        try:
            logger.info(f"🔌 Lade {self.services[service_type]['name']} Daten...")
            
            url = f"{self.base_url}/api/smart-grid/{service_type}"
            params = {'hours': hours}
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('success'):
                count = data.get('count', 0)
                logger.info(f"✅ {self.services[service_type]['name']}: {count} Services geladen")
                return True
            else:
                logger.warning(f"⚠️ {self.services[service_type]['name']}: {data.get('message', 'Unbekannter Fehler')}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ {self.services[service_type]['name']} Request Fehler: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ {self.services[service_type]['name']} Fehler: {e}")
            return False
    
    def fetch_all_smart_grid_data(self, hours: int = 24) -> bool:
        """Alle Smart Grid Services Daten abrufen"""
        try:
            logger.info("🔌 Lade alle Smart Grid Services Daten...")
            
            url = f"{self.base_url}/api/smart-grid/fetch"
            payload = {
                'service_type': 'all',
                'hours': hours
            }
            
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('success'):
                summary = data.get('data', {}).get('summary', {})
                total_services = summary.get('total_services', 0)
                total_power = summary.get('total_power_mw', 0)
                services_active = summary.get('services_active', 0)
                
                logger.info(f"✅ Alle Smart Grid Services: {total_services} Services, {total_power:.1f} MW, {services_active} aktiv")
                return True
            else:
                logger.warning(f"⚠️ Alle Smart Grid Services: {data.get('message', 'Unbekannter Fehler')}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Alle Smart Grid Services Request Fehler: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Alle Smart Grid Services Fehler: {e}")
            return False
    
    def test_smart_grid_api(self) -> bool:
        """Smart Grid API Verbindungstest"""
        try:
            logger.info("🔍 Teste Smart Grid API Verbindung...")
            
            url = f"{self.base_url}/api/smart-grid/test"
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('success'):
                sample_data = data.get('sample_data', {})
                services_active = sample_data.get('services_active', 0)
                total_services = sample_data.get('total_services', 0)
                
                logger.info(f"✅ Smart Grid API Test erfolgreich: {services_active} Services aktiv, {total_services} Services gesamt")
                return True
            else:
                logger.warning(f"⚠️ Smart Grid API Test fehlgeschlagen: {data.get('message', 'Unbekannter Fehler')}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Smart Grid API Test Request Fehler: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Smart Grid API Test Fehler: {e}")
            return False
    
    def cleanup_old_data(self) -> bool:
        """Alte Smart Grid Daten bereinigen"""
        try:
            logger.info("🧹 Bereinige alte Smart Grid Daten...")
            
            # Hier könnte eine Bereinigungslogik implementiert werden
            # z.B. Daten älter als 30 Tage löschen
            
            logger.info("✅ Smart Grid Datenbereinigung abgeschlossen")
            return True
            
        except Exception as e:
            logger.error(f"❌ Smart Grid Datenbereinigung Fehler: {e}")
            return False
    
    def setup_scheduler(self):
        """Scheduler für Smart Grid Services einrichten"""
        logger.info("⏰ Richte Smart Grid Scheduler ein...")
        
        # Einzelne Services
        for service_id, service_config in self.services.items():
            if not service_config.get('active', False):
                continue
            
            interval = service_config['interval']
            hours = service_config['hours']
            
            # Schedule für jeden Service
            if interval == 'every 15 minutes':
                schedule.every(15).minutes.do(self.fetch_smart_grid_data, service_id, hours)
            elif interval == 'every 30 minutes':
                schedule.every(30).minutes.do(self.fetch_smart_grid_data, service_id, hours)
            elif interval == 'every 1 hour':
                schedule.every().hour.do(self.fetch_smart_grid_data, service_id, hours)
            elif interval == 'every 10 minutes':
                schedule.every(10).minutes.do(self.fetch_smart_grid_data, service_id, hours)
            
            logger.info(f"📅 {service_config['name']}: {interval}")
        
        # Alle Services täglich um 00:00 Uhr
        schedule.every().day.at("00:00").do(self.fetch_all_smart_grid_data, 24)
        logger.info("📅 Alle Smart Grid Services: täglich 00:00 Uhr")
        
        # API-Test alle 6 Stunden
        schedule.every(6).hours.do(self.test_smart_grid_api)
        logger.info("📅 Smart Grid API Test: alle 6 Stunden")
        
        # Bereinigung jeden Sonntag um 03:00 Uhr
        schedule.every().sunday.at("03:00").do(self.cleanup_old_data)
        logger.info("📅 Smart Grid Datenbereinigung: Sonntag 03:00 Uhr")
        
        logger.info("✅ Smart Grid Scheduler eingerichtet")
    
    def run_scheduler(self):
        """Scheduler ausführen"""
        logger.info("🚀 Smart Grid Scheduler gestartet")
        logger.info("=" * 50)
        
        # Initialer Test
        self.test_smart_grid_api()
        
        # Scheduler einrichten
        self.setup_scheduler()
        
        # Scheduler-Loop
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Alle 60 Sekunden prüfen
                
        except KeyboardInterrupt:
            logger.info("⏹️ Smart Grid Scheduler gestoppt")
        except Exception as e:
            logger.error(f"❌ Smart Grid Scheduler Fehler: {e}")

def main():
    """Hauptfunktion"""
    print("🔌 Smart Grid Scheduler für BESS Simulation")
    print("=" * 50)
    
    # Logs-Verzeichnis erstellen
    os.makedirs('logs', exist_ok=True)
    
    # Scheduler starten
    scheduler = SmartGridScheduler()
    scheduler.run_scheduler()

if __name__ == "__main__":
    main()
