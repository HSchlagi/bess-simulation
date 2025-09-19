"""
Live BESS Daten Service
Integriert echte BESS-Speicherdaten über FastAPI/MQTT
"""

import requests
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import os
import logging

logger = logging.getLogger(__name__)

# MQTT Bridge importieren (optional)
try:
    from .mqtt_bridge import mqtt_bridge
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False
    logger.warning("MQTT Bridge nicht verfügbar")

class LiveBESSDataService:
    """Service für Live BESS-Daten Integration"""
    
    def __init__(self):
        self.fastapi_url = os.getenv('LIVE_BESS_API_URL', 'http://localhost:8080')
        self.api_token = os.getenv('LIVE_BESS_API_TOKEN', 'changeme_token_123')
        self.timeout = 5  # 5 Sekunden Timeout
        
        # MQTT-Integration
        self.use_mqtt = os.getenv('USE_MQTT_BRIDGE', 'false').lower() == 'true'
        self.mqtt_connected = False
        
        if self.use_mqtt and MQTT_AVAILABLE:
            self.init_mqtt_bridge()
    
    def init_mqtt_bridge(self):
        """Initialisiert die MQTT-Bridge"""
        try:
            # Callback für neue Daten registrieren
            mqtt_bridge.add_data_callback(self.on_new_mqtt_data)
            
            # MQTT-Verbindung herstellen
            mqtt_bridge.connect()
            
            # Prüfe Verbindungsstatus nach kurzer Wartezeit
            import time
            time.sleep(2)
            self.mqtt_connected = mqtt_bridge.connected
            
            logger.info(f"MQTT-Bridge initialisiert: {'Verbunden' if self.mqtt_connected else 'Nicht verbunden'}")
            
        except Exception as e:
            logger.error(f"Fehler bei MQTT-Bridge Initialisierung: {e}")
            self.mqtt_connected = False
    
    def on_new_mqtt_data(self, data: Dict):
        """Callback für neue MQTT-Daten"""
        logger.debug(f"Neue MQTT-Daten erhalten: {data.get('site')}/{data.get('device')}")
    
    def get_live_data(self, limit: int = 10) -> List[Dict]:
        """Holt die neuesten Live-Daten (MQTT oder FastAPI)"""
        
        # Priorisiere MQTT-Daten falls verfügbar
        if self.use_mqtt and self.mqtt_connected and MQTT_AVAILABLE:
            return self.get_mqtt_data(limit=limit)
        else:
            return self.get_fastapi_data(limit=limit)
    
    def get_mqtt_data(self, limit: int = 10) -> List[Dict]:
        """Holt Daten direkt von der MQTT-Bridge"""
        try:
            data = mqtt_bridge.get_latest_data(limit=limit)
            
            # Konvertiere MQTT-Datenformat zu FastAPI-Format
            converted_data = []
            for row in data:
                converted_data.append({
                    'site': row['site'],
                    'device': row['device'],
                    'ts': row['timestamp'],
                    'soc': row['soc'],
                    'p': row['power'],
                    'p_ch': row['power_charge'],
                    'p_dis': row['power_discharge'],
                    'v_dc': row['voltage_dc'],
                    'i_dc': row['current_dc'],
                    't_cell_max': row['temperature_max'],
                    'soh': row['soh'],
                    'alarms': json.loads(row['alarms']) if row['alarms'] else []
                })
            
            logger.info(f"MQTT-Daten abgerufen: {len(converted_data)} Datensätze")
            return converted_data
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der MQTT-Daten: {e}")
            # Fallback zu FastAPI
            return self.get_fastapi_data(limit=limit)
    
    def get_fastapi_data(self, limit: int = 10) -> List[Dict]:
        """Holt die neuesten Live-Daten vom FastAPI Service"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_token}',
                'Content-Type': 'application/json'
            }
            
            url = f"{self.fastapi_url}/api/last"
            params = {'limit': limit}
            
            response = requests.get(url, headers=headers, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"FastAPI-Daten erfolgreich abgerufen: {len(data)} Datensätze")
                return data
            else:
                logger.warning(f"API-Fehler: {response.status_code} - {response.text}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Verbindungsfehler zu Live-BESS API: {e}")
            return []
        except Exception as e:
            logger.error(f"Unerwarteter Fehler beim Abrufen der FastAPI-Daten: {e}")
            return []
    
    def get_system_status(self) -> Dict[str, Any]:
        """Prüft den Status des Live-Systems (MQTT + FastAPI)"""
        status_info = {
            'last_check': datetime.now().isoformat(),
            'data_source': 'unknown'
        }
        
        # MQTT-Status prüfen
        if self.use_mqtt and MQTT_AVAILABLE:
            mqtt_status = {
                'mqtt_available': True,
                'mqtt_connected': self.mqtt_connected,
                'broker_host': mqtt_bridge.broker_host,
                'broker_port': mqtt_bridge.broker_port
            }
            status_info.update(mqtt_status)
            
            if self.mqtt_connected:
                status_info['status'] = 'online'
                status_info['data_source'] = 'mqtt'
                return status_info
        
        # Fallback zu FastAPI
        try:
            headers = {
                'Authorization': f'Bearer {self.api_token}',
                'Content-Type': 'application/json'
            }
            
            url = f"{self.fastapi_url}/healthz"
            response = requests.get(url, headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                status_info.update({
                    'status': 'online',
                    'data_source': 'fastapi',
                    'api_url': self.fastapi_url,
                    'mqtt_available': MQTT_AVAILABLE,
                    'mqtt_connected': self.mqtt_connected if self.use_mqtt else False
                })
                return status_info
            else:
                status_info.update({
                    'status': 'error',
                    'error_code': response.status_code,
                    'data_source': 'fastapi',
                    'api_url': self.fastapi_url
                })
                return status_info
                
        except requests.exceptions.RequestException as e:
            status_info.update({
                'status': 'offline',
                'error': str(e),
                'data_source': 'fastapi',
                'api_url': self.fastapi_url,
                'mqtt_available': MQTT_AVAILABLE,
                'mqtt_connected': self.mqtt_connected if self.use_mqtt else False
            })
            return status_info
    
    def get_device_summary(self, site: str = None, device: str = None) -> Dict[str, Any]:
        """Holt eine Zusammenfassung der Gerätedaten"""
        try:
            data = self.get_live_data(limit=100)
            
            if not data:
                return {'error': 'Keine Daten verfügbar'}
            
            # Filtere nach Site/Device falls angegeben
            if site:
                data = [d for d in data if d.get('site') == site]
            if device:
                data = [d for d in data if d.get('device') == device]
            
            if not data:
                return {'error': 'Keine Daten für die angegebenen Parameter'}
            
            # Berechne Statistiken
            soc_values = [float(d.get('soc', 0)) for d in data if d.get('soc') is not None]
            power_values = [float(d.get('p', 0)) for d in data if d.get('p') is not None]
            voltage_values = [float(d.get('v_dc', 0)) for d in data if d.get('v_dc') is not None]
            
            summary = {
                'total_records': len(data),
                'date_range': {
                    'oldest': data[-1].get('ts') if data else None,
                    'newest': data[0].get('ts') if data else None
                },
                'soc_stats': {
                    'current': soc_values[0] if soc_values else None,
                    'min': min(soc_values) if soc_values else None,
                    'max': max(soc_values) if soc_values else None,
                    'avg': sum(soc_values) / len(soc_values) if soc_values else None
                },
                'power_stats': {
                    'current': power_values[0] if power_values else None,
                    'min': min(power_values) if power_values else None,
                    'max': max(power_values) if power_values else None,
                    'avg': sum(power_values) / len(power_values) if power_values else None
                },
                'voltage_stats': {
                    'current': voltage_values[0] if voltage_values else None,
                    'min': min(voltage_values) if voltage_values else None,
                    'max': max(voltage_values) if voltage_values else None,
                    'avg': sum(voltage_values) / len(voltage_values) if voltage_values else None
                },
                'devices': list(set([d.get('device') for d in data if d.get('device')])),
                'sites': list(set([d.get('site') for d in data if d.get('site')]))
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Fehler beim Erstellen der Gerätezusammenfassung: {e}")
            return {'error': str(e)}
    
    def get_chart_data(self, hours: int = 24) -> Dict[str, Any]:
        """Holt Daten für Charts (letzte X Stunden)"""
        try:
            # Hole mehr Daten für Chart-Zeitraum
            data = self.get_live_data(limit=hours * 4)  # Annahme: alle 15 Min ein Datensatz
            
            if not data:
                return {'error': 'Keine Daten verfügbar'}
            
            # Sortiere nach Zeit (älteste zuerst)
            data.sort(key=lambda x: x.get('ts', ''))
            
            # Bereite Chart-Daten vor
            chart_data = {
                'labels': [],
                'soc': [],
                'power': [],
                'voltage': [],
                'current': [],
                'temperature': []
            }
            
            for record in data:
                ts = record.get('ts', '')
                if ts:
                    # Konvertiere ISO-String zu lesbarem Format
                    try:
                        dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                        chart_data['labels'].append(dt.strftime('%H:%M'))
                    except:
                        chart_data['labels'].append(ts)
                
                chart_data['soc'].append(float(record.get('soc', 0)) if record.get('soc') is not None else None)
                chart_data['power'].append(float(record.get('p', 0)) if record.get('p') is not None else None)
                chart_data['voltage'].append(float(record.get('v_dc', 0)) if record.get('v_dc') is not None else None)
                chart_data['current'].append(float(record.get('i_dc', 0)) if record.get('i_dc') is not None else None)
                chart_data['temperature'].append(float(record.get('t_cell_max', 0)) if record.get('t_cell_max') is not None else None)
            
            return chart_data
            
        except Exception as e:
            logger.error(f"Fehler beim Erstellen der Chart-Daten: {e}")
            return {'error': str(e)}

# Globale Service-Instanz
live_bess_service = LiveBESSDataService()
