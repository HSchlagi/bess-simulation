"""
MQTT Bridge für Live BESS Daten
Direkte MQTT-Verbindung zu BESS-Speichersystemen
"""

import paho.mqtt.client as mqtt
import json
import sqlite3
import threading
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Callable
import os

logger = logging.getLogger(__name__)

class BESSMQTTBridge:
    """MQTT Bridge für Live BESS-Daten"""
    
    def __init__(self):
        self.client = None
        self.connected = False
        self.subscribed_topics = set()
        self.data_callbacks = []
        self.db_path = os.getenv('LIVE_BESS_DB_PATH', 'live/data/bess.db')
        
        # MQTT Konfiguration
        self.broker_host = os.getenv('MQTT_BROKER_HOST', 'localhost')
        self.broker_port = int(os.getenv('MQTT_BROKER_PORT', '1883'))
        self.username = os.getenv('MQTT_USERNAME', 'bessuser')
        self.password = os.getenv('MQTT_PASSWORD', 'besspass')
        
        # Topic-Konfiguration
        self.base_topic = os.getenv('MQTT_BASE_TOPIC', 'bess')
        self.telemetry_topic = f"{self.base_topic}/+/+/telemetry"
        
        # Initialisiere Datenbank
        self.init_database()
        
    def init_database(self):
        """Initialisiert die SQLite-Datenbank für Live-Daten"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS live_bess_telemetry (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    site TEXT NOT NULL,
                    device TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    soc REAL,
                    power REAL,
                    power_charge REAL,
                    power_discharge REAL,
                    voltage_dc REAL,
                    current_dc REAL,
                    temperature_max REAL,
                    soh REAL,
                    alarms TEXT,
                    raw_data TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Index für bessere Performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_site_device_timestamp 
                ON live_bess_telemetry(site, device, timestamp)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_created_at 
                ON live_bess_telemetry(created_at)
            """)
            
            conn.commit()
            conn.close()
            
            logger.info(f"Live BESS Datenbank initialisiert: {self.db_path}")
            
        except Exception as e:
            logger.error(f"Fehler bei Datenbankinitialisierung: {e}")
    
    def add_data_callback(self, callback: Callable):
        """Fügt einen Callback für neue Daten hinzu"""
        self.data_callbacks.append(callback)
    
    def remove_data_callback(self, callback: Callable):
        """Entfernt einen Daten-Callback"""
        if callback in self.data_callbacks:
            self.data_callbacks.remove(callback)
    
    def on_connect(self, client, userdata, flags, rc):
        """MQTT Verbindungs-Callback"""
        if rc == 0:
            self.connected = True
            logger.info("MQTT-Bridge erfolgreich verbunden")
            
            # Subscribiere zu Telemetrie-Topics
            self.subscribe_to_telemetry()
            
        else:
            self.connected = False
            logger.error(f"MQTT-Verbindung fehlgeschlagen: {rc}")
    
    def on_disconnect(self, client, userdata, rc):
        """MQTT Disconnect-Callback"""
        self.connected = False
        logger.warning(f"MQTT-Verbindung getrennt: {rc}")
    
    def on_message(self, client, userdata, msg):
        """MQTT Nachrichten-Callback"""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
            # Parse Topic: bess/site1/bess1/telemetry
            topic_parts = topic.split('/')
            if len(topic_parts) >= 4:
                site = topic_parts[1]
                device = topic_parts[2]
                message_type = topic_parts[3]
                
                if message_type == 'telemetry':
                    self.process_telemetry_message(site, device, payload)
                    
        except Exception as e:
            logger.error(f"Fehler beim Verarbeiten der MQTT-Nachricht: {e}")
    
    def process_telemetry_message(self, site: str, device: str, payload: str):
        """Verarbeitet Telemetrie-Nachrichten"""
        try:
            data = json.loads(payload)
            
            # Validiere und normalisiere Daten
            telemetry_data = self.normalize_telemetry_data(site, device, data)
            
            # Speichere in Datenbank
            self.save_telemetry_to_db(telemetry_data)
            
            # Benachrichtige Callbacks
            for callback in self.data_callbacks:
                try:
                    callback(telemetry_data)
                except Exception as e:
                    logger.error(f"Fehler in Daten-Callback: {e}")
                    
            logger.debug(f"Telemetrie verarbeitet: {site}/{device}")
            
        except Exception as e:
            logger.error(f"Fehler beim Verarbeiten der Telemetrie: {e}")
    
    def normalize_telemetry_data(self, site: str, device: str, data: Dict) -> Dict:
        """Normalisiert Telemetrie-Daten"""
        timestamp = data.get('ts', datetime.now().isoformat())
        
        return {
            'site': site,
            'device': device,
            'timestamp': timestamp,
            'soc': float(data.get('soc', 0)) if data.get('soc') is not None else None,
            'power': float(data.get('p', 0)) if data.get('p') is not None else None,
            'power_charge': float(data.get('p_ch', 0)) if data.get('p_ch') is not None else None,
            'power_discharge': float(data.get('p_dis', 0)) if data.get('p_dis') is not None else None,
            'voltage_dc': float(data.get('v_dc', 0)) if data.get('v_dc') is not None else None,
            'current_dc': float(data.get('i_dc', 0)) if data.get('i_dc') is not None else None,
            'temperature_max': float(data.get('t_cell_max', 0)) if data.get('t_cell_max') is not None else None,
            'soh': float(data.get('soh', 0)) if data.get('soh') is not None else None,
            'alarms': json.dumps(data.get('alarms', [])),
            'raw_data': json.dumps(data)
        }
    
    def save_telemetry_to_db(self, data: Dict):
        """Speichert Telemetrie-Daten in der Datenbank"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO live_bess_telemetry 
                (site, device, timestamp, soc, power, power_charge, power_discharge,
                 voltage_dc, current_dc, temperature_max, soh, alarms, raw_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data['site'], data['device'], data['timestamp'],
                data['soc'], data['power'], data['power_charge'], data['power_discharge'],
                data['voltage_dc'], data['current_dc'], data['temperature_max'],
                data['soh'], data['alarms'], data['raw_data']
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Fehler beim Speichern in Datenbank: {e}")
    
    def subscribe_to_telemetry(self):
        """Subscribiert zu Telemetrie-Topics"""
        try:
            self.client.subscribe(self.telemetry_topic, qos=1)
            self.subscribed_topics.add(self.telemetry_topic)
            logger.info(f"Subscribed zu: {self.telemetry_topic}")
            
        except Exception as e:
            logger.error(f"Fehler beim Subscribieren: {e}")
    
    def connect(self):
        """Stellt MQTT-Verbindung her"""
        try:
            self.client = mqtt.Client()
            self.client.username_pw_set(self.username, self.password)
            
            self.client.on_connect = self.on_connect
            self.client.on_disconnect = self.on_disconnect
            self.client.on_message = self.on_message
            
            self.client.connect(self.broker_host, self.broker_port, 60)
            
            # Starte MQTT-Loop in separatem Thread
            mqtt_thread = threading.Thread(target=self.client.loop_forever, daemon=True)
            mqtt_thread.start()
            
            logger.info(f"MQTT-Bridge gestartet: {self.broker_host}:{self.broker_port}")
            
        except Exception as e:
            logger.error(f"Fehler beim MQTT-Verbindungsaufbau: {e}")
            self.connected = False
    
    def disconnect(self):
        """Trennt MQTT-Verbindung"""
        try:
            if self.client and self.connected:
                self.client.disconnect()
                self.connected = False
                logger.info("MQTT-Verbindung getrennt")
                
        except Exception as e:
            logger.error(f"Fehler beim MQTT-Trennen: {e}")
    
    def get_latest_data(self, site: str = None, device: str = None, limit: int = 10) -> List[Dict]:
        """Holt die neuesten Daten aus der lokalen Datenbank"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = """
                SELECT * FROM live_bess_telemetry 
                WHERE 1=1
            """
            params = []
            
            if site:
                query += " AND site = ?"
                params.append(site)
            
            if device:
                query += " AND device = ?"
                params.append(device)
            
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Konvertiere zu Dict-Liste
            data = []
            for row in rows:
                data.append(dict(row))
            
            conn.close()
            return data
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Daten: {e}")
            return []
    
    def get_statistics(self, site: str = None, device: str = None, hours: int = 24) -> Dict:
        """Berechnet Statistiken für die letzten X Stunden"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    COUNT(*) as total_records,
                    AVG(soc) as avg_soc,
                    MIN(soc) as min_soc,
                    MAX(soc) as max_soc,
                    AVG(power) as avg_power,
                    MIN(power) as min_power,
                    MAX(power) as max_power,
                    AVG(voltage_dc) as avg_voltage,
                    MIN(voltage_dc) as min_voltage,
                    MAX(voltage_dc) as max_voltage,
                    AVG(temperature_max) as avg_temp,
                    MIN(temperature_max) as min_temp,
                    MAX(temperature_max) as max_temp
                FROM live_bess_telemetry 
                WHERE created_at >= datetime('now', '-{} hours')
            """.format(hours)
            
            params = []
            if site:
                query += " AND site = ?"
                params.append(site)
            
            if device:
                query += " AND device = ?"
                params.append(device)
            
            cursor.execute(query, params)
            row = cursor.fetchone()
            
            if row:
                stats = {
                    'total_records': row[0],
                    'soc': {'avg': row[1], 'min': row[2], 'max': row[3]},
                    'power': {'avg': row[4], 'min': row[5], 'max': row[6]},
                    'voltage': {'avg': row[7], 'min': row[8], 'max': row[9]},
                    'temperature': {'avg': row[10], 'min': row[11], 'max': row[12]}
                }
            else:
                stats = {}
            
            conn.close()
            return stats
            
        except Exception as e:
            logger.error(f"Fehler bei Statistik-Berechnung: {e}")
            return {}

# Globale MQTT-Bridge Instanz
mqtt_bridge = BESSMQTTBridge()
