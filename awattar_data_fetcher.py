#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
aWattar Data Fetcher für BESS Simulation
Integriert österreichische Strompreise von der aWattar API
"""

import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
from sqlalchemy import and_
from models import db, SpotPrice

logger = logging.getLogger(__name__)

class AWattarDataFetcher:
    """Fetcher für aWattar API-Daten"""
    
    def __init__(self):
        self.base_url = "https://api.awattar.at/v1/marketdata"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'BESS-Simulation/2.1 (https://bess.instanet.at)',
            'Accept': 'application/json'
        })
    
    def fetch_market_data(self, start_date: Optional[datetime] = None, 
                         end_date: Optional[datetime] = None) -> Dict:
        """
        Holt Marktdaten von der aWattar API
        
        Args:
            start_date: Startdatum (optional, Standard: heute)
            end_date: Enddatum (optional, Standard: heute + 1 Tag)
            
        Returns:
            Dict mit API-Response oder Fehler-Info
        """
        try:
            # Standard-Parameter setzen
            if not start_date:
                start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            if not end_date:
                end_date = start_date + timedelta(days=1)
            
            # URL-Parameter für aWattar API
            params = {
                'start': int(start_date.timestamp() * 1000),  # Millisekunden
                'end': int(end_date.timestamp() * 1000)
            }
            
            logger.info(f"Fetching aWattar data from {start_date} to {end_date}")
            
            response = self.session.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully fetched {len(data.get('data', []))} price points")
            
            return {
                'success': True,
                'data': data,
                'fetched_at': datetime.now(),
                'start_date': start_date,
                'end_date': end_date
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return {
                'success': False,
                'error': f"API request failed: {str(e)}",
                'fetched_at': datetime.now()
            }
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return {
                'success': False,
                'error': f"JSON decode error: {str(e)}",
                'fetched_at': datetime.now()
            }
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {
                'success': False,
                'error': f"Unexpected error: {str(e)}",
                'fetched_at': datetime.now()
            }
    
    def parse_market_data(self, api_response: Dict) -> List[Dict]:
        """
        Parst aWattar API-Response in Standard-Format
        
        Args:
            api_response: Response von fetch_market_data()
            
        Returns:
            List[Dict]: Liste von Spot-Preis-Daten
        """
        if not api_response.get('success'):
            return []
        
        market_data = api_response['data'].get('data', [])
        parsed_data = []
        
        for item in market_data:
            try:
                # Timestamp von Millisekunden zu datetime konvertieren
                start_timestamp = datetime.fromtimestamp(item['start_timestamp'] / 1000)
                end_timestamp = datetime.fromtimestamp(item['end_timestamp'] / 1000)
                
                parsed_item = {
                    'timestamp': start_timestamp,
                    'end_timestamp': end_timestamp,
                    'price_eur_mwh': float(item['marketprice']),
                    'source': 'aWATTAR (Live API)',
                    'region': 'AT',
                    'price_type': 'day_ahead',
                    'unit': item.get('unit', 'Eur/MWh')
                }
                parsed_data.append(parsed_item)
                
            except (KeyError, ValueError, TypeError) as e:
                logger.warning(f"Failed to parse market data item: {e}")
                continue
        
        logger.info(f"Parsed {len(parsed_data)} price points")
        return parsed_data
    
    def save_to_database(self, parsed_data: List[Dict], 
                        app_context=None) -> Dict:
        """
        Speichert geparste Daten in der Datenbank
        
        Args:
            parsed_data: Liste von geparsten Spot-Preis-Daten
            app_context: Flask App Context (optional)
            
        Returns:
            Dict: Ergebnis der Speicherung
        """
        if not parsed_data:
            return {
                'success': False,
                'error': 'No data to save',
                'saved_count': 0
            }
        
        try:
            saved_count = 0
            skipped_count = 0
            error_count = 0
            
            for item in parsed_data:
                try:
                    # Prüfen ob Datensatz bereits existiert
                    existing = SpotPrice.query.filter(
                        and_(
                            SpotPrice.timestamp == item['timestamp'],
                            SpotPrice.source == item['source'],
                            SpotPrice.region == item['region']
                        )
                    ).first()
                    
                    if existing:
                        # Aktualisieren falls Preis sich geändert hat
                        if existing.price_eur_mwh != item['price_eur_mwh']:
                            existing.price_eur_mwh = item['price_eur_mwh']
                            existing.created_at = datetime.utcnow()
                            logger.debug(f"Updated price for {item['timestamp']}")
                        else:
                            skipped_count += 1
                            continue
                    else:
                        # Neuen Datensatz erstellen
                        spot_price = SpotPrice(
                            timestamp=item['timestamp'],
                            price_eur_mwh=item['price_eur_mwh'],
                            source=item['source'],
                            region=item['region'],
                            price_type=item['price_type']
                        )
                        db.session.add(spot_price)
                    
                    saved_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to save price data: {e}")
                    error_count += 1
                    continue
            
            # Transaktion committen
            db.session.commit()
            
            logger.info(f"Saved {saved_count} price points, skipped {skipped_count}, errors {error_count}")
            
            return {
                'success': True,
                'saved_count': saved_count,
                'skipped_count': skipped_count,
                'error_count': error_count,
                'total_processed': len(parsed_data)
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Database transaction failed: {e}")
            return {
                'success': False,
                'error': f"Database transaction failed: {str(e)}",
                'saved_count': 0
            }
    
    def fetch_and_save(self, start_date: Optional[datetime] = None,
                      end_date: Optional[datetime] = None,
                      app_context=None) -> Dict:
        """
        Kompletter Workflow: Daten holen, parsen und speichern
        
        Args:
            start_date: Startdatum (optional)
            end_date: Enddatum (optional)
            app_context: Flask App Context (optional)
            
        Returns:
            Dict: Vollständiges Ergebnis
        """
        logger.info("Starting aWattar fetch and save workflow")
        
        # 1. Daten von API holen
        api_response = self.fetch_market_data(start_date, end_date)
        
        if not api_response['success']:
            return {
                'success': False,
                'error': api_response['error'],
                'step': 'api_fetch'
            }
        
        # 2. Daten parsen
        parsed_data = self.parse_market_data(api_response)
        
        if not parsed_data:
            return {
                'success': False,
                'error': 'No data could be parsed from API response',
                'step': 'parsing'
            }
        
        # 3. In Datenbank speichern
        save_result = self.save_to_database(parsed_data, app_context)
        
        if not save_result['success']:
            return {
                'success': False,
                'error': save_result['error'],
                'step': 'database_save'
            }
        
        # 4. Erfolgreiches Ergebnis zusammenstellen
        return {
            'success': True,
            'api_response': api_response,
            'parsed_count': len(parsed_data),
            'save_result': save_result,
            'fetched_at': datetime.now()
        }
    
    def get_latest_prices(self, hours: int = 24) -> List[Dict]:
        """
        Holt die neuesten Preise aus der Datenbank
        
        Args:
            hours: Anzahl der Stunden zurück
            
        Returns:
            List[Dict]: Neueste Spot-Preise
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            prices = SpotPrice.query.filter(
                and_(
                    SpotPrice.source == 'aWATTAR',
                    SpotPrice.timestamp >= cutoff_time
                )
            ).order_by(SpotPrice.timestamp.desc()).all()
            
            return [{
                'id': price.id,
                'timestamp': price.timestamp.isoformat(),
                'price_eur_mwh': price.price_eur_mwh,
                'source': price.source,
                'region': price.region,
                'price_type': price.price_type,
                'created_at': price.created_at.isoformat() if price.created_at else None
            } for price in prices]
            
        except Exception as e:
            logger.error(f"Failed to get latest prices: {e}")
            return []
    
    def get_prices_for_range(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Holt Preise für einen spezifischen Datumsbereich aus der Datenbank
        
        Args:
            start_date: Startdatum (YYYY-MM-DD)
            end_date: Enddatum (YYYY-MM-DD)
            
        Returns:
            List[Dict]: Spot-Preise für den Zeitraum
        """
        try:
            # Datumsstrings zu datetime-Objekten konvertieren
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)  # +1 Tag für Enddatum
            
            prices = SpotPrice.query.filter(
                and_(
                    SpotPrice.source == 'aWATTAR',
                    SpotPrice.timestamp >= start_dt,
                    SpotPrice.timestamp < end_dt
                )
            ).order_by(SpotPrice.timestamp.asc()).all()
            
            logger.info(f"Retrieved {len(prices)} prices for range {start_date} to {end_date}")
            
            return [{
                'id': price.id,
                'timestamp': price.timestamp.isoformat(),
                'price_eur_mwh': price.price_eur_mwh,
                'source': price.source,
                'region': price.region,
                'price_type': price.price_type,
                'created_at': price.created_at.isoformat() if price.created_at else None
            } for price in prices]
            
        except Exception as e:
            logger.error(f"Failed to get prices for range {start_date} to {end_date}: {e}")
            return []


# Globale Instanz für einfache Verwendung
awattar_fetcher = AWattarDataFetcher()


def test_awattar_integration():
    """Test-Funktion für aWattar Integration"""
    print("Testing aWattar API Integration...")
    
    # 1. API-Test
    print("\n1. Testing API connection...")
    api_response = awattar_fetcher.fetch_market_data()
    
    if api_response['success']:
        print(f"✅ API connection successful")
        print(f"   Fetched {len(api_response['data'].get('data', []))} price points")
    else:
        print(f"❌ API connection failed: {api_response['error']}")
        return False
    
    # 2. Parsing-Test
    print("\n2. Testing data parsing...")
    parsed_data = awattar_fetcher.parse_market_data(api_response)
    
    if parsed_data:
        print(f"✅ Data parsing successful")
        print(f"   Parsed {len(parsed_data)} price points")
        print(f"   Sample: {parsed_data[0]}")
    else:
        print(f"❌ Data parsing failed")
        return False
    
    # 3. Datenbank-Test (nur wenn Flask-App verfügbar)
    print("\n3. Testing database integration...")
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            save_result = awattar_fetcher.save_to_database(parsed_data[:5])  # Nur 5 Test-Datensätze
            
            if save_result['success']:
                print(f"✅ Database integration successful")
                print(f"   Saved {save_result['saved_count']} price points")
            else:
                print(f"❌ Database integration failed: {save_result['error']}")
                return False
                
    except ImportError:
        print("⚠️  Flask app not available, skipping database test")
    
    print("\n🎉 aWattar integration test completed successfully!")
    return True


if __name__ == "__main__":
    # Test ausführen wenn direkt aufgerufen
    test_awattar_integration()
