#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ENTSO-E API Fetcher für BESS Simulation
======================================

Integration der ENTSO-E Transparency Platform für europäische Strommarkt-Daten.
Unterstützt Day-Ahead Prices, Intraday Prices, Generation, Load und Balancing.

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
import xml.etree.ElementTree as ET
from dataclasses import dataclass

# Logging konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ENTSOEData:
    """Datenklasse für ENTSO-E Daten"""
    timestamp: datetime
    price_eur_mwh: float
    country_code: str
    market_type: str  # 'day_ahead', 'intraday', 'balancing'
    data_type: str    # 'price', 'generation', 'load'
    source: str

class ENTSOEAPIFetcher:
    """Hauptklasse für ENTSO-E API Integration"""
    
    def __init__(self, api_key: Optional[str] = None):
        env_token = os.getenv('ENTSOE_API_KEY', '')
        self.api_key = api_key or env_token or ''
        self.demo_mode = not bool(self.api_key)
        self.base_url = 'https://web-api.tp.entsoe.eu/api'
        
        # Rate Limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Sekunden zwischen Requests
        
        # Länder-Codes für Österreich und Nachbarländer
        self.countries = {
            'AT': 'Austria',
            'DE': 'Germany', 
            'CH': 'Switzerland',
            'IT': 'Italy',
            'CZ': 'Czech Republic',
            'SK': 'Slovakia',
            'HU': 'Hungary',
            'SI': 'Slovenia'
        }

        self.bidding_zones = {
            'AT': '10YAT-APG------L',
            'DE': '10Y1001A1001A83F',
            'DE-LU': '10Y1001A1001A82H',
            'CH': '10YCH-SWISSGRIDZ',
            'IT': '10YIT-GRTN-----B',
            'CZ': '10YCZ-CEPS-----N',
            'SK': '10YSK-SEPS-----K',
            'HU': '10YHU-MAVIR----U',
            'SI': '10YSI-ELES-----O'
        }
        
        # Market Types
        self.market_types = {
            'day_ahead': 'A44',      # Day-ahead prices
            'intraday': 'A69',       # Intraday prices
            'generation': 'A75',     # Generation
            'load': 'A65',           # Load
            'balancing': 'A85'       # Balancing
        }
    
    def _rate_limit(self):
        """Rate Limiting für API-Requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _make_request(self, url: str, params: Dict = None) -> Optional[str]:
        """Sichere API-Request mit Fehlerbehandlung"""
        try:
            self._rate_limit()
            
            logger.info(f"🌍 ENTSO-E API-Request: {url}")
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            logger.info(f"✅ ENTSO-E API-Response erfolgreich: {len(response.text)} Zeichen")
            return response.text
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ ENTSO-E API-Request fehlgeschlagen: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Unerwarteter Fehler: {e}")
            return None
    
    def _parse_xml_response(self, xml_content: str) -> List[ENTSOEData]:
        """Parse ENTSO-E XML Response"""
        try:
            root = ET.fromstring(xml_content)
            data_points = []
            
            default_ns = root.tag.split('}')[0].strip('{')
            ns = {'ns': default_ns}
            
            for timeseries in root.findall('.//ns:TimeSeries', ns):
                market_type = 'unknown'
                business = timeseries.find('.//ns:businessType', ns)
                if business is not None and business.text:
                    market_type = business.text
                
                country_code = 'AT'
                bidding_zone = timeseries.find('.//ns:outBiddingZone_Domain.mRID', ns)
                if bidding_zone is None:
                    bidding_zone = timeseries.find('.//ns:in_Domain.mRID', ns)
                if bidding_zone is not None and bidding_zone.text:
                    zone_text = bidding_zone.text
                    if zone_text.startswith('10Y') and '-' in zone_text:
                        country_code = zone_text[2:4]
                    elif len(zone_text) >= 2:
                        country_code = zone_text[:2]
                
                periods = timeseries.findall('.//ns:Period', ns)
                if not periods:
                    periods = timeseries.findall('.//ns:period', ns)
                
                for period in periods:
                    start_node = period.find('.//ns:start', ns)
                    resolution_node = period.find('.//ns:resolution', ns)
                    if start_node is None:
                        continue
                    start_dt = datetime.fromisoformat(start_node.text.replace('Z', '+00:00'))
                    
                    resolution = resolution_node.text if resolution_node is not None else 'PT60M'
                    if resolution == 'PT15M':
                        step = timedelta(minutes=15)
                    elif resolution == 'PT30M':
                        step = timedelta(minutes=30)
                    else:
                        step = timedelta(hours=1)
                    
                    points = period.findall('.//ns:Point', ns)
                    for point in points:
                        position_node = point.find('.//ns:position', ns)
                        price_node = point.find('.//ns:price.amount', ns)
                        quantity_node = point.find('.//ns:quantity', ns)
                        
                        price_text = None
                        if price_node is not None and price_node.text:
                            price_text = price_node.text
                        elif quantity_node is not None and quantity_node.text:
                            price_text = quantity_node.text
                        
                        if position_node is None or price_text is None:
                            continue
                        
                        position = int(position_node.text)
                        timestamp = start_dt + step * (position - 1)
                        
                        data_points.append(ENTSOEData(
                            timestamp=timestamp,
                            price_eur_mwh=float(price_text),
                            country_code=country_code,
                            market_type=market_type,
                            data_type='price',
                            source='ENTSO-E'
                        ))
            
            return data_points
            
        except ET.ParseError as e:
            logger.error(f"❌ XML Parse Fehler: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Unerwarteter Fehler beim XML-Parsing: {e}")
            return []
    
    def get_day_ahead_prices(self, country_code: str = 'AT', start_date: str = None, end_date: str = None) -> List[ENTSOEData]:
        """Day-Ahead Preise von ENTSO-E abrufen"""
        if not self.api_key:
            logger.warning("⚠️ ENTSO-E API-Key nicht konfiguriert - Demo-Modus aktiviert")
            return self._generate_demo_prices(country_code, 'day_ahead', start_date, end_date)
        
        if not start_date:
            start_date = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d%H%M')
        if not end_date:
            end_date = datetime.now().strftime('%Y%m%d%H%M')
        
        zone = self.bidding_zones.get(country_code, self.bidding_zones.get('AT'))

        url = f"{self.base_url}"
        params = {
            'securityToken': self.api_key,
            'documentType': self.market_types['day_ahead'],
            'in_Domain': zone,
            'out_Domain': zone,
            'periodStart': start_date,
            'periodEnd': end_date
        }
        
        xml_content = self._make_request(url, params)
        if not xml_content:
            logger.warning("⚠️ ENTSO-E API nicht verfügbar - verwende Demo-Daten")
            return self._generate_demo_prices(country_code, 'day_ahead', start_date, end_date)
        
        data_points = self._parse_xml_response(xml_content)
        logger.info(f"✅ ENTSO-E Day-Ahead Preise geladen: {len(data_points)} Datenpunkte")
        return data_points
    
    def get_intraday_prices(self, country_code: str = 'AT', start_date: str = None, end_date: str = None) -> List[ENTSOEData]:
        """Intraday Preise von ENTSO-E abrufen"""
        if not self.api_key:
            logger.warning("⚠️ ENTSO-E API-Key nicht konfiguriert - Demo-Modus aktiviert")
            return self._generate_demo_prices(country_code, 'intraday', start_date, end_date)
        
        if not start_date:
            start_date = (datetime.now() - timedelta(hours=6)).strftime('%Y%m%d%H%M')
        if not end_date:
            end_date = datetime.now().strftime('%Y%m%d%H%M')
        
        zone = self.bidding_zones.get(country_code, self.bidding_zones.get('AT'))

        url = f"{self.base_url}"
        params = {
            'securityToken': self.api_key,
            'documentType': self.market_types['intraday'],
            'in_Domain': zone,
            'out_Domain': zone,
            'periodStart': start_date,
            'periodEnd': end_date
        }
        
        xml_content = self._make_request(url, params)
        if not xml_content:
            logger.warning("⚠️ ENTSO-E API nicht verfügbar - verwende Demo-Daten")
            return self._generate_demo_prices(country_code, 'intraday', start_date, end_date)
        
        data_points = self._parse_xml_response(xml_content)
        logger.info(f"✅ ENTSO-E Intraday Preise geladen: {len(data_points)} Datenpunkte")
        return data_points
    
    def get_generation_data(self, country_code: str = 'AT', start_date: str = None, end_date: str = None) -> List[ENTSOEData]:
        """Generation-Daten von ENTSO-E abrufen"""
        if not self.api_key:
            logger.warning("⚠️ ENTSO-E API-Key nicht konfiguriert - Demo-Modus aktiviert")
            return self._generate_demo_generation(country_code, start_date, end_date)
        
        if not start_date:
            start_date = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d%H%M')
        if not end_date:
            end_date = datetime.now().strftime('%Y%m%d%H%M')
        
        zone = self.bidding_zones.get(country_code, self.bidding_zones.get('AT'))

        url = f"{self.base_url}"
        params = {
            'securityToken': self.api_key,
            'documentType': self.market_types['generation'],
            'in_Domain': zone,
            'out_Domain': zone,
            'periodStart': start_date,
            'periodEnd': end_date
        }
        
        xml_content = self._make_request(url, params)
        if not xml_content:
            logger.warning("⚠️ ENTSO-E API nicht verfügbar - verwende Demo-Daten")
            return self._generate_demo_generation(country_code, start_date, end_date)
        
        data_points = self._parse_xml_response(xml_content)
        logger.info(f"✅ ENTSO-E Generation-Daten geladen: {len(data_points)} Datenpunkte")
        return data_points
    
    def _generate_demo_prices(self, country_code: str, market_type: str, start_date: str = None, end_date: str = None) -> List[ENTSOEData]:
        """Generiere Demo-Preise für ENTSO-E"""
        logger.warning(f"⚠️ ENTSO-E Demo-Modus - generiere {market_type} Preise für {country_code}")
        
        # Demo-Daten für letzte 24 Stunden
        demo_data = []
        start_dt = datetime.now() - timedelta(hours=24)
        
        for i in range(24):
            timestamp = start_dt + timedelta(hours=i)
            
            # Realistische Preis-Variation basierend auf Tageszeit
            base_price = 80.0  # €/MWh
            hourly_variation = 20 * (i % 12 - 6) / 6  # -20 bis +20
            market_variation = 10 if market_type == 'intraday' else 0
            
            price = base_price + hourly_variation + market_variation + (i % 3) * 5
            
            demo_data.append(ENTSOEData(
                timestamp=timestamp,
                price_eur_mwh=round(price, 2),
                country_code=country_code,
                market_type=market_type,
                data_type='price',
                source='ENTSO-E (Demo)'
            ))
        
        logger.info(f"✅ ENTSO-E Demo-Preise generiert: {len(demo_data)} Datenpunkte")
        return demo_data
    
    def _generate_demo_generation(self, country_code: str, start_date: str = None, end_date: str = None) -> List[ENTSOEData]:
        """Generiere Demo-Generation-Daten für ENTSO-E"""
        logger.warning(f"⚠️ ENTSO-E Demo-Modus - generiere Generation-Daten für {country_code}")
        
        # Demo-Daten für letzte 24 Stunden
        demo_data = []
        start_dt = datetime.now() - timedelta(hours=24)
        
        for i in range(24):
            timestamp = start_dt + timedelta(hours=i)
            
            # Realistische Generation-Variation
            base_generation = 5000.0  # MW
            hourly_variation = 1000 * (i % 12 - 6) / 6  # -1000 bis +1000
            
            generation = base_generation + hourly_variation + (i % 4) * 200
            
            demo_data.append(ENTSOEData(
                timestamp=timestamp,
                price_eur_mwh=round(generation, 1),  # Verwende price_eur_mwh für Generation MW
                country_code=country_code,
                market_type='generation',
                data_type='generation',
                source='ENTSO-E (Demo)'
            ))
        
        logger.info(f"✅ ENTSO-E Demo-Generation generiert: {len(demo_data)} Datenpunkte")
        return demo_data
    
    def get_market_data(self, country_code: str = 'AT', data_type: str = 'day_ahead', hours: int = 24) -> Dict:
        """Kombinierte Marktdaten für ein Land abrufen"""
        logger.info(f"🌍 Lade ENTSO-E Marktdaten für {country_code} ({data_type})")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(hours=hours)
        
        result = {
            'country': {
                'code': country_code,
                'name': self.countries.get(country_code, country_code)
            },
            'data_type': data_type,
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
                'hours': hours
            },
            'prices': [],
            'generation': [],
            'status': 'success',
            'timestamp': datetime.now().isoformat()
        }
        
        # Preise abrufen
        if data_type in ['day_ahead', 'both']:
            prices = self.get_day_ahead_prices(country_code, 
                                             start_date.strftime('%Y%m%d%H%M'),
                                             end_date.strftime('%Y%m%d%H%M'))
            result['prices'].extend(prices)
        
        if data_type in ['intraday', 'both']:
            intraday_prices = self.get_intraday_prices(country_code,
                                                     start_date.strftime('%Y%m%d%H%M'),
                                                     end_date.strftime('%Y%m%d%H%M'))
            result['prices'].extend(intraday_prices)
        
        # Generation abrufen
        if data_type in ['generation', 'both']:
            generation = self.get_generation_data(country_code,
                                                start_date.strftime('%Y%m%d%H%M'),
                                                end_date.strftime('%Y%m%d%H%M'))
            result['generation'].extend(generation)
        
        # Status prüfen
        if not result['prices'] and not result['generation']:
            result['status'] = 'error'
            result['message'] = 'Keine ENTSO-E Daten verfügbar'
        elif not result['prices'] or not result['generation']:
            result['status'] = 'partial'
            result['message'] = 'Nur teilweise Daten verfügbar'
        
        logger.info(f"✅ ENTSO-E Marktdaten geladen: {len(result['prices'])} Preise, {len(result['generation'])} Generation")
        return result
    
    def test_api_connection(self) -> Dict:
        """Test der ENTSO-E API-Verbindung"""
        logger.info("🔍 Teste ENTSO-E API Verbindung...")
        
        result = {
            'status': 'not_configured',
            'message': 'API-Key nicht gesetzt',
            'countries_available': list(self.countries.keys()),
            'market_types': list(self.market_types.keys())
        }
        
        if self.api_key:
            # Test mit Österreich Day-Ahead Preisen
            test_data = self.get_day_ahead_prices('AT')
            if test_data:
                result['status'] = 'success'
                result['message'] = f'Verbindung erfolgreich - {len(test_data)} Datenpunkte'
                result['sample_price'] = test_data[0].price_eur_mwh if test_data else None
            else:
                result['status'] = 'demo'
                result['message'] = 'API-Key gesetzt, aber Demo-Modus aktiv'
        else:
            # Test Demo-Modus
            test_data = self.get_day_ahead_prices('AT')
            if test_data:
                result['status'] = 'demo'
                result['message'] = f'Demo-Modus aktiv - {len(test_data)} Datenpunkte'
                result['sample_price'] = test_data[0].price_eur_mwh if test_data else None
        
        logger.info(f"🔍 ENTSO-E API-Test abgeschlossen: {result['status']}")
        return result

def main():
    """Test-Funktion"""
    print("🌍 ENTSO-E API Fetcher Test")
    print("=" * 40)
    
    fetcher = ENTSOEAPIFetcher()
    
    # API-Verbindung testen
    test_result = fetcher.test_api_connection()
    print(f"API-Test: {test_result['status']}")
    print(f"Message: {test_result['message']}")
    
    # Marktdaten für Österreich abrufen
    print("\n🌍 Marktdaten für Österreich:")
    market_data = fetcher.get_market_data('AT', 'day_ahead', 24)
    
    if market_data['prices']:
        prices = market_data['prices']
        print(f"Preise: {len(prices)} Datenpunkte")
        print(f"Neuester Preis: {prices[-1].price_eur_mwh} €/MWh")
        print(f"Zeitraum: {prices[0].timestamp} - {prices[-1].timestamp}")
    
    if market_data['generation']:
        generation = market_data['generation']
        print(f"Generation: {len(generation)} Datenpunkte")
        print(f"Neueste Generation: {generation[-1].price_eur_mwh} MW")

if __name__ == "__main__":
    main()
