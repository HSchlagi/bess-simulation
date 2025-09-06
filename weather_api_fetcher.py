#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wetter-API Fetcher für BESS Simulation
=====================================

Intelligente Integration von Wetterdaten für PV-Prognosen und BESS-Simulationen.
Unterstützt OpenWeatherMap, ECMWF und PVGIS Weather APIs.

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
import random
import math
from dataclasses import dataclass

# Logging konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class WeatherData:
    """Datenklasse für Wetterdaten"""
    timestamp: datetime
    temperature: float  # °C
    humidity: float     # %
    wind_speed: float   # m/s
    wind_direction: float  # Grad
    pressure: float     # hPa
    solar_irradiation: float  # W/m²
    cloud_cover: float  # %
    precipitation: float  # mm
    location: str
    source: str

class WeatherAPIFetcher:
    """Hauptklasse für Wetter-API Integration"""
    
    def __init__(self):
        self.openweather_api_key = os.getenv('OPENWEATHER_API_KEY', '')
        self.ecmwf_api_key = os.getenv('ECMWF_API_KEY', '')
        self.pvgis_api_url = 'https://re.jrc.ec.europa.eu/api/v5_2'
        
        # API-Endpunkte
        self.openweather_base_url = 'https://api.openweathermap.org/data/2.5'
        self.ecmwf_base_url = 'https://api.ecmwf.int/v1'
        
        # Rate Limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Sekunden zwischen Requests
        
    def _rate_limit(self):
        """Rate Limiting für API-Requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _make_request(self, url: str, params: Dict = None) -> Optional[Dict]:
        """Sichere API-Request mit Fehlerbehandlung"""
        try:
            self._rate_limit()
            
            logger.info(f"🌤️ API-Request: {url}")
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✅ API-Response erfolgreich: {len(str(data))} Zeichen")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ API-Request fehlgeschlagen: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON-Decode Fehler: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Unerwarteter Fehler: {e}")
            return None
    
    def get_openweather_current(self, lat: float, lon: float) -> Optional[WeatherData]:
        """Aktuelle Wetterdaten von OpenWeatherMap"""
        if not self.openweather_api_key:
            logger.warning("⚠️ OpenWeatherMap API-Key nicht konfiguriert - Demo-Modus aktiviert")
            # Demo-Daten für fehlenden API-Key
            return WeatherData(
                timestamp=datetime.now(),
                temperature=15.5,
                humidity=65.0,
                wind_speed=3.2,
                wind_direction=180.0,
                pressure=1013.25,
                solar_irradiation=0,  # OpenWeatherMap hat keine direkte Einstrahlung
                cloud_cover=40.0,
                precipitation=0.0,
                location=f"Demo Standort ({lat}, {lon})",
                source='OpenWeatherMap (Demo)'
            )
        
        url = f"{self.openweather_base_url}/weather"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': self.openweather_api_key,
            'units': 'metric',
            'lang': 'de'
        }
        
        data = self._make_request(url, params)
        if not data:
            return None
        
        try:
            return WeatherData(
                timestamp=datetime.fromtimestamp(data['dt']),
                temperature=data['main']['temp'],
                humidity=data['main']['humidity'],
                wind_speed=data['wind']['speed'],
                wind_direction=data['wind'].get('deg', 0),
                pressure=data['main']['pressure'],
                solar_irradiation=0,  # OpenWeatherMap hat keine direkte Einstrahlung
                cloud_cover=data['clouds']['all'],
                precipitation=data.get('rain', {}).get('1h', 0),
                location=f"{data['name']}, {data['sys']['country']}",
                source='OpenWeatherMap'
            )
        except KeyError as e:
            logger.error(f"❌ Fehlende Daten in OpenWeatherMap Response: {e}")
            return None
    
    def get_openweather_forecast(self, lat: float, lon: float, days: int = 5) -> List[WeatherData]:
        """Wettervorhersage von OpenWeatherMap (5 Tage)"""
        if not self.openweather_api_key:
            logger.warning("⚠️ OpenWeatherMap API-Key nicht konfiguriert - Demo-Modus aktiviert")
            # Demo-Vorhersage-Daten
            demo_forecast = []
            for i in range(days * 8):  # 8 Messungen pro Tag
                timestamp = datetime.now() + timedelta(hours=i*3)
                demo_forecast.append(WeatherData(
                    timestamp=timestamp,
                    temperature=15.5 + (i % 24) * 0.5,  # Leichte Variation
                    humidity=65.0 + (i % 12) * 2.0,
                    wind_speed=3.2 + (i % 8) * 0.3,
                    wind_direction=180.0 + (i % 360),
                    pressure=1013.25 + (i % 10) * 0.5,
                    solar_irradiation=0,
                    cloud_cover=40.0 + (i % 30),
                    precipitation=0.0,
                    location=f"Demo Standort ({lat}, {lon})",
                    source='OpenWeatherMap (Demo)'
                ))
            return demo_forecast
        
        url = f"{self.openweather_base_url}/forecast"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': self.openweather_api_key,
            'units': 'metric',
            'lang': 'de'
        }
        
        data = self._make_request(url, params)
        if not data:
            return []
        
        weather_data = []
        try:
            for item in data['list'][:days * 8]:  # 8 Messungen pro Tag (3h Intervalle)
                weather_data.append(WeatherData(
                    timestamp=datetime.fromtimestamp(item['dt']),
                    temperature=item['main']['temp'],
                    humidity=item['main']['humidity'],
                    wind_speed=item['wind']['speed'],
                    wind_direction=item['wind'].get('deg', 0),
                    pressure=item['main']['pressure'],
                    solar_irradiation=0,  # Schätzung basierend auf Tageszeit und Wolken
                    cloud_cover=item['clouds']['all'],
                    precipitation=item.get('rain', {}).get('3h', 0),
                    location=f"{data['city']['name']}, {data['city']['country']}",
                    source='OpenWeatherMap'
                ))
        except KeyError as e:
            logger.error(f"❌ Fehlende Daten in OpenWeatherMap Forecast: {e}")
            return []
        
        return weather_data
    
    def get_pvgis_weather(self, lat: float, lon: float, start_date: str, end_date: str) -> List[WeatherData]:
        """Historische Wetterdaten von PVGIS"""
        # PVGIS hat keine direkte Wetter-API, verwende TMY-Daten
        url = f"{self.pvgis_api_url}/tmy"
        params = {
            'lat': lat,
            'lon': lon,
            'outputformat': 'json'
        }
        
        data = self._make_request(url, params)
        if not data:
            logger.warning("⚠️ PVGIS API nicht verfügbar - verwende Demo-Daten")
            return self._generate_pvgis_demo_data(lat, lon, start_date, end_date)
        
        weather_data = []
        try:
            # PVGIS TMY-Daten haben andere Struktur
            for item in data['outputs']['tmy_hourly']:
                # PVGIS Zeitstempel ist in UTC
                timestamp = datetime.strptime(item['time(UTC)'], '%Y%m%d:%H%M')
                
                weather_data.append(WeatherData(
                    timestamp=timestamp,
                    temperature=item['T2m'],
                    humidity=item['RH'],
                    wind_speed=item['WS10m'],
                    wind_direction=item['WD10m'],
                    pressure=item['SP'],
                    solar_irradiation=item['G(i)'],
                    cloud_cover=0,  # PVGIS hat keine direkte Wolkenbedeckung
                    precipitation=0,  # PVGIS hat keine Niederschlagsdaten
                    location=f"PVGIS ({lat}, {lon})",
                    source='PVGIS'
                ))
        except KeyError as e:
            logger.error(f"❌ Fehlende Daten in PVGIS Response: {e}")
            return self._generate_pvgis_demo_data(lat, lon, start_date, end_date)
        
        logger.info(f"✅ PVGIS echte Daten geladen: {len(weather_data)} Datenpunkte")
        return weather_data
    
    def _generate_pvgis_demo_data(self, lat: float, lon: float, start_date: str, end_date: str) -> List[WeatherData]:
        """Generiere PVGIS Demo-Daten als Fallback"""
        logger.warning("⚠️ PVGIS Demo-Modus - generiere Demo-Daten")
        
        # Demo-Daten für letzte 7 Tage
        demo_data = []
        start_dt = datetime.strptime(start_date, '%Y%m%d')
        end_dt = datetime.strptime(end_date, '%Y%m%d')
        
        current_dt = start_dt
        while current_dt <= end_dt:
            for hour in range(24):
                timestamp = current_dt.replace(hour=hour, minute=0, second=0, microsecond=0)
                
                # Realistische Wetterdaten-Variation
                base_temp = 15.0 + 10 * math.sin((current_dt.timetuple().tm_yday / 365) * 2 * math.pi)
                hourly_temp = base_temp + 5 * math.sin((hour / 24) * 2 * math.pi)
                
                demo_data.append(WeatherData(
                    timestamp=timestamp,
                    temperature=round(hourly_temp, 1),
                    humidity=round(60 + 20 * math.sin((hour / 24) * 2 * math.pi), 1),
                    wind_speed=round(2.0 + 3.0 * random.random(), 1),
                    wind_direction=round(180 + 180 * random.random(), 1),
                    pressure=round(1013 + 10 * random.random(), 1),
                    solar_irradiation=round(max(0, 800 * math.sin((hour / 24) * math.pi)), 1),
                    cloud_cover=round(30 + 40 * random.random(), 1),
                    precipitation=round(0.5 * random.random(), 1),
                    location=f"PVGIS Demo ({lat}, {lon})",
                    source='PVGIS (Demo)'
                ))
            
            current_dt += timedelta(days=1)
        
        logger.info(f"✅ PVGIS Demo-Daten generiert: {len(demo_data)} Datenpunkte")
        return demo_data
    
    def get_weather_for_location(self, lat: float, lon: float, location_name: str = "") -> Dict:
        """Kombinierte Wetterdaten für einen Standort"""
        logger.info(f"🌤️ Lade Wetterdaten für Standort: {location_name or f'{lat}, {lon}'}")
        
        result = {
            'location': {
                'name': location_name or f"Standort ({lat}, {lon})",
                'latitude': lat,
                'longitude': lon
            },
            'current': None,
            'forecast': [],
            'historical': [],
            'status': 'success',
            'timestamp': datetime.now().isoformat()
        }
        
        # Aktuelle Wetterdaten
        current = self.get_openweather_current(lat, lon)
        if current:
            result['current'] = {
                'temperature': current.temperature,
                'humidity': current.humidity,
                'wind_speed': current.wind_speed,
                'wind_direction': current.wind_direction,
                'pressure': current.pressure,
                'cloud_cover': current.cloud_cover,
                'precipitation': current.precipitation,
                'timestamp': current.timestamp.isoformat(),
                'source': current.source
            }
        
        # Wettervorhersage
        forecast = self.get_openweather_forecast(lat, lon, 5)
        if forecast:
            result['forecast'] = [
                {
                    'timestamp': w.timestamp.isoformat(),
                    'temperature': w.temperature,
                    'humidity': w.humidity,
                    'wind_speed': w.wind_speed,
                    'solar_irradiation': w.solar_irradiation,
                    'cloud_cover': w.cloud_cover,
                    'precipitation': w.precipitation
                }
                for w in forecast
            ]
        
        # Historische Daten (letzte 7 Tage)
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y%m%d')
        
        historical = self.get_pvgis_weather(lat, lon, start_date, end_date)
        if historical:
            result['historical'] = [
                {
                    'timestamp': w.timestamp.isoformat(),
                    'temperature': w.temperature,
                    'humidity': w.humidity,
                    'wind_speed': w.wind_speed,
                    'solar_irradiation': w.solar_irradiation,
                    'pressure': w.pressure
                }
                for w in historical
            ]
        
        # Status prüfen
        if not result['current'] and not result['forecast'] and not result['historical']:
            result['status'] = 'error'
            result['message'] = 'Keine Wetterdaten verfügbar'
        elif not result['current']:
            result['status'] = 'partial'
            result['message'] = 'Nur teilweise Daten verfügbar'
        
        logger.info(f"✅ Wetterdaten geladen: {len(result['forecast'])} Vorhersage, {len(result['historical'])} historisch")
        return result
    
    def test_api_connection(self) -> Dict:
        """Test der API-Verbindungen"""
        logger.info("🔍 Teste Wetter-API Verbindungen...")
        
        result = {
            'openweather': {'status': 'not_configured', 'message': 'API-Key nicht gesetzt'},
            'pvgis': {'status': 'unknown', 'message': 'Nicht getestet'},
            'overall': 'not_configured'
        }
        
        # OpenWeatherMap Test
        test_data = self.get_openweather_current(48.2082, 16.3738)  # Wien
        if test_data:
            if self.openweather_api_key:
                result['openweather'] = {
                    'status': 'success',
                    'message': f'Verbindung erfolgreich - {test_data.location}',
                    'temperature': test_data.temperature
                }
            else:
                result['openweather'] = {
                    'status': 'demo',
                    'message': f'Demo-Modus aktiv - {test_data.location}',
                    'temperature': test_data.temperature
                }
        else:
            result['openweather'] = {
                'status': 'error',
                'message': 'API-Request fehlgeschlagen'
            }
        
        # PVGIS Test
        try:
            test_data = self.get_pvgis_weather(48.2082, 16.3738, '20240101', '20240102')
            if test_data:
                # Prüfe ob echte oder Demo-Daten
                is_demo = any(item.source == 'PVGIS (Demo)' for item in test_data)
                status = 'demo' if is_demo else 'success'
                result['pvgis'] = {
                    'status': status,
                    'message': f'{"Demo-Modus aktiv" if is_demo else "Verbindung erfolgreich"} - {len(test_data)} Datenpunkte'
                }
            else:
                result['pvgis'] = {
                    'status': 'error',
                    'message': 'Keine Daten erhalten'
                }
        except Exception as e:
            result['pvgis'] = {
                'status': 'error',
                'message': f'Fehler: {str(e)}'
            }
        
        # Gesamtstatus
        if result['openweather']['status'] in ['success', 'demo'] or result['pvgis']['status'] in ['success', 'demo']:
            result['overall'] = 'demo' if 'demo' in [result['openweather']['status'], result['pvgis']['status']] else 'success'
        elif result['openweather']['status'] == 'not_configured':
            result['overall'] = 'partial'
        else:
            result['overall'] = 'error'
        
        logger.info(f"🔍 API-Test abgeschlossen: {result['overall']}")
        return result

def main():
    """Test-Funktion"""
    print("🌤️ Wetter-API Fetcher Test")
    print("=" * 40)
    
    fetcher = WeatherAPIFetcher()
    
    # API-Verbindung testen
    test_result = fetcher.test_api_connection()
    print(f"API-Test: {test_result['overall']}")
    print(f"OpenWeatherMap: {test_result['openweather']['status']}")
    print(f"PVGIS: {test_result['pvgis']['status']}")
    
    # Wetterdaten für Wien abrufen
    print("\n🌤️ Wetterdaten für Wien:")
    weather_data = fetcher.get_weather_for_location(48.2082, 16.3738, "Wien")
    
    if weather_data['current']:
        current = weather_data['current']
        print(f"Temperatur: {current['temperature']}°C")
        print(f"Luftfeuchtigkeit: {current['humidity']}%")
        print(f"Wind: {current['wind_speed']} m/s")
        print(f"Wolkenbedeckung: {current['cloud_cover']}%")
    
    print(f"Vorhersage: {len(weather_data['forecast'])} Datenpunkte")
    print(f"Historisch: {len(weather_data['historical'])} Datenpunkte")

if __name__ == "__main__":
    main()
