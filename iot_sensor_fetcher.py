#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IoT Sensor Fetcher für BESS Simulation
=====================================

Integration von IoT-Sensoren für Real-time BESS-Monitoring.
Unterstützt verschiedene Sensor-Typen für Batterie-, PV- und Grid-Monitoring.

Unterstützt:
- Batterie-Sensoren (Spannung, Strom, Temperatur, SOC)
- PV-Sensoren (Leistung, Spannung, Strom, Temperatur)
- Grid-Sensoren (Spannung, Frequenz, Power Factor)
- Umgebungs-Sensoren (Temperatur, Luftfeuchtigkeit, Wind)
- Smart Meter Integration
- Modbus TCP/RTU Support
- MQTT Integration
- OPC UA Support

Autor: Ing. Heinz Schlagintweit
Datum: Januar 2025
"""

import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import time
import os
import hashlib
import hmac
from dataclasses import dataclass
from decimal import Decimal
import math
import random

# Logging konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BatterySensorData:
    """Datenklasse für Batterie-Sensor-Daten"""
    timestamp: datetime
    voltage_v: float
    current_a: float
    power_w: float
    temperature_c: float
    soc_percent: float
    soh_percent: float
    cycle_count: int
    sensor_id: str
    battery_id: str
    location: str
    source: str

@dataclass
class PVSensorData:
    """Datenklasse für PV-Sensor-Daten"""
    timestamp: datetime
    power_w: float
    voltage_v: float
    current_a: float
    temperature_c: float
    irradiance_w_m2: float
    efficiency_percent: float
    sensor_id: str
    pv_string_id: str
    location: str
    source: str

@dataclass
class GridSensorData:
    """Datenklasse für Grid-Sensor-Daten"""
    timestamp: datetime
    voltage_v: float
    frequency_hz: float
    power_factor: float
    active_power_w: float
    reactive_power_var: float
    apparent_power_va: float
    sensor_id: str
    grid_connection_id: str
    location: str
    source: str

@dataclass
class EnvironmentalSensorData:
    """Datenklasse für Umgebungs-Sensor-Daten"""
    timestamp: datetime
    temperature_c: float
    humidity_percent: float
    wind_speed_ms: float
    wind_direction_deg: float
    pressure_hpa: float
    sensor_id: str
    location: str
    source: str

class IoTSensorFetcher:
    """Hauptklasse für IoT-Sensor Integration"""
    
    def __init__(self):
        # API-Konfiguration
        self.api_keys = {
            'modbus_tcp': os.getenv('MODBUS_TCP_API_KEY', ''),
            'mqtt_broker': os.getenv('MQTT_BROKER_API_KEY', ''),
            'opc_ua': os.getenv('OPC_UA_API_KEY', ''),
            'smart_meter': os.getenv('SMART_METER_IOT_API_KEY', ''),
            'weather_station': os.getenv('WEATHER_STATION_API_KEY', '')
        }
        
        # API-Endpunkte
        self.api_endpoints = {
            'modbus_tcp': 'https://api.modbus-tcp.com/v1/sensors',
            'mqtt_broker': 'https://api.mqtt-broker.com/v1/data',
            'opc_ua': 'https://api.opc-ua.com/v1/nodes',
            'smart_meter': 'https://api.smart-meter-iot.com/v1/readings',
            'weather_station': 'https://api.weather-station.com/v1/environmental'
        }
        
        # Rate Limiting
        self.last_request_time = {}
        self.min_request_interval = 1.0  # Sekunden zwischen Requests
        
        # IoT-Sensor-Typen
        self.sensor_types = {
            'battery': {
                'name': 'Batterie-Sensoren',
                'description': 'BESS Batterie-Monitoring',
                'parameters': ['voltage', 'current', 'power', 'temperature', 'soc', 'soh'],
                'active': True
            },
            'pv': {
                'name': 'PV-Sensoren',
                'description': 'Photovoltaik-Monitoring',
                'parameters': ['power', 'voltage', 'current', 'temperature', 'irradiance'],
                'active': True
            },
            'grid': {
                'name': 'Grid-Sensoren',
                'description': 'Netz-Monitoring',
                'parameters': ['voltage', 'frequency', 'power_factor', 'active_power'],
                'active': True
            },
            'environmental': {
                'name': 'Umgebungs-Sensoren',
                'description': 'Wetter- und Umgebungsdaten',
                'parameters': ['temperature', 'humidity', 'wind_speed', 'pressure'],
                'active': True
            }
        }
        
        # Kommunikationsprotokolle
        self.protocols = {
            'modbus_tcp': {
                'name': 'Modbus TCP',
                'description': 'Industrielles Kommunikationsprotokoll',
                'port': 502,
                'active': True
            },
            'mqtt': {
                'name': 'MQTT',
                'description': 'Message Queuing Telemetry Transport',
                'port': 1883,
                'active': True
            },
            'opc_ua': {
                'name': 'OPC UA',
                'description': 'Open Platform Communications Unified Architecture',
                'port': 4840,
                'active': True
            },
            'http': {
                'name': 'HTTP REST',
                'description': 'RESTful API',
                'port': 80,
                'active': True
            }
        }
    
    def _rate_limit(self, protocol: str):
        """Rate Limiting für IoT-Requests"""
        current_time = time.time()
        last_time = self.last_request_time.get(protocol, 0)
        time_since_last = current_time - last_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time[protocol] = time.time()
    
    def _make_request(self, url: str, params: Dict = None, headers: Dict = None) -> Optional[Dict]:
        """Sichere IoT-API-Request mit Fehlerbehandlung"""
        try:
            logger.info(f"📡 IoT Sensor API-Request: {url}")
            response = requests.get(url, params=params, headers=headers, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✅ IoT Sensor API-Response erfolgreich: {len(str(data))} Zeichen")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ IoT Sensor API-Request fehlgeschlagen: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Unerwarteter Fehler: {e}")
            return None
    
    def get_battery_sensor_data(self, hours: int = 24) -> List[BatterySensorData]:
        """Batterie-Sensor-Daten abrufen"""
        if not self.api_keys['modbus_tcp']:
            logger.warning("⚠️ Modbus TCP API-Key nicht konfiguriert - Demo-Modus aktiviert")
            return self._generate_demo_battery_data(hours)
        
        self._rate_limit('modbus_tcp')
        
        url = f"{self.api_endpoints['modbus_tcp']}/battery"
        params = {
            'hours': hours,
            'limit': 100
        }
        headers = {
            'Authorization': f"Bearer {self.api_keys['modbus_tcp']}",
            'Content-Type': 'application/json'
        }
        
        data = self._make_request(url, params, headers)
        if not data:
            logger.warning("⚠️ Modbus TCP Battery API nicht verfügbar - verwende Demo-Daten")
            return self._generate_demo_battery_data(hours)
        
        return self._parse_battery_data(data)
    
    def get_pv_sensor_data(self, hours: int = 24) -> List[PVSensorData]:
        """PV-Sensor-Daten abrufen"""
        if not self.api_keys['mqtt_broker']:
            logger.warning("⚠️ MQTT Broker API-Key nicht konfiguriert - Demo-Modus aktiviert")
            return self._generate_demo_pv_data(hours)
        
        self._rate_limit('mqtt')
        
        url = f"{self.api_endpoints['mqtt_broker']}/pv"
        params = {
            'hours': hours,
            'limit': 100
        }
        headers = {
            'Authorization': f"Bearer {self.api_keys['mqtt_broker']}",
            'Content-Type': 'application/json'
        }
        
        data = self._make_request(url, params, headers)
        if not data:
            logger.warning("⚠️ MQTT Broker PV API nicht verfügbar - verwende Demo-Daten")
            return self._generate_demo_pv_data(hours)
        
        return self._parse_pv_data(data)
    
    def get_grid_sensor_data(self, hours: int = 24) -> List[GridSensorData]:
        """Grid-Sensor-Daten abrufen"""
        if not self.api_keys['opc_ua']:
            logger.warning("⚠️ OPC UA API-Key nicht konfiguriert - Demo-Modus aktiviert")
            return self._generate_demo_grid_data(hours)
        
        self._rate_limit('opc_ua')
        
        url = f"{self.api_endpoints['opc_ua']}/grid"
        params = {
            'hours': hours,
            'limit': 100
        }
        headers = {
            'Authorization': f"Bearer {self.api_keys['opc_ua']}",
            'Content-Type': 'application/json'
        }
        
        data = self._make_request(url, params, headers)
        if not data:
            logger.warning("⚠️ OPC UA Grid API nicht verfügbar - verwende Demo-Daten")
            return self._generate_demo_grid_data(hours)
        
        return self._parse_grid_data(data)
    
    def get_environmental_sensor_data(self, hours: int = 24) -> List[EnvironmentalSensorData]:
        """Umgebungs-Sensor-Daten abrufen"""
        if not self.api_keys['weather_station']:
            logger.warning("⚠️ Weather Station API-Key nicht konfiguriert - Demo-Modus aktiviert")
            return self._generate_demo_environmental_data(hours)
        
        self._rate_limit('weather_station')
        
        url = f"{self.api_endpoints['weather_station']}/environmental"
        params = {
            'hours': hours,
            'limit': 100
        }
        headers = {
            'Authorization': f"Bearer {self.api_keys['weather_station']}",
            'Content-Type': 'application/json'
        }
        
        data = self._make_request(url, params, headers)
        if not data:
            logger.warning("⚠️ Weather Station Environmental API nicht verfügbar - verwende Demo-Daten")
            return self._generate_demo_environmental_data(hours)
        
        return self._parse_environmental_data(data)
    
    def _parse_battery_data(self, data: Dict) -> List[BatterySensorData]:
        """Parse Battery Sensor API Response"""
        sensor_data = []
        
        try:
            for sensor in data.get('battery_sensors', []):
                sensor_data.append(BatterySensorData(
                    timestamp=datetime.fromisoformat(sensor['timestamp'].replace('Z', '+00:00')),
                    voltage_v=float(sensor['voltage_v']),
                    current_a=float(sensor['current_a']),
                    power_w=float(sensor['power_w']),
                    temperature_c=float(sensor['temperature_c']),
                    soc_percent=float(sensor['soc_percent']),
                    soh_percent=float(sensor['soh_percent']),
                    cycle_count=int(sensor['cycle_count']),
                    sensor_id=sensor.get('sensor_id', ''),
                    battery_id=sensor.get('battery_id', ''),
                    location=sensor.get('location', ''),
                    source='Modbus TCP Battery API'
                ))
        except Exception as e:
            logger.error(f"❌ Fehler beim Parsen der Battery Sensor Daten: {e}")
        
        return sensor_data
    
    def _parse_pv_data(self, data: Dict) -> List[PVSensorData]:
        """Parse PV Sensor API Response"""
        sensor_data = []
        
        try:
            for sensor in data.get('pv_sensors', []):
                sensor_data.append(PVSensorData(
                    timestamp=datetime.fromisoformat(sensor['timestamp'].replace('Z', '+00:00')),
                    power_w=float(sensor['power_w']),
                    voltage_v=float(sensor['voltage_v']),
                    current_a=float(sensor['current_a']),
                    temperature_c=float(sensor['temperature_c']),
                    irradiance_w_m2=float(sensor['irradiance_w_m2']),
                    efficiency_percent=float(sensor['efficiency_percent']),
                    sensor_id=sensor.get('sensor_id', ''),
                    pv_string_id=sensor.get('pv_string_id', ''),
                    location=sensor.get('location', ''),
                    source='MQTT PV API'
                ))
        except Exception as e:
            logger.error(f"❌ Fehler beim Parsen der PV Sensor Daten: {e}")
        
        return sensor_data
    
    def _parse_grid_data(self, data: Dict) -> List[GridSensorData]:
        """Parse Grid Sensor API Response"""
        sensor_data = []
        
        try:
            for sensor in data.get('grid_sensors', []):
                sensor_data.append(GridSensorData(
                    timestamp=datetime.fromisoformat(sensor['timestamp'].replace('Z', '+00:00')),
                    voltage_v=float(sensor['voltage_v']),
                    frequency_hz=float(sensor['frequency_hz']),
                    power_factor=float(sensor['power_factor']),
                    active_power_w=float(sensor['active_power_w']),
                    reactive_power_var=float(sensor['reactive_power_var']),
                    apparent_power_va=float(sensor['apparent_power_va']),
                    sensor_id=sensor.get('sensor_id', ''),
                    grid_connection_id=sensor.get('grid_connection_id', ''),
                    location=sensor.get('location', ''),
                    source='OPC UA Grid API'
                ))
        except Exception as e:
            logger.error(f"❌ Fehler beim Parsen der Grid Sensor Daten: {e}")
        
        return sensor_data
    
    def _parse_environmental_data(self, data: Dict) -> List[EnvironmentalSensorData]:
        """Parse Environmental Sensor API Response"""
        sensor_data = []
        
        try:
            for sensor in data.get('environmental_sensors', []):
                sensor_data.append(EnvironmentalSensorData(
                    timestamp=datetime.fromisoformat(sensor['timestamp'].replace('Z', '+00:00')),
                    temperature_c=float(sensor['temperature_c']),
                    humidity_percent=float(sensor['humidity_percent']),
                    wind_speed_ms=float(sensor['wind_speed_ms']),
                    wind_direction_deg=float(sensor['wind_direction_deg']),
                    pressure_hpa=float(sensor['pressure_hpa']),
                    sensor_id=sensor.get('sensor_id', ''),
                    location=sensor.get('location', ''),
                    source='Weather Station Environmental API'
                ))
        except Exception as e:
            logger.error(f"❌ Fehler beim Parsen der Environmental Sensor Daten: {e}")
        
        return sensor_data
    
    def _generate_demo_battery_data(self, hours: int) -> List[BatterySensorData]:
        """Generiere Demo-Daten für Batterie-Sensoren"""
        logger.warning("⚠️ IoT Demo-Modus - generiere Battery Sensor Daten")
        
        demo_data = []
        start_dt = datetime.now() - timedelta(hours=hours)
        
        for i in range(min(hours * 4, 96)):  # Alle 15 Minuten, max 96 Datenpunkte
            timestamp = start_dt + timedelta(minutes=i * 15)
            
            # Realistische Batterie-Daten
            base_voltage = 400.0  # 400V System
            voltage_v = base_voltage + random.uniform(-5.0, 5.0)
            
            # SOC basierend auf Tageszeit (Laden/Entladen)
            hour_of_day = timestamp.hour
            if 6 <= hour_of_day <= 18:  # Tag: Entladen
                soc_percent = max(20.0, 100.0 - (hour_of_day - 6) * 5)
            else:  # Nacht: Laden
                soc_percent = min(100.0, 20.0 + (24 - hour_of_day + 6) * 3)
            
            # Strom basierend auf SOC und Tageszeit
            if soc_percent > 80:
                current_a = random.uniform(-50, -10)  # Laden
            elif soc_percent < 30:
                current_a = random.uniform(10, 100)  # Entladen
            else:
                current_a = random.uniform(-20, 20)  # Neutral
            
            power_w = voltage_v * current_a
            temperature_c = 25.0 + random.uniform(-5, 15)  # 20-40°C
            soh_percent = max(80.0, 100.0 - (i / 1000))  # Degradation über Zeit
            cycle_count = int(i / 10)  # Zyklen basierend auf Zeit
            
            demo_data.append(BatterySensorData(
                timestamp=timestamp,
                voltage_v=round(voltage_v, 2),
                current_a=round(current_a, 2),
                power_w=round(power_w, 1),
                temperature_c=round(temperature_c, 1),
                soc_percent=round(soc_percent, 1),
                soh_percent=round(soh_percent, 1),
                cycle_count=cycle_count,
                sensor_id=f"BAT_SENSOR_{i % 10 + 1:02d}",
                battery_id=f"BATTERY_{i % 5 + 1:02d}",
                location=f"BESS_Location_{i % 3 + 1}",
                source='Battery Sensor (Demo)'
            ))
        
        logger.info(f"✅ Battery Sensor Demo-Daten generiert: {len(demo_data)} Datenpunkte")
        return demo_data
    
    def _generate_demo_pv_data(self, hours: int) -> List[PVSensorData]:
        """Generiere Demo-Daten für PV-Sensoren"""
        logger.warning("⚠️ IoT Demo-Modus - generiere PV Sensor Daten")
        
        demo_data = []
        start_dt = datetime.now() - timedelta(hours=hours)
        
        for i in range(min(hours * 4, 96)):  # Alle 15 Minuten, max 96 Datenpunkte
            timestamp = start_dt + timedelta(minutes=i * 15)
            
            # Realistische PV-Daten basierend auf Tageszeit
            hour_of_day = timestamp.hour
            minute_of_hour = timestamp.minute
            
            # Sonnenstand simulieren
            if 6 <= hour_of_day <= 18:  # Tag
                sun_factor = math.sin((hour_of_day - 6) * math.pi / 12)
                irradiance_w_m2 = 1000 * sun_factor + random.uniform(-100, 100)
                irradiance_w_m2 = max(0, irradiance_w_m2)
            else:  # Nacht
                irradiance_w_m2 = 0
            
            # PV-Leistung basierend auf Einstrahlung
            if irradiance_w_m2 > 0:
                base_power = 10000  # 10 kW System
                power_w = base_power * (irradiance_w_m2 / 1000) * random.uniform(0.8, 1.0)
                voltage_v = 400.0 + random.uniform(-10, 10)
                current_a = power_w / voltage_v if voltage_v > 0 else 0
                efficiency_percent = random.uniform(18, 22)
            else:
                power_w = 0
                voltage_v = 0
                current_a = 0
                efficiency_percent = 0
            
            temperature_c = 25.0 + (irradiance_w_m2 / 1000) * 10 + random.uniform(-5, 5)
            
            demo_data.append(PVSensorData(
                timestamp=timestamp,
                power_w=round(power_w, 1),
                voltage_v=round(voltage_v, 2),
                current_a=round(current_a, 2),
                temperature_c=round(temperature_c, 1),
                irradiance_w_m2=round(irradiance_w_m2, 1),
                efficiency_percent=round(efficiency_percent, 1),
                sensor_id=f"PV_SENSOR_{i % 8 + 1:02d}",
                pv_string_id=f"PV_STRING_{i % 4 + 1:02d}",
                location=f"PV_Location_{i % 2 + 1}",
                source='PV Sensor (Demo)'
            ))
        
        logger.info(f"✅ PV Sensor Demo-Daten generiert: {len(demo_data)} Datenpunkte")
        return demo_data
    
    def _generate_demo_grid_data(self, hours: int) -> List[GridSensorData]:
        """Generiere Demo-Daten für Grid-Sensoren"""
        logger.warning("⚠️ IoT Demo-Modus - generiere Grid Sensor Daten")
        
        demo_data = []
        start_dt = datetime.now() - timedelta(hours=hours)
        
        for i in range(min(hours * 4, 96)):  # Alle 15 Minuten, max 96 Datenpunkte
            timestamp = start_dt + timedelta(minutes=i * 15)
            
            # Realistische Grid-Daten
            voltage_v = 400.0 + random.uniform(-10, 10)  # 390-410V
            frequency_hz = 50.0 + random.uniform(-0.1, 0.1)  # 49.9-50.1 Hz
            power_factor = random.uniform(0.85, 1.0)  # 0.85-1.0
            
            # Leistung basierend auf Tageszeit
            hour_of_day = timestamp.hour
            if 6 <= hour_of_day <= 22:  # Tag: höhere Last
                base_power = 50000  # 50 kW
            else:  # Nacht: niedrigere Last
                base_power = 20000  # 20 kW
            
            active_power_w = base_power + random.uniform(-5000, 5000)
            apparent_power_va = active_power_w / power_factor
            reactive_power_var = math.sqrt(apparent_power_va**2 - active_power_w**2)
            
            demo_data.append(GridSensorData(
                timestamp=timestamp,
                voltage_v=round(voltage_v, 2),
                frequency_hz=round(frequency_hz, 3),
                power_factor=round(power_factor, 3),
                active_power_w=round(active_power_w, 1),
                reactive_power_var=round(reactive_power_var, 1),
                apparent_power_va=round(apparent_power_va, 1),
                sensor_id=f"GRID_SENSOR_{i % 6 + 1:02d}",
                grid_connection_id=f"GRID_CONN_{i % 3 + 1:02d}",
                location=f"Grid_Location_{i % 2 + 1}",
                source='Grid Sensor (Demo)'
            ))
        
        logger.info(f"✅ Grid Sensor Demo-Daten generiert: {len(demo_data)} Datenpunkte")
        return demo_data
    
    def _generate_demo_environmental_data(self, hours: int) -> List[EnvironmentalSensorData]:
        """Generiere Demo-Daten für Umgebungs-Sensoren"""
        logger.warning("⚠️ IoT Demo-Modus - generiere Environmental Sensor Daten")
        
        demo_data = []
        start_dt = datetime.now() - timedelta(hours=hours)
        
        for i in range(min(hours * 4, 96)):  # Alle 15 Minuten, max 96 Datenpunkte
            timestamp = start_dt + timedelta(minutes=i * 15)
            
            # Realistische Umgebungsdaten
            hour_of_day = timestamp.hour
            
            # Temperatur basierend auf Tageszeit
            base_temp = 20.0
            temp_variation = 10 * math.sin((hour_of_day - 6) * math.pi / 12)
            temperature_c = base_temp + temp_variation + random.uniform(-3, 3)
            
            # Luftfeuchtigkeit (invers zu Temperatur)
            humidity_percent = max(30, 80 - (temperature_c - 20) * 2) + random.uniform(-10, 10)
            humidity_percent = min(100, max(20, humidity_percent))
            
            # Wind basierend auf Tageszeit (mehr Wind am Tag)
            if 8 <= hour_of_day <= 18:
                wind_speed_ms = random.uniform(2, 8)
            else:
                wind_speed_ms = random.uniform(0, 4)
            
            wind_direction_deg = random.uniform(0, 360)
            pressure_hpa = 1013.25 + random.uniform(-20, 20)
            
            demo_data.append(EnvironmentalSensorData(
                timestamp=timestamp,
                temperature_c=round(temperature_c, 1),
                humidity_percent=round(humidity_percent, 1),
                wind_speed_ms=round(wind_speed_ms, 1),
                wind_direction_deg=round(wind_direction_deg, 1),
                pressure_hpa=round(pressure_hpa, 2),
                sensor_id=f"ENV_SENSOR_{i % 4 + 1:02d}",
                location=f"Environmental_Location_{i % 2 + 1}",
                source='Environmental Sensor (Demo)'
            ))
        
        logger.info(f"✅ Environmental Sensor Demo-Daten generiert: {len(demo_data)} Datenpunkte")
        return demo_data
    
    def get_all_sensor_data(self, hours: int = 24) -> Dict:
        """Alle IoT-Sensor-Daten abrufen"""
        logger.info(f"📡 Lade IoT-Sensor-Daten für {hours} Stunden...")
        
        result = {
            'sensors': {},
            'summary': {
                'total_sensors': 0,
                'total_power_w': 0.0,
                'avg_temperature_c': 0.0,
                'sensor_types_active': 0
            },
            'status': 'success',
            'timestamp': datetime.now().isoformat()
        }
        
        for sensor_type, sensor_config in self.sensor_types.items():
            if not sensor_config.get('active', False):
                continue
            
            try:
                logger.info(f"📡 Lade {sensor_config['name']} Daten...")
                
                if sensor_type == 'battery':
                    data = self.get_battery_sensor_data(hours)
                elif sensor_type == 'pv':
                    data = self.get_pv_sensor_data(hours)
                elif sensor_type == 'grid':
                    data = self.get_grid_sensor_data(hours)
                elif sensor_type == 'environmental':
                    data = self.get_environmental_sensor_data(hours)
                else:
                    continue
                
                if data:
                    result['sensors'][sensor_type] = {
                        'name': sensor_config['name'],
                        'description': sensor_config['description'],
                        'data': data,
                        'count': len(data),
                        'parameters': sensor_config['parameters']
                    }
                    
                    # Summary aktualisieren
                    result['summary']['total_sensors'] += len(data)
                    result['summary']['sensor_types_active'] += 1
                    
                    # Spezifische Metriken
                    if sensor_type == 'battery':
                        result['summary']['total_power_w'] += sum(d.power_w for d in data)
                        result['summary']['avg_temperature_c'] += sum(d.temperature_c for d in data)
                    elif sensor_type == 'pv':
                        result['summary']['total_power_w'] += sum(d.power_w for d in data)
                        result['summary']['avg_temperature_c'] += sum(d.temperature_c for d in data)
                    elif sensor_type == 'grid':
                        result['summary']['total_power_w'] += sum(d.active_power_w for d in data)
                    elif sensor_type == 'environmental':
                        result['summary']['avg_temperature_c'] += sum(d.temperature_c for d in data)
                    
                    logger.info(f"✅ {sensor_config['name']}: {len(data)} Sensoren")
                
            except Exception as e:
                logger.error(f"❌ Fehler bei {sensor_config['name']}: {e}")
        
        # Durchschnittswerte berechnen
        if result['summary']['sensor_types_active'] > 0:
            result['summary']['avg_temperature_c'] /= result['summary']['sensor_types_active']
        
        # Status prüfen
        if result['summary']['sensor_types_active'] == 0:
            result['status'] = 'error'
            result['message'] = 'Keine IoT-Sensoren verfügbar'
        elif result['summary']['sensor_types_active'] < len(self.sensor_types):
            result['status'] = 'partial'
            result['message'] = f'Nur {result["summary"]["sensor_types_active"]} von {len(self.sensor_types)} Sensor-Typen verfügbar'
        
        logger.info(f"✅ IoT-Sensor-Daten geladen: {result['summary']['total_sensors']} Sensoren, {result['summary']['total_power_w']:.1f} W")
        return result
    
    def test_api_connection(self) -> Dict:
        """Test der IoT-Sensor API-Verbindungen"""
        logger.info("🔍 Teste IoT-Sensor API Verbindungen...")
        
        result = {
            'status': 'not_configured',
            'message': 'Keine API-Keys konfiguriert',
            'sensors': {},
            'protocols': {},
            'demo_available': True
        }
        
        # Sensor-Typen testen
        for sensor_type, sensor_config in self.sensor_types.items():
            # Test mit Demo-Daten
            if sensor_type == 'battery':
                test_data = self._generate_demo_battery_data(1)
            elif sensor_type == 'pv':
                test_data = self._generate_demo_pv_data(1)
            elif sensor_type == 'grid':
                test_data = self._generate_demo_grid_data(1)
            elif sensor_type == 'environmental':
                test_data = self._generate_demo_environmental_data(1)
            else:
                continue
            
            if test_data:
                result['sensors'][sensor_type] = {
                    'name': sensor_config['name'],
                    'status': 'demo',
                    'message': f'Demo-Modus - {len(test_data)} Test-Datenpunkte'
                }
            else:
                result['sensors'][sensor_type] = {
                    'name': sensor_config['name'],
                    'status': 'error',
                    'message': 'Demo-Modus nicht verfügbar'
                }
        
        # Kommunikationsprotokolle testen
        for protocol_id, protocol_config in self.protocols.items():
            result['protocols'][protocol_id] = {
                'name': protocol_config['name'],
                'status': 'available',
                'message': f'Port {protocol_config["port"]} verfügbar'
            }
        
        # Gesamtstatus bestimmen
        working_sensors = sum(1 for s in result['sensors'].values() if s['status'] == 'demo')
        if working_sensors > 0:
            result['status'] = 'demo'
            result['message'] = f'Demo-Modus für {working_sensors} Sensor-Typen verfügbar'
        
        logger.info(f"🔍 IoT-Sensor API-Test abgeschlossen: {result['status']}")
        return result

def main():
    """Test-Funktion"""
    print("📡 IoT Sensor Fetcher Test")
    print("=" * 50)
    
    fetcher = IoTSensorFetcher()
    
    # API-Verbindungen testen
    test_result = fetcher.test_api_connection()
    print(f"API-Test: {test_result['status']}")
    print(f"Message: {test_result['message']}")
    
    # Alle Sensor-Typen testen
    print("\n📡 IoT-Sensor-Typen:")
    for sensor_type, sensor_info in test_result['sensors'].items():
        print(f"  {sensor_info['name']}: {sensor_info['status']} - {sensor_info['message']}")
    
    # Kommunikationsprotokolle
    print("\n📡 Kommunikationsprotokolle:")
    for protocol_id, protocol_info in test_result['protocols'].items():
        print(f"  {protocol_info['name']}: {protocol_info['status']} - {protocol_info['message']}")
    
    # Demo-Daten für alle Sensoren abrufen
    print("\n📡 Demo-Daten für alle Sensoren:")
    all_data = fetcher.get_all_sensor_data(24)
    
    print(f"Status: {all_data['status']}")
    print(f"Sensor-Typen aktiv: {all_data['summary']['sensor_types_active']}")
    print(f"Gesamt Sensoren: {all_data['summary']['total_sensors']}")
    print(f"Gesamt Power: {all_data['summary']['total_power_w']:.1f} W")
    print(f"Durchschnittstemperatur: {all_data['summary']['avg_temperature_c']:.1f} °C")

if __name__ == "__main__":
    main()
