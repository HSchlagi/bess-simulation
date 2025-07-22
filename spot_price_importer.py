#!/usr/bin/env python3
"""
Spot-Preis Importer für BESS Simulation
Integriert verschiedene Datenquellen für Strom-Spot-Preise
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import logging
from typing import List, Dict, Tuple, Optional
from app import db
from models import SpotPrice, SpotPriceConfig, EconomicAnalysis, Project

# Logging konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SpotPriceAPI:
    """API-Integration für verschiedene Spot-Preis Quellen"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'BESS-Simulation/1.0'
        })
    
    def fetch_entsoe_prices(self, date: datetime, region: str = 'AT') -> List[Dict]:
        """ENTSO-E Transparency Platform API"""
        try:
            # ENTSO-E API Endpoint
            base_url = "https://transparency.entsoe.eu/api"
            
            # Parameter für Day-Ahead Preise
            params = {
                'securityToken': 'YOUR_API_KEY',  # Muss konfiguriert werden
                'documentType': 'A44',
                'in_Domain': f'10Y1001A1001A83F',  # Österreich
                'out_Domain': f'10Y1001A1001A83F',
                'periodStart': date.strftime('%Y%m%d0000'),
                'periodEnd': (date + timedelta(days=1)).strftime('%Y%m%d0000')
            }
            
            response = self.session.get(base_url, params=params)
            response.raise_for_status()
            
            # XML zu DataFrame parsen (vereinfacht)
            # In der Praxis würde hier XML-Parsing implementiert
            logger.info(f"ENTSO-E Daten abgerufen für {date.date()}")
            
            # Mock-Daten für Demo
            return self._generate_mock_prices(date, 'ENTSO-E', region)
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen von ENTSO-E Daten: {e}")
            return []
    
    def fetch_apg_prices(self, date: datetime) -> List[Dict]:
        """Austrian Power Grid (APG) Daten"""
        try:
            # APG Marktdaten URL
            url = "https://www.apg.at/de/markt/marktdaten"
            
            # In der Praxis würde hier Web-Scraping oder API-Call implementiert
            logger.info(f"APG Daten abgerufen für {date.date()}")
            
            return self._generate_mock_prices(date, 'APG', 'AT')
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen von APG Daten: {e}")
            return []
    
    def fetch_epex_prices(self, date: datetime, region: str = 'AT') -> List[Dict]:
        """EPEX SPOT API (kostenpflichtig)"""
        try:
            # EPEX SPOT API Endpoint
            url = "https://api.epexspot.com/v1/market-data"
            
            # In der Praxis würde hier die echte EPEX API verwendet
            logger.info(f"EPEX Daten abgerufen für {date.date()}")
            
            return self._generate_mock_prices(date, 'EPEX', region)
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen von EPEX Daten: {e}")
            return []
    
    def _generate_mock_prices(self, date: datetime, source: str, region: str) -> List[Dict]:
        """Generiert Mock-Preisdaten für Demo-Zwecke"""
        prices = []
        
        # Realistische österreichische Spot-Preise (€/MWh)
        base_prices = [
            45, 42, 40, 38, 35, 32, 30, 28, 25, 22, 20, 18,  # Nacht (0-11h)
            20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75,  # Tag (12-23h)
        ]
        
        # Wochentag-Effekt
        weekday_factor = 1.1 if date.weekday() < 5 else 0.9  # Wochenende günstiger
        
        # Jahreszeit-Effekt
        month = date.month
        if month in [12, 1, 2]:  # Winter
            season_factor = 1.2
        elif month in [6, 7, 8]:  # Sommer
            season_factor = 0.9
        else:  # Übergangszeit
            season_factor = 1.0
        
        for hour in range(24):
            base_price = base_prices[hour]
            adjusted_price = base_price * weekday_factor * season_factor
            
            # Zufällige Variation (±10%)
            variation = np.random.normal(0, 0.05)
            final_price = adjusted_price * (1 + variation)
            
            timestamp = date.replace(hour=hour, minute=0, second=0, microsecond=0)
            
            prices.append({
                'timestamp': timestamp,
                'price_eur_mwh': round(final_price, 2),
                'source': source,
                'region': region,
                'price_type': 'day_ahead'
            })
        
        return prices

class SpotPriceProcessor:
    """Verarbeitung und Analyse von Spot-Preisdaten"""
    
    def __init__(self):
        self.low_price_threshold = 50   # €/MWh
        self.high_price_threshold = 100  # €/MWh
    
    def categorize_prices(self, prices: List[Dict]) -> Dict:
        """Kategorisiert Preise in Niedrig-, Mittel- und Hochpreis"""
        price_values = [p['price_eur_mwh'] for p in prices]
        
        low_prices = [p for p in price_values if p < self.low_price_threshold]
        medium_prices = [p for p in price_values if self.low_price_threshold <= p <= self.high_price_threshold]
        high_prices = [p for p in price_values if p > self.high_price_threshold]
        
        return {
            'low_prices': {
                'count': len(low_prices),
                'avg_price': np.mean(low_prices) if low_prices else 0,
                'hours': len(low_prices)
            },
            'medium_prices': {
                'count': len(medium_prices),
                'avg_price': np.mean(medium_prices) if medium_prices else 0,
                'hours': len(medium_prices)
            },
            'high_prices': {
                'count': len(high_prices),
                'avg_price': np.mean(high_prices) if high_prices else 0,
                'hours': len(high_prices)
            },
            'overall': {
                'avg_price': np.mean(price_values),
                'min_price': min(price_values),
                'max_price': max(price_values),
                'std_price': np.std(price_values)
            }
        }
    
    def calculate_arbitrage_potential(self, prices: List[Dict], bess_capacity_kwh: float, 
                                    bess_power_kw: float, efficiency: float = 0.9) -> Dict:
        """Berechnet Arbitrage-Potential für BESS"""
        
        # Preise sortieren
        sorted_prices = sorted(prices, key=lambda x: x['price_eur_mwh'])
        
        # Niedrigste 25% zum Laden, höchste 25% zum Entladen
        n_hours = len(sorted_prices)
        n_arbitrage_hours = n_hours // 4
        
        low_prices = sorted_prices[:n_arbitrage_hours]
        high_prices = sorted_prices[-n_arbitrage_hours:]
        
        avg_low_price = np.mean([p['price_eur_mwh'] for p in low_prices])
        avg_high_price = np.mean([p['price_eur_mwh'] for p in high_prices])
        
        price_spread = avg_high_price - avg_low_price
        
        # Arbitrage-Berechnung
        daily_cycles = min(n_arbitrage_hours, 24)  # Max 1 Zyklus pro Stunde
        daily_energy = bess_capacity_kwh * efficiency
        daily_revenue = daily_energy * price_spread / 1000  # MWh zu kWh
        
        annual_revenue = daily_revenue * 365
        optimal_cycles = daily_cycles * 365
        
        return {
            'price_spread_eur_mwh': round(price_spread, 2),
            'daily_revenue_eur': round(daily_revenue, 2),
            'annual_revenue_eur': round(annual_revenue, 2),
            'optimal_cycles_per_year': optimal_cycles,
            'avg_low_price': round(avg_low_price, 2),
            'avg_high_price': round(avg_high_price, 2),
            'arbitrage_hours_per_day': n_arbitrage_hours
        }
    
    def calculate_peak_shaving_potential(self, prices: List[Dict], bess_power_kw: float) -> Dict:
        """Berechnet Peak-Shaving Potential"""
        
        # Höchste Preise identifizieren (obere 20%)
        sorted_prices = sorted(prices, key=lambda x: x['price_eur_mwh'], reverse=True)
        n_peak_hours = max(1, len(sorted_prices) // 5)  # 20% der Stunden
        
        peak_prices = sorted_prices[:n_peak_hours]
        avg_peak_price = np.mean([p['price_eur_mwh'] for p in peak_prices])
        
        # Peak-Shaving Berechnung
        daily_peak_hours = n_peak_hours
        daily_savings = bess_power_kw * avg_peak_price / 1000  # kW zu MW
        annual_savings = daily_savings * 365
        
        return {
            'avg_peak_price_eur_mwh': round(avg_peak_price, 2),
            'peak_hours_per_day': daily_peak_hours,
            'daily_savings_eur': round(daily_savings, 2),
            'annual_savings_eur': round(annual_savings, 2),
            'peak_power_kw': bess_power_kw
        }
    
    def calculate_roi(self, annual_savings: float, total_investment: float, 
                     annual_operation_cost: float = 0) -> Dict:
        """Berechnet ROI und Payback-Periode"""
        
        net_annual_savings = annual_savings - annual_operation_cost
        
        if total_investment > 0:
            roi_percentage = (net_annual_savings / total_investment) * 100
            payback_years = total_investment / net_annual_savings
        else:
            roi_percentage = 0
            payback_years = float('inf')
        
        return {
            'total_investment_eur': total_investment,
            'annual_savings_eur': annual_savings,
            'net_annual_savings_eur': net_annual_savings,
            'roi_percentage': round(roi_percentage, 2),
            'payback_years': round(payback_years, 2)
        }

class SpotPriceImporter:
    """Hauptklasse für Spot-Preis Import und Verarbeitung"""
    
    def __init__(self):
        self.api = SpotPriceAPI()
        self.processor = SpotPriceProcessor()
    
    def import_daily_prices(self, date: datetime, source: str = 'ENTSO-E', region: str = 'AT') -> bool:
        """Importiert tägliche Spot-Preise"""
        try:
            # Bestehende Preise für das Datum löschen
            existing_prices = SpotPrice.query.filter(
                SpotPrice.timestamp >= date.replace(hour=0, minute=0, second=0),
                SpotPrice.timestamp < date.replace(hour=0, minute=0, second=0) + timedelta(days=1),
                SpotPrice.source == source,
                SpotPrice.region == region
            ).all()
            
            for price in existing_prices:
                db.session.delete(price)
            
            # Neue Preise abrufen
            if source == 'ENTSO-E':
                prices = self.api.fetch_entsoe_prices(date, region)
            elif source == 'APG':
                prices = self.api.fetch_apg_prices(date)
            elif source == 'EPEX':
                prices = self.api.fetch_epex_prices(date, region)
            else:
                logger.error(f"Unbekannte Quelle: {source}")
                return False
            
            # Preise in Datenbank speichern
            for price_data in prices:
                spot_price = SpotPrice(**price_data)
                db.session.add(spot_price)
            
            db.session.commit()
            logger.info(f"Spot-Preise importiert: {len(prices)} Datensätze für {date.date()}")
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Importieren der Spot-Preise: {e}")
            db.session.rollback()
            return False
    
    def analyze_project_economics(self, project_id: int, analysis_date: datetime = None) -> Dict:
        """Führt Wirtschaftlichkeits-Analyse für ein Projekt durch"""
        
        if analysis_date is None:
            analysis_date = datetime.now()
        
        project = Project.query.get(project_id)
        if not project:
            return {'error': 'Projekt nicht gefunden'}
        
        # Spot-Preise für die letzten 30 Tage abrufen
        start_date = analysis_date - timedelta(days=30)
        prices = SpotPrice.query.filter(
            SpotPrice.timestamp >= start_date,
            SpotPrice.timestamp <= analysis_date,
            SpotPrice.region == 'AT'  # Standard: Österreich
        ).all()
        
        if not prices:
            return {'error': 'Keine Spot-Preise verfügbar'}
        
        # Preisdaten konvertieren
        price_data = [{
            'timestamp': p.timestamp,
            'price_eur_mwh': p.price_eur_mwh
        } for p in prices]
        
        # BESS-Konfiguration
        bess_capacity = project.bess_size or 5000  # kWh
        bess_power = project.bess_power or 1000    # kW
        efficiency = 0.9  # 90%
        
        # Analysen durchführen
        price_categories = self.processor.categorize_prices(price_data)
        arbitrage = self.processor.calculate_arbitrage_potential(
            price_data, bess_capacity, bess_power, efficiency
        )
        peak_shaving = self.processor.calculate_peak_shaving_potential(
            price_data, bess_power
        )
        
        # Gesamte Einsparungen
        total_annual_savings = arbitrage['annual_revenue_eur'] + peak_shaving['annual_savings_eur']
        
        # ROI-Berechnung (geschätzte Investitionskosten)
        estimated_investment = bess_capacity * 800  # 800 €/kWh geschätzt
        roi_data = self.processor.calculate_roi(total_annual_savings, estimated_investment)
        
        # Ergebnisse in Datenbank speichern
        analysis = EconomicAnalysis(
            project_id=project_id,
            analysis_date=analysis_date,
            analysis_type='comprehensive',
            annual_arbitrage_potential=arbitrage['annual_revenue_eur'],
            optimal_cycles_per_year=arbitrage['optimal_cycles_per_year'],
            avg_price_spread=arbitrage['price_spread_eur_mwh'],
            annual_peak_shaving_savings=peak_shaving['annual_savings_eur'],
            peak_hours_per_day=peak_shaving['peak_hours_per_day'],
            avg_peak_price=peak_shaving['avg_peak_price_eur_mwh'],
            total_investment=estimated_investment,
            annual_savings=total_annual_savings,
            payback_period_years=roi_data['payback_years'],
            roi_percentage=roi_data['roi_percentage'],
            bess_capacity_kwh=bess_capacity,
            bess_power_kw=bess_power,
            efficiency=efficiency
        )
        
        db.session.add(analysis)
        db.session.commit()
        
        return {
            'project_name': project.name,
            'analysis_date': analysis_date.isoformat(),
            'price_categories': price_categories,
            'arbitrage_potential': arbitrage,
            'peak_shaving_potential': peak_shaving,
            'roi_analysis': roi_data,
            'total_annual_savings': total_annual_savings
        }
    
    def get_current_prices(self, region: str = 'AT') -> List[Dict]:
        """Gibt aktuelle Spot-Preise zurück"""
        today = datetime.now().date()
        start_time = datetime.combine(today, datetime.min.time())
        end_time = start_time + timedelta(days=1)
        
        prices = SpotPrice.query.filter(
            SpotPrice.timestamp >= start_time,
            SpotPrice.timestamp <= end_time,
            SpotPrice.region == region
        ).order_by(SpotPrice.timestamp).all()
        
        return [{
            'timestamp': p.timestamp.isoformat(),
            'price_eur_mwh': p.price_eur_mwh,
            'source': p.source,
            'price_type': p.price_type
        } for p in prices]
    
    def get_price_statistics(self, days: int = 30, region: str = 'AT') -> Dict:
        """Gibt Preis-Statistiken für einen Zeitraum zurück"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        prices = SpotPrice.query.filter(
            SpotPrice.timestamp >= start_date,
            SpotPrice.timestamp <= end_date,
            SpotPrice.region == region
        ).all()
        
        if not prices:
            return {'error': 'Keine Preisdaten verfügbar'}
        
        price_values = [p.price_eur_mwh for p in prices]
        
        return {
            'period_days': days,
            'total_hours': len(prices),
            'avg_price': round(np.mean(price_values), 2),
            'min_price': round(min(price_values), 2),
            'max_price': round(max(price_values), 2),
            'std_price': round(np.std(price_values), 2),
            'price_categories': self.processor.categorize_prices([{
                'price_eur_mwh': p.price_eur_mwh
            } for p in prices])
        }

# Beispiel-Verwendung
if __name__ == "__main__":
    from app import create_app
    
    # Flask-App erstellen und Kontext setzen
    app = create_app()
    
    with app.app_context():
        importer = SpotPriceImporter()
        
        # Tägliche Preise importieren
        today = datetime.now()
        success = importer.import_daily_prices(today, 'ENTSO-E', 'AT')
        
        if success:
            print("✅ Spot-Preise erfolgreich importiert")
            
            # Aktuelle Preise anzeigen
            current_prices = importer.get_current_prices('AT')
            print(f"📊 {len(current_prices)} aktuelle Preise verfügbar")
            
            # Statistiken anzeigen
            stats = importer.get_price_statistics(7, 'AT')
            if 'error' not in stats:
                print(f"📈 Durchschnittspreis (7 Tage): {stats['avg_price']} €/MWh")
            else:
                print(f"📈 Keine Preisdaten verfügbar: {stats['error']}")
        else:
            print("❌ Fehler beim Importieren der Spot-Preise") 