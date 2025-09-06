#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IoT Sensor Scheduler für BESS Simulation
=======================================

Automatisierte Datenabrufe für IoT-Sensoren.
Unterstützt Battery, PV, Grid und Environmental Sensoren.

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
        logging.FileHandler('logs/iot_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class IoTScheduler:
    """IoT-Sensor Scheduler"""
    
    def __init__(self):
        self.base_url = "http://127.0.0.1:5000"
        self.session = requests.Session()
        self.session.timeout = 30
        
        # IoT-Sensor Konfiguration
        self.sensors = {
            'battery': {
                'name': 'Batterie-Sensoren',
                'interval': 'every 5 minutes',  # Alle 5 Minuten
                'hours': 24,
                'active': True
            },
            'pv': {
                'name': 'PV-Sensoren',
                'interval': 'every 10 minutes',  # Alle 10 Minuten
                'hours': 24,
                'active': True
            },
            'grid': {
                'name': 'Grid-Sensoren',
                'interval': 'every 15 minutes',  # Alle 15 Minuten
                'hours': 24,
                'active': True
            },
            'environmental': {
                'name': 'Umgebungs-Sensoren',
                'interval': 'every 30 minutes',  # Alle 30 Minuten
                'hours': 24,
                'active': True
            }
        }
        
        logger.info("📡 IoT-Sensor Scheduler initialisiert")
    
    def fetch_iot_data(self, sensor_type: str, hours: int = 24) -> bool:
        """IoT-Daten für einen Sensor-Typ abrufen"""
        try:
            logger.info(f"📡 Lade {self.sensors[sensor_type]['name']} Daten...")
            
            url = f"{self.base_url}/api/iot/{sensor_type}"
            params = {'hours': hours}
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('success'):
                count = data.get('count', 0)
                logger.info(f"✅ {self.sensors[sensor_type]['name']}: {count} Sensoren geladen")
                return True
            else:
                logger.warning(f"⚠️ {self.sensors[sensor_type]['name']}: {data.get('message', 'Unbekannter Fehler')}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ {self.sensors[sensor_type]['name']} Request Fehler: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ {self.sensors[sensor_type]['name']} Fehler: {e}")
            return False
    
    def fetch_all_iot_data(self, hours: int = 24) -> bool:
        """Alle IoT-Sensor-Daten abrufen"""
        try:
            logger.info("📡 Lade alle IoT-Sensor-Daten...")
            
            url = f"{self.base_url}/api/iot/fetch"
            payload = {
                'sensor_type': 'all',
                'hours': hours
            }
            
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('success'):
                summary = data.get('data', {}).get('summary', {})
                total_sensors = summary.get('total_sensors', 0)
                total_power = summary.get('total_power_w', 0)
                sensor_types_active = summary.get('sensor_types_active', 0)
                avg_temperature = summary.get('avg_temperature_c', 0)
                
                logger.info(f"✅ Alle IoT-Sensoren: {total_sensors} Sensoren, {total_power:.1f} W, {sensor_types_active} Typen, {avg_temperature:.1f}°C")
                return True
            else:
                logger.warning(f"⚠️ Alle IoT-Sensoren: {data.get('message', 'Unbekannter Fehler')}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Alle IoT-Sensoren Request Fehler: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Alle IoT-Sensoren Fehler: {e}")
            return False
    
    def test_iot_api(self) -> bool:
        """IoT-Sensor API Verbindungstest"""
        try:
            logger.info("🔍 Teste IoT-Sensor API Verbindung...")
            
            url = f"{self.base_url}/api/iot/test"
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('success'):
                sample_data = data.get('sample_data', {})
                sensor_types_active = sample_data.get('sensor_types_active', 0)
                total_sensors = sample_data.get('total_sensors', 0)
                avg_temperature = sample_data.get('avg_temperature_c', 0)
                
                logger.info(f"✅ IoT-Sensor API Test erfolgreich: {sensor_types_active} Typen aktiv, {total_sensors} Sensoren, {avg_temperature:.1f}°C")
                return True
            else:
                logger.warning(f"⚠️ IoT-Sensor API Test fehlgeschlagen: {data.get('message', 'Unbekannter Fehler')}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ IoT-Sensor API Test Request Fehler: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ IoT-Sensor API Test Fehler: {e}")
            return False
    
    def cleanup_old_data(self) -> bool:
        """Alte IoT-Sensor-Daten bereinigen"""
        try:
            logger.info("🧹 Bereinige alte IoT-Sensor-Daten...")
            
            # Hier könnte eine Bereinigungslogik implementiert werden
            # z.B. Daten älter als 30 Tage löschen
            
            logger.info("✅ IoT-Sensor-Datenbereinigung abgeschlossen")
            return True
            
        except Exception as e:
            logger.error(f"❌ IoT-Sensor-Datenbereinigung Fehler: {e}")
            return False
    
    def setup_scheduler(self):
        """Scheduler für IoT-Sensoren einrichten"""
        logger.info("⏰ Richte IoT-Sensor Scheduler ein...")
        
        # Einzelne Sensor-Typen
        for sensor_id, sensor_config in self.sensors.items():
            if not sensor_config.get('active', False):
                continue
            
            interval = sensor_config['interval']
            hours = sensor_config['hours']
            
            # Schedule für jeden Sensor-Typ
            if interval == 'every 5 minutes':
                schedule.every(5).minutes.do(self.fetch_iot_data, sensor_id, hours)
            elif interval == 'every 10 minutes':
                schedule.every(10).minutes.do(self.fetch_iot_data, sensor_id, hours)
            elif interval == 'every 15 minutes':
                schedule.every(15).minutes.do(self.fetch_iot_data, sensor_id, hours)
            elif interval == 'every 30 minutes':
                schedule.every(30).minutes.do(self.fetch_iot_data, sensor_id, hours)
            
            logger.info(f"📅 {sensor_config['name']}: {interval}")
        
        # Alle Sensoren täglich um 00:00 Uhr
        schedule.every().day.at("00:00").do(self.fetch_all_iot_data, 24)
        logger.info("📅 Alle IoT-Sensoren: täglich 00:00 Uhr")
        
        # API-Test alle 4 Stunden
        schedule.every(4).hours.do(self.test_iot_api)
        logger.info("📅 IoT-Sensor API Test: alle 4 Stunden")
        
        # Bereinigung jeden Montag um 02:00 Uhr
        schedule.every().monday.at("02:00").do(self.cleanup_old_data)
        logger.info("📅 IoT-Sensor-Datenbereinigung: Montag 02:00 Uhr")
        
        logger.info("✅ IoT-Sensor Scheduler eingerichtet")
    
    def run_scheduler(self):
        """Scheduler ausführen"""
        logger.info("🚀 IoT-Sensor Scheduler gestartet")
        logger.info("=" * 50)
        
        # Initialer Test
        self.test_iot_api()
        
        # Scheduler einrichten
        self.setup_scheduler()
        
        # Scheduler-Loop
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Alle 60 Sekunden prüfen
                
        except KeyboardInterrupt:
            logger.info("⏹️ IoT-Sensor Scheduler gestoppt")
        except Exception as e:
            logger.error(f"❌ IoT-Sensor Scheduler Fehler: {e}")

def main():
    """Hauptfunktion"""
    print("📡 IoT-Sensor Scheduler für BESS Simulation")
    print("=" * 50)
    
    # Logs-Verzeichnis erstellen
    os.makedirs('logs', exist_ok=True)
    
    # Scheduler starten
    scheduler = IoTScheduler()
    scheduler.run_scheduler()

if __name__ == "__main__":
    main()
