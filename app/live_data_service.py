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
    
    # ============================================================================
    # PROJEKT-ZUORDNUNG METHODEN
    # ============================================================================
    
    def get_project_mappings(self, project_id: int = None) -> List[Dict[str, Any]]:
        """Holt BESS-Projekt-Zuordnungen"""
        try:
            from models import BESSProjectMapping, Project
            
            query = BESSProjectMapping.query
            
            if project_id:
                query = query.filter_by(project_id=project_id)
            
            mappings = query.all()
            
            result = []
            for mapping in mappings:
                result.append({
                    'id': mapping.id,
                    'project_id': mapping.project_id,
                    'project_name': mapping.project.name,
                    'site': mapping.site,
                    'device': mapping.device,
                    'bess_name': mapping.bess_name,
                    'display_name': mapping.display_name,
                    'mqtt_topic': mapping.mqtt_topic,
                    'is_active': mapping.is_active,
                    'auto_sync': mapping.auto_sync,
                    'sync_interval_minutes': mapping.sync_interval_minutes,
                    'description': mapping.description,
                    'location': mapping.location,
                    'manufacturer': mapping.manufacturer,
                    'model': mapping.model,
                    'rated_power_kw': mapping.rated_power_kw,
                    'rated_energy_kwh': mapping.rated_energy_kwh,
                    'last_sync': mapping.last_sync.isoformat() if mapping.last_sync else None,
                    'created_at': mapping.created_at.isoformat()
                })
            
            logger.info(f"Projekt-Mappings abgerufen: {len(result)} für Projekt {project_id or 'alle'}")
            return result
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Projekt-Mappings: {e}")
            return []
    
    def get_project_live_data(self, project_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Holt Live-Daten für ein spezifisches Projekt"""
        try:
            from models import BESSProjectMapping, BESSTelemetryData
            
            # Hole alle aktiven Mappings für das Projekt
            mappings = BESSProjectMapping.query.filter_by(
                project_id=project_id,
                is_active=True
            ).all()
            
            if not mappings:
                logger.warning(f"Keine aktiven BESS-Mappings für Projekt {project_id}")
                return []
            
            # Hole neueste Telemetrie-Daten für alle Mappings
            result = []
            for mapping in mappings:
                latest_data = BESSTelemetryData.query.filter_by(
                    bess_mapping_id=mapping.id
                ).order_by(BESSTelemetryData.timestamp.desc()).limit(limit).all()
                
                for data in latest_data:
                    result.append({
                        'project_id': project_id,
                        'project_name': mapping.project.name,
                        'bess_mapping_id': mapping.id,
                        'bess_name': mapping.display_name,
                        'site': mapping.site,
                        'device': mapping.device,
                        'timestamp': data.timestamp.isoformat(),
                        'soc': data.soc_percent,
                        'p': data.power_kw,
                        'p_ch': data.power_charge_kw,
                        'p_dis': data.power_discharge_kw,
                        'v_dc': data.voltage_dc_v,
                        'i_dc': data.current_dc_a,
                        't_cell_max': data.temperature_max_c,
                        'soh': data.soh_percent,
                        'alarms': json.loads(data.alarms) if data.alarms else [],
                        'data_quality': data.data_quality,
                        'source': data.source
                    })
            
            # Sortiere nach Zeitstempel (neueste zuerst)
            result.sort(key=lambda x: x['timestamp'], reverse=True)
            
            logger.info(f"Projekt-spezifische Live-Daten: {len(result)} für Projekt {project_id}")
            return result[:limit]
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Projekt-Live-Daten: {e}")
            return []
    
    def get_project_device_summary(self, project_id: int) -> Dict[str, Any]:
        """Holt Geräte-Zusammenfassung für ein Projekt"""
        try:
            from models import BESSProjectMapping, BESSTelemetryData
            
            mappings = BESSProjectMapping.query.filter_by(
                project_id=project_id,
                is_active=True
            ).all()
            
            if not mappings:
                return {
                    'project_id': project_id,
                    'devices': [],
                    'sites': [],
                    'total_power_kw': 0,
                    'total_energy_kwh': 0,
                    'last_update': None
                }
            
            devices = []
            sites = set()
            total_power = 0
            total_energy = 0
            last_update = None
            
            for mapping in mappings:
                # Hole neueste Daten
                latest_data = BESSTelemetryData.query.filter_by(
                    bess_mapping_id=mapping.id
                ).order_by(BESSTelemetryData.timestamp.desc()).first()
                
                device_info = {
                    'id': mapping.id,
                    'name': mapping.display_name,
                    'site': mapping.site,
                    'device': mapping.device,
                    'rated_power_kw': mapping.rated_power_kw,
                    'rated_energy_kwh': mapping.rated_energy_kwh,
                    'location': mapping.location,
                    'manufacturer': mapping.manufacturer,
                    'model': mapping.model,
                    'is_active': mapping.is_active,
                    'last_sync': mapping.last_sync.isoformat() if mapping.last_sync else None
                }
                
                if latest_data:
                    device_info.update({
                        'last_data': latest_data.timestamp.isoformat(),
                        'soc': latest_data.soc_percent,
                        'power': latest_data.power_kw,
                        'temperature': latest_data.temperature_max_c,
                        'data_quality': latest_data.data_quality
                    })
                    
                    if latest_data.timestamp and (not last_update or latest_data.timestamp > last_update):
                        last_update = latest_data.timestamp
                
                devices.append(device_info)
                sites.add(mapping.site)
                
                if mapping.rated_power_kw:
                    total_power += mapping.rated_power_kw
                if mapping.rated_energy_kwh:
                    total_energy += mapping.rated_energy_kwh
            
            return {
                'project_id': project_id,
                'project_name': mappings[0].project.name if mappings else None,
                'devices': devices,
                'sites': list(sites),
                'device_count': len(devices),
                'site_count': len(sites),
                'total_power_kw': total_power,
                'total_energy_kwh': total_energy,
                'last_update': last_update.isoformat() if last_update else None
            }
            
        except Exception as e:
            logger.error(f"Fehler bei Projekt-Device-Summary: {e}")
            return {'error': str(e)}
    
    def sync_project_data(self, project_id: int) -> Dict[str, Any]:
        """Synchronisiert Live-Daten für ein Projekt mit der Datenbank"""
        try:
            from models import BESSProjectMapping, BESSTelemetryData
            from datetime import datetime
            
            mappings = BESSProjectMapping.query.filter_by(
                project_id=project_id,
                is_active=True,
                auto_sync=True
            ).all()
            
            if not mappings:
                return {'message': 'Keine aktiven Mappings für Auto-Sync gefunden'}
            
            synced_count = 0
            error_count = 0
            
            for mapping in mappings:
                try:
                    # Hole Live-Daten vom MQTT/FastAPI Service
                    live_data = self.get_live_data(limit=1)
                    
                    # Filtere nach diesem Mapping
                    mapping_data = None
                    for data in live_data:
                        if data.get('site') == mapping.site and data.get('device') == mapping.device:
                            mapping_data = data
                            break
                    
                    if mapping_data:
                        # Speichere in Telemetrie-Tabelle
                        from app import db
                        telemetry = BESSTelemetryData(
                            bess_mapping_id=mapping.id,
                            timestamp=datetime.fromisoformat(mapping_data['ts'].replace('Z', '+00:00')),
                            soc_percent=mapping_data.get('soc'),
                            power_kw=mapping_data.get('p'),
                            power_charge_kw=mapping_data.get('p_ch'),
                            power_discharge_kw=mapping_data.get('p_dis'),
                            voltage_dc_v=mapping_data.get('v_dc'),
                            current_dc_a=mapping_data.get('i_dc'),
                            temperature_max_c=mapping_data.get('t_cell_max'),
                            soh_percent=mapping_data.get('soh'),
                            alarms=json.dumps(mapping_data.get('alarms', [])),
                            source='mqtt' if self.use_mqtt else 'fastapi'
                        )
                        
                        db.session.add(telemetry)
                        
                        # Update last_sync
                        mapping.last_sync = datetime.utcnow()
                        
                        synced_count += 1
                        
                except Exception as e:
                    logger.error(f"Fehler beim Sync für Mapping {mapping.id}: {e}")
                    error_count += 1
            
            db.session.commit()
            
            return {
                'project_id': project_id,
                'synced_mappings': synced_count,
                'errors': error_count,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Fehler bei Projekt-Sync: {e}")
            from app import db
            db.session.rollback()
            return {'error': str(e)}

# Globale Service-Instanz
live_bess_service = LiveBESSDataService()
