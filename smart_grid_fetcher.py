#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart Grid Fetcher für BESS Simulation
=====================================

Integration von Smart Grid Services für intelligente Stromnetze.
Unterstützt Grid-Services, Frequenzregelung, Spannungshaltung und Demand Response.

Unterstützt:
- Frequenzregelung (FCR, aFRR, mFRR)
- Spannungshaltung (Reactive Power)
- Demand Response Management
- Grid Code Compliance
- Virtuelle Kraftwerke
- Smart Meter Integration
- Grid Stability Monitoring

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

# Logging konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class GridServiceData:
    """Datenklasse für Smart Grid Services"""
    timestamp: datetime
    service_type: str  # 'fcr', 'afrr', 'mfrr', 'voltage', 'demand_response'
    power_mw: float
    price_eur_mw: float
    grid_operator: str
    service_provider: str
    grid_area: str
    frequency_hz: float
    voltage_kv: float
    response_time_ms: int
    availability: float  # 0.0 - 1.0
    source: str

@dataclass
class GridStabilityData:
    """Datenklasse für Grid Stability Monitoring"""
    timestamp: datetime
    frequency_hz: float
    voltage_kv: float
    power_flow_mw: float
    grid_load_percent: float
    stability_index: float  # 0.0 - 1.0
    grid_area: str
    operator: str
    source: str

class SmartGridFetcher:
    """Hauptklasse für Smart Grid Integration"""
    
    def __init__(self):
        # API-Konfiguration
        self.api_keys = {
            'apg': os.getenv('APG_SMART_GRID_API_KEY', ''),
            'tso_austria': os.getenv('TSO_AUSTRIA_API_KEY', ''),
            'epex_spot': os.getenv('EPEX_SPOT_API_KEY', ''),
            'grid_operator': os.getenv('GRID_OPERATOR_API_KEY', ''),
            'smart_meter': os.getenv('SMART_METER_API_KEY', '')
        }
        
        # API-Endpunkte
        self.api_endpoints = {
            'apg': 'https://api.apg.at/v1/smart-grid',
            'tso_austria': 'https://api.tso-austria.at/v1/grid-services',
            'epex_spot': 'https://api.epexspot.com/v1/balancing',
            'grid_operator': 'https://api.grid-operator.at/v1/services',
            'smart_meter': 'https://api.smart-meter.at/v1/data'
        }
        
        # Rate Limiting
        self.last_request_time = {}
        self.min_request_interval = 2.0  # Sekunden zwischen Requests
        
        # Grid Services
        self.grid_services = {
            'fcr': {
                'name': 'Frequenzregelung (FCR)',
                'description': 'Primäre Frequenzregelung',
                'response_time': '30 Sekunden',
                'duration': '30 Minuten',
                'active': True
            },
            'afrr': {
                'name': 'Automatische Frequenzregelung (aFRR)',
                'description': 'Sekundäre Frequenzregelung',
                'response_time': '5 Minuten',
                'duration': '15 Minuten',
                'active': True
            },
            'mfrr': {
                'name': 'Manuelle Frequenzregelung (mFRR)',
                'description': 'Tertiäre Frequenzregelung',
                'response_time': '12.5 Minuten',
                'duration': '60 Minuten',
                'active': True
            },
            'voltage': {
                'name': 'Spannungshaltung',
                'description': 'Reactive Power Management',
                'response_time': '1 Minute',
                'duration': 'Kontinuierlich',
                'active': True
            },
            'demand_response': {
                'name': 'Demand Response',
                'description': 'Laststeuerung',
                'response_time': '15 Minuten',
                'duration': '2 Stunden',
                'active': True
            }
        }
        
        # Grid Areas
        self.grid_areas = {
            'at': 'Österreich',
            'de': 'Deutschland',
            'ch': 'Schweiz',
            'it': 'Italien',
            'cz': 'Tschechien',
            'sk': 'Slowakei',
            'hu': 'Ungarn',
            'si': 'Slowenien'
        }
    
    def _rate_limit(self, service: str):
        """Rate Limiting für API-Requests"""
        current_time = time.time()
        last_time = self.last_request_time.get(service, 0)
        time_since_last = current_time - last_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time[service] = time.time()
    
    def _make_request(self, url: str, params: Dict = None, headers: Dict = None) -> Optional[Dict]:
        """Sichere API-Request mit Fehlerbehandlung"""
        try:
            logger.info(f"🔌 Smart Grid API-Request: {url}")
            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✅ Smart Grid API-Response erfolgreich: {len(str(data))} Zeichen")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Smart Grid API-Request fehlgeschlagen: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Unerwarteter Fehler: {e}")
            return None
    
    def get_fcr_data(self, hours: int = 24) -> List[GridServiceData]:
        """Frequenzregelung (FCR) Daten abrufen"""
        if not self.api_keys['apg']:
            logger.warning("⚠️ APG Smart Grid API-Key nicht konfiguriert - Demo-Modus aktiviert")
            return self._generate_demo_grid_service_data('fcr', hours)
        
        self._rate_limit('fcr')
        
        url = f"{self.api_endpoints['apg']}/fcr"
        params = {
            'hours': hours,
            'limit': 100
        }
        headers = {
            'Authorization': f"Bearer {self.api_keys['apg']}",
            'Content-Type': 'application/json'
        }
        
        data = self._make_request(url, params, headers)
        if not data:
            logger.warning("⚠️ APG FCR API nicht verfügbar - verwende Demo-Daten")
            return self._generate_demo_grid_service_data('fcr', hours)
        
        return self._parse_fcr_data(data)
    
    def get_afrr_data(self, hours: int = 24) -> List[GridServiceData]:
        """Automatische Frequenzregelung (aFRR) Daten abrufen"""
        if not self.api_keys['tso_austria']:
            logger.warning("⚠️ TSO Austria API-Key nicht konfiguriert - Demo-Modus aktiviert")
            return self._generate_demo_grid_service_data('afrr', hours)
        
        self._rate_limit('afrr')
        
        url = f"{self.api_endpoints['tso_austria']}/afrr"
        params = {
            'hours': hours,
            'limit': 100
        }
        headers = {
            'Authorization': f"Bearer {self.api_keys['tso_austria']}",
            'Content-Type': 'application/json'
        }
        
        data = self._make_request(url, params, headers)
        if not data:
            logger.warning("⚠️ TSO Austria aFRR API nicht verfügbar - verwende Demo-Daten")
            return self._generate_demo_grid_service_data('afrr', hours)
        
        return self._parse_afrr_data(data)
    
    def get_mfrr_data(self, hours: int = 24) -> List[GridServiceData]:
        """Manuelle Frequenzregelung (mFRR) Daten abrufen"""
        if not self.api_keys['epex_spot']:
            logger.warning("⚠️ EPEX Spot API-Key nicht konfiguriert - Demo-Modus aktiviert")
            return self._generate_demo_grid_service_data('mfrr', hours)
        
        self._rate_limit('mfrr')
        
        url = f"{self.api_endpoints['epex_spot']}/mfrr"
        params = {
            'hours': hours,
            'limit': 100
        }
        headers = {
            'Authorization': f"Bearer {self.api_keys['epex_spot']}",
            'Content-Type': 'application/json'
        }
        
        data = self._make_request(url, params, headers)
        if not data:
            logger.warning("⚠️ EPEX Spot mFRR API nicht verfügbar - verwende Demo-Daten")
            return self._generate_demo_grid_service_data('mfrr', hours)
        
        return self._parse_mfrr_data(data)
    
    def get_voltage_control_data(self, hours: int = 24) -> List[GridServiceData]:
        """Spannungshaltung Daten abrufen"""
        if not self.api_keys['grid_operator']:
            logger.warning("⚠️ Grid Operator API-Key nicht konfiguriert - Demo-Modus aktiviert")
            return self._generate_demo_grid_service_data('voltage', hours)
        
        self._rate_limit('voltage')
        
        url = f"{self.api_endpoints['grid_operator']}/voltage-control"
        params = {
            'hours': hours,
            'limit': 100
        }
        headers = {
            'Authorization': f"Bearer {self.api_keys['grid_operator']}",
            'Content-Type': 'application/json'
        }
        
        data = self._make_request(url, params, headers)
        if not data:
            logger.warning("⚠️ Grid Operator Voltage Control API nicht verfügbar - verwende Demo-Daten")
            return self._generate_demo_grid_service_data('voltage', hours)
        
        return self._parse_voltage_control_data(data)
    
    def get_demand_response_data(self, hours: int = 24) -> List[GridServiceData]:
        """Demand Response Daten abrufen"""
        if not self.api_keys['smart_meter']:
            logger.warning("⚠️ Smart Meter API-Key nicht konfiguriert - Demo-Modus aktiviert")
            return self._generate_demo_grid_service_data('demand_response', hours)
        
        self._rate_limit('demand_response')
        
        url = f"{self.api_endpoints['smart_meter']}/demand-response"
        params = {
            'hours': hours,
            'limit': 100
        }
        headers = {
            'Authorization': f"Bearer {self.api_keys['smart_meter']}",
            'Content-Type': 'application/json'
        }
        
        data = self._make_request(url, params, headers)
        if not data:
            logger.warning("⚠️ Smart Meter Demand Response API nicht verfügbar - verwende Demo-Daten")
            return self._generate_demo_grid_service_data('demand_response', hours)
        
        return self._parse_demand_response_data(data)
    
    def get_grid_stability_data(self, hours: int = 24) -> List[GridStabilityData]:
        """Grid Stability Monitoring Daten abrufen"""
        if not self.api_keys['apg']:
            logger.warning("⚠️ APG API-Key nicht konfiguriert - Demo-Modus aktiviert")
            return self._generate_demo_grid_stability_data(hours)
        
        self._rate_limit('grid_stability')
        
        url = f"{self.api_endpoints['apg']}/grid-stability"
        params = {
            'hours': hours,
            'limit': 100
        }
        headers = {
            'Authorization': f"Bearer {self.api_keys['apg']}",
            'Content-Type': 'application/json'
        }
        
        data = self._make_request(url, params, headers)
        if not data:
            logger.warning("⚠️ APG Grid Stability API nicht verfügbar - verwende Demo-Daten")
            return self._generate_demo_grid_stability_data(hours)
        
        return self._parse_grid_stability_data(data)
    
    def _parse_fcr_data(self, data: Dict) -> List[GridServiceData]:
        """Parse FCR API Response"""
        grid_data = []
        
        try:
            for service in data.get('fcr_services', []):
                grid_data.append(GridServiceData(
                    timestamp=datetime.fromisoformat(service['timestamp'].replace('Z', '+00:00')),
                    service_type='fcr',
                    power_mw=float(service['power_mw']),
                    price_eur_mw=float(service['price_eur_mw']),
                    grid_operator=service.get('grid_operator', 'APG'),
                    service_provider=service.get('service_provider', ''),
                    grid_area=service.get('grid_area', 'at'),
                    frequency_hz=float(service.get('frequency_hz', 50.0)),
                    voltage_kv=float(service.get('voltage_kv', 400.0)),
                    response_time_ms=int(service.get('response_time_ms', 30000)),
                    availability=float(service.get('availability', 0.95)),
                    source='APG FCR API'
                ))
        except Exception as e:
            logger.error(f"❌ Fehler beim Parsen der FCR Daten: {e}")
        
        return grid_data
    
    def _parse_afrr_data(self, data: Dict) -> List[GridServiceData]:
        """Parse aFRR API Response"""
        grid_data = []
        
        try:
            for service in data.get('afrr_services', []):
                grid_data.append(GridServiceData(
                    timestamp=datetime.fromisoformat(service['timestamp'].replace('Z', '+00:00')),
                    service_type='afrr',
                    power_mw=float(service['power_mw']),
                    price_eur_mw=float(service['price_eur_mw']),
                    grid_operator=service.get('grid_operator', 'TSO Austria'),
                    service_provider=service.get('service_provider', ''),
                    grid_area=service.get('grid_area', 'at'),
                    frequency_hz=float(service.get('frequency_hz', 50.0)),
                    voltage_kv=float(service.get('voltage_kv', 400.0)),
                    response_time_ms=int(service.get('response_time_ms', 300000)),
                    availability=float(service.get('availability', 0.90)),
                    source='TSO Austria aFRR API'
                ))
        except Exception as e:
            logger.error(f"❌ Fehler beim Parsen der aFRR Daten: {e}")
        
        return grid_data
    
    def _parse_mfrr_data(self, data: Dict) -> List[GridServiceData]:
        """Parse mFRR API Response"""
        grid_data = []
        
        try:
            for service in data.get('mfrr_services', []):
                grid_data.append(GridServiceData(
                    timestamp=datetime.fromisoformat(service['timestamp'].replace('Z', '+00:00')),
                    service_type='mfrr',
                    power_mw=float(service['power_mw']),
                    price_eur_mw=float(service['price_eur_mw']),
                    grid_operator=service.get('grid_operator', 'EPEX Spot'),
                    service_provider=service.get('service_provider', ''),
                    grid_area=service.get('grid_area', 'at'),
                    frequency_hz=float(service.get('frequency_hz', 50.0)),
                    voltage_kv=float(service.get('voltage_kv', 400.0)),
                    response_time_ms=int(service.get('response_time_ms', 750000)),
                    availability=float(service.get('availability', 0.85)),
                    source='EPEX Spot mFRR API'
                ))
        except Exception as e:
            logger.error(f"❌ Fehler beim Parsen der mFRR Daten: {e}")
        
        return grid_data
    
    def _parse_voltage_control_data(self, data: Dict) -> List[GridServiceData]:
        """Parse Voltage Control API Response"""
        grid_data = []
        
        try:
            for service in data.get('voltage_services', []):
                grid_data.append(GridServiceData(
                    timestamp=datetime.fromisoformat(service['timestamp'].replace('Z', '+00:00')),
                    service_type='voltage',
                    power_mw=float(service['reactive_power_mvar']),
                    price_eur_mw=float(service['price_eur_mvar']),
                    grid_operator=service.get('grid_operator', 'Grid Operator'),
                    service_provider=service.get('service_provider', ''),
                    grid_area=service.get('grid_area', 'at'),
                    frequency_hz=float(service.get('frequency_hz', 50.0)),
                    voltage_kv=float(service.get('voltage_kv', 400.0)),
                    response_time_ms=int(service.get('response_time_ms', 60000)),
                    availability=float(service.get('availability', 0.98)),
                    source='Grid Operator Voltage Control API'
                ))
        except Exception as e:
            logger.error(f"❌ Fehler beim Parsen der Voltage Control Daten: {e}")
        
        return grid_data
    
    def _parse_demand_response_data(self, data: Dict) -> List[GridServiceData]:
        """Parse Demand Response API Response"""
        grid_data = []
        
        try:
            for service in data.get('demand_response_services', []):
                grid_data.append(GridServiceData(
                    timestamp=datetime.fromisoformat(service['timestamp'].replace('Z', '+00:00')),
                    service_type='demand_response',
                    power_mw=float(service['power_reduction_mw']),
                    price_eur_mw=float(service['price_eur_mw']),
                    grid_operator=service.get('grid_operator', 'Smart Meter'),
                    service_provider=service.get('service_provider', ''),
                    grid_area=service.get('grid_area', 'at'),
                    frequency_hz=float(service.get('frequency_hz', 50.0)),
                    voltage_kv=float(service.get('voltage_kv', 400.0)),
                    response_time_ms=int(service.get('response_time_ms', 900000)),
                    availability=float(service.get('availability', 0.80)),
                    source='Smart Meter Demand Response API'
                ))
        except Exception as e:
            logger.error(f"❌ Fehler beim Parsen der Demand Response Daten: {e}")
        
        return grid_data
    
    def _parse_grid_stability_data(self, data: Dict) -> List[GridStabilityData]:
        """Parse Grid Stability API Response"""
        stability_data = []
        
        try:
            for stability in data.get('stability_data', []):
                stability_data.append(GridStabilityData(
                    timestamp=datetime.fromisoformat(stability['timestamp'].replace('Z', '+00:00')),
                    frequency_hz=float(stability['frequency_hz']),
                    voltage_kv=float(stability['voltage_kv']),
                    power_flow_mw=float(stability['power_flow_mw']),
                    grid_load_percent=float(stability['grid_load_percent']),
                    stability_index=float(stability['stability_index']),
                    grid_area=stability.get('grid_area', 'at'),
                    operator=stability.get('operator', 'APG'),
                    source='APG Grid Stability API'
                ))
        except Exception as e:
            logger.error(f"❌ Fehler beim Parsen der Grid Stability Daten: {e}")
        
        return stability_data
    
    def _generate_demo_grid_service_data(self, service_type: str, hours: int) -> List[GridServiceData]:
        """Generiere Demo-Daten für Grid Services"""
        logger.warning(f"⚠️ Smart Grid Demo-Modus - generiere {service_type} Daten")
        
        demo_data = []
        start_dt = datetime.now() - timedelta(hours=hours)
        
        # Service-spezifische Demo-Daten
        service_config = self.grid_services.get(service_type, {})
        service_name = service_config.get('name', service_type)
        
        for i in range(min(hours, 24)):  # Maximal 24 Datenpunkte
            timestamp = start_dt + timedelta(hours=i)
            
            # Realistische Grid Service-Daten
            if service_type == 'fcr':
                power_mw = 5.0 + (i % 8) * 2  # 5-19 MW
                base_price = 15.0  # 15 €/MW
                response_time = 30000  # 30 Sekunden
                availability = 0.95
            elif service_type == 'afrr':
                power_mw = 10.0 + (i % 12) * 5  # 10-65 MW
                base_price = 25.0  # 25 €/MW
                response_time = 300000  # 5 Minuten
                availability = 0.90
            elif service_type == 'mfrr':
                power_mw = 20.0 + (i % 15) * 10  # 20-160 MW
                base_price = 35.0  # 35 €/MW
                response_time = 750000  # 12.5 Minuten
                availability = 0.85
            elif service_type == 'voltage':
                power_mw = 2.0 + (i % 6) * 1  # 2-7 MVar
                base_price = 8.0  # 8 €/MVar
                response_time = 60000  # 1 Minute
                availability = 0.98
            elif service_type == 'demand_response':
                power_mw = 15.0 + (i % 10) * 8  # 15-87 MW
                base_price = 20.0  # 20 €/MW
                response_time = 900000  # 15 Minuten
                availability = 0.80
            else:
                power_mw = 10.0
                base_price = 20.0
                response_time = 300000
                availability = 0.90
            
            # Preis-Variation basierend auf Tageszeit
            price_variation = 0.1 * math.sin(i * math.pi / 12)  # Sinus-Kurve
            price_eur_mw = base_price + price_variation * base_price
            
            # Grid Area zufällig auswählen
            grid_area = list(self.grid_areas.keys())[i % len(self.grid_areas)]
            
            demo_data.append(GridServiceData(
                timestamp=timestamp,
                service_type=service_type,
                power_mw=round(power_mw, 2),
                price_eur_mw=round(price_eur_mw, 2),
                grid_operator=f"Demo {service_type.upper()} Operator",
                service_provider=f"Demo Provider {i % 5 + 1}",
                grid_area=grid_area,
                frequency_hz=round(50.0 + (i % 3 - 1) * 0.1, 2),
                voltage_kv=round(400.0 + (i % 5 - 2) * 2.0, 1),
                response_time_ms=response_time,
                availability=round(availability + (i % 3 - 1) * 0.02, 3),
                source=f'{service_name} (Demo)'
            ))
        
        logger.info(f"✅ Smart Grid Demo-Daten generiert: {len(demo_data)} Datenpunkte für {service_name}")
        return demo_data
    
    def _generate_demo_grid_stability_data(self, hours: int) -> List[GridStabilityData]:
        """Generiere Demo-Daten für Grid Stability"""
        logger.warning("⚠️ Smart Grid Demo-Modus - generiere Grid Stability Daten")
        
        demo_data = []
        start_dt = datetime.now() - timedelta(hours=hours)
        
        for i in range(min(hours, 24)):  # Maximal 24 Datenpunkte
            timestamp = start_dt + timedelta(hours=i)
            
            # Realistische Grid Stability-Daten
            frequency_hz = 50.0 + (i % 5 - 2) * 0.05  # 49.9 - 50.1 Hz
            voltage_kv = 400.0 + (i % 7 - 3) * 1.0  # 397 - 403 kV
            power_flow_mw = 1000.0 + (i % 20) * 50  # 1000 - 1950 MW
            grid_load_percent = 60.0 + (i % 15) * 2  # 60 - 88 %
            
            # Stability Index basierend auf Frequenz und Spannung
            freq_deviation = abs(frequency_hz - 50.0)
            voltage_deviation = abs(voltage_kv - 400.0)
            stability_index = max(0.0, 1.0 - (freq_deviation * 10 + voltage_deviation * 0.1))
            
            # Grid Area zufällig auswählen
            grid_area = list(self.grid_areas.keys())[i % len(self.grid_areas)]
            
            demo_data.append(GridStabilityData(
                timestamp=timestamp,
                frequency_hz=round(frequency_hz, 3),
                voltage_kv=round(voltage_kv, 1),
                power_flow_mw=round(power_flow_mw, 1),
                grid_load_percent=round(grid_load_percent, 1),
                stability_index=round(stability_index, 3),
                grid_area=grid_area,
                operator=f"Demo Grid Operator {i % 3 + 1}",
                source='Grid Stability (Demo)'
            ))
        
        logger.info(f"✅ Grid Stability Demo-Daten generiert: {len(demo_data)} Datenpunkte")
        return demo_data
    
    def get_all_grid_services(self, hours: int = 24) -> Dict:
        """Alle Smart Grid Services Daten abrufen"""
        logger.info(f"🔌 Lade Smart Grid Services Daten für {hours} Stunden...")
        
        result = {
            'services': {},
            'stability': [],
            'summary': {
                'total_services': 0,
                'total_power_mw': 0.0,
                'total_value_eur': 0.0,
                'avg_availability': 0.0,
                'services_active': 0
            },
            'status': 'success',
            'timestamp': datetime.now().isoformat()
        }
        
        for service_id, service_config in self.grid_services.items():
            if not service_config.get('active', False):
                continue
            
            try:
                logger.info(f"🔌 Lade {service_config['name']} Daten...")
                
                if service_id == 'fcr':
                    data = self.get_fcr_data(hours)
                elif service_id == 'afrr':
                    data = self.get_afrr_data(hours)
                elif service_id == 'mfrr':
                    data = self.get_mfrr_data(hours)
                elif service_id == 'voltage':
                    data = self.get_voltage_control_data(hours)
                elif service_id == 'demand_response':
                    data = self.get_demand_response_data(hours)
                else:
                    continue
                
                if data:
                    result['services'][service_id] = {
                        'name': service_config['name'],
                        'description': service_config['description'],
                        'data': data,
                        'count': len(data),
                        'total_power': sum(d.power_mw for d in data),
                        'total_value': sum(d.power_mw * d.price_eur_mw for d in data),
                        'avg_price': sum(d.price_eur_mw for d in data) / len(data) if data else 0,
                        'avg_availability': sum(d.availability for d in data) / len(data) if data else 0
                    }
                    
                    # Summary aktualisieren
                    result['summary']['total_services'] += len(data)
                    result['summary']['total_power_mw'] += sum(d.power_mw for d in data)
                    result['summary']['total_value_eur'] += sum(d.power_mw * d.price_eur_mw for d in data)
                    result['summary']['services_active'] += 1
                    
                    logger.info(f"✅ {service_config['name']}: {len(data)} Services, {sum(d.power_mw for d in data):.1f} MW")
                
            except Exception as e:
                logger.error(f"❌ Fehler bei {service_config['name']}: {e}")
        
        # Grid Stability Daten
        try:
            stability_data = self.get_grid_stability_data(hours)
            if stability_data:
                result['stability'] = stability_data
                result['summary']['avg_availability'] = sum(d.stability_index for d in stability_data) / len(stability_data)
                logger.info(f"✅ Grid Stability: {len(stability_data)} Datenpunkte")
        except Exception as e:
            logger.error(f"❌ Fehler bei Grid Stability: {e}")
        
        # Status prüfen
        if result['summary']['services_active'] == 0:
            result['status'] = 'error'
            result['message'] = 'Keine Smart Grid Services verfügbar'
        elif result['summary']['services_active'] < len(self.grid_services):
            result['status'] = 'partial'
            result['message'] = f'Nur {result["summary"]["services_active"]} von {len(self.grid_services)} Services verfügbar'
        
        logger.info(f"✅ Smart Grid Services Daten geladen: {result['summary']['total_services']} Services, {result['summary']['total_power_mw']:.1f} MW")
        return result
    
    def test_api_connection(self) -> Dict:
        """Test der Smart Grid API-Verbindungen"""
        logger.info("🔍 Teste Smart Grid API Verbindungen...")
        
        result = {
            'status': 'not_configured',
            'message': 'Keine API-Keys konfiguriert',
            'services': {},
            'demo_available': True
        }
        
        configured_services = 0
        working_services = 0
        
        for service_id, service_config in self.grid_services.items():
            # Test mit Demo-Daten
            test_data = self._generate_demo_grid_service_data(service_id, 1)
            if test_data:
                working_services += 1
                result['services'][service_id] = {
                    'name': service_config['name'],
                    'status': 'demo',
                    'message': f'Demo-Modus - {len(test_data)} Test-Datenpunkte'
                }
            else:
                result['services'][service_id] = {
                    'name': service_config['name'],
                    'status': 'error',
                    'message': 'Demo-Modus nicht verfügbar'
                }
        
        # Grid Stability Test
        stability_test = self._generate_demo_grid_stability_data(1)
        if stability_test:
            result['stability'] = {
                'status': 'demo',
                'message': f'Demo-Modus - {len(stability_test)} Test-Datenpunkte'
            }
        
        # Gesamtstatus bestimmen
        if working_services > 0:
            result['status'] = 'demo'
            result['message'] = f'Demo-Modus für {working_services} Services verfügbar'
        
        logger.info(f"🔍 Smart Grid API-Test abgeschlossen: {result['status']}")
        return result

def main():
    """Test-Funktion"""
    print("🔌 Smart Grid Fetcher Test")
    print("=" * 50)
    
    fetcher = SmartGridFetcher()
    
    # API-Verbindungen testen
    test_result = fetcher.test_api_connection()
    print(f"API-Test: {test_result['status']}")
    print(f"Message: {test_result['message']}")
    
    # Alle Services testen
    print("\n🔌 Smart Grid Services:")
    for service_id, service_info in test_result['services'].items():
        print(f"  {service_info['name']}: {service_info['status']} - {service_info['message']}")
    
    # Demo-Daten für alle Services abrufen
    print("\n🔌 Demo-Daten für alle Services:")
    all_data = fetcher.get_all_grid_services(24)
    
    print(f"Status: {all_data['status']}")
    print(f"Services aktiv: {all_data['summary']['services_active']}")
    print(f"Gesamt Services: {all_data['summary']['total_services']}")
    print(f"Gesamt Power: {all_data['summary']['total_power_mw']:.1f} MW")
    print(f"Gesamt Wert: {all_data['summary']['total_value_eur']:.2f} €")
    print(f"Grid Stability: {len(all_data['stability'])} Datenpunkte")

if __name__ == "__main__":
    main()
