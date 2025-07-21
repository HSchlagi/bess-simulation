#!/usr/bin/env python3
"""
Demo: Spot-Preis Integration für BESS Simulation
Verwendet Mock-Daten für Demonstration der Wirtschaftlichkeits-Analysen
"""

import numpy as np
from datetime import datetime, timedelta
import json
import sys
import os

# Stelle sicher, dass numpy verfügbar ist
try:
    import numpy as np
except ImportError:
    print("Fehler: numpy ist nicht installiert")
    sys.exit(1)

class SpotPriceDemo:
    """Demo-Klasse für Spot-Preis Analysen"""
    
    def __init__(self):
        self.low_price_threshold = 50   # €/MWh
        self.high_price_threshold = 100  # €/MWh
    
    def generate_mock_prices(self, days: int = 30) -> list:
        """Generiert realistische Mock-Preisdaten"""
        prices = []
        base_date = datetime.now() - timedelta(days=days)
        
        # Realistische österreichische Spot-Preise (€/MWh)
        base_prices = [
            45, 42, 40, 38, 35, 32, 30, 28, 25, 22, 20, 18,  # Nacht (0-11h)
            20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75,  # Tag (12-23h)
        ]
        
        for day in range(days):
            current_date = base_date + timedelta(days=day)
            
            # Wochentag-Effekt
            weekday_factor = 1.1 if current_date.weekday() < 5 else 0.9  # Wochenende günstiger
            
            # Jahreszeit-Effekt
            month = current_date.month
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
                
                timestamp = current_date.replace(hour=hour, minute=0, second=0, microsecond=0)
                
                prices.append({
                    'timestamp': timestamp,
                    'price_eur_mwh': round(final_price, 2)
                })
        
        return prices
    
    def generate_mock_daily_prices(self, days: int = 30) -> list:
        """Generiert tägliche Durchschnittspreise"""
        prices = []
        base_date = datetime.now() - timedelta(days=days)
        
        for day in range(days):
            current_date = base_date + timedelta(days=day)
            
            # Wochentag-Effekt
            weekday_factor = 1.1 if current_date.weekday() < 5 else 0.9
            
            # Jahreszeit-Effekt
            month = current_date.month
            if month in [12, 1, 2]:  # Winter
                season_factor = 1.2
            elif month in [6, 7, 8]:  # Sommer
                season_factor = 0.9
            else:  # Übergangszeit
                season_factor = 1.0
            
            # Täglicher Durchschnittspreis (40-60 €/MWh)
            base_price = 50
            adjusted_price = base_price * weekday_factor * season_factor
            
            # Zufällige Variation (±15%)
            variation = np.random.normal(0, 0.08)
            final_price = adjusted_price * (1 + variation)
            
            timestamp = current_date.replace(hour=12, minute=0, second=0, microsecond=0)
            
            prices.append({
                'timestamp': timestamp,
                'price_eur_mwh': round(final_price, 2),
                'type': 'daily_average'
            })
        
        return prices
    
    def generate_mock_monthly_prices(self, months: int = 12) -> list:
        """Generiert monatliche Durchschnittspreise"""
        prices = []
        base_date = datetime.now() - timedelta(days=months*30)
        
        for month in range(months):
            current_date = base_date + timedelta(days=month*30)
            
            # Jahreszeit-Effekt
            month_num = current_date.month
            if month_num in [12, 1, 2]:  # Winter
                season_factor = 1.3
            elif month_num in [6, 7, 8]:  # Sommer
                season_factor = 0.8
            else:  # Übergangszeit
                season_factor = 1.0
            
            # Monatlicher Durchschnittspreis (35-65 €/MWh)
            base_price = 50
            adjusted_price = base_price * season_factor
            
            # Zufällige Variation (±20%)
            variation = np.random.normal(0, 0.1)
            final_price = adjusted_price * (1 + variation)
            
            timestamp = current_date.replace(day=15, hour=12, minute=0, second=0, microsecond=0)
            
            prices.append({
                'timestamp': timestamp,
                'price_eur_mwh': round(final_price, 2),
                'type': 'monthly_average'
            })
        
        return prices
    
    def generate_2024_historical_prices(self, region: str = 'AT') -> list:
        """Generiert historische 2024 Preisdaten für verschiedene Regionen"""
        prices = []
        start_date = datetime(2024, 1, 1)
        
        # Region-spezifische Basispreise (€/MWh)
        region_prices = {
            'AT': {'base': 50, 'volatility': 0.1},  # Österreich
            'DE': {'base': 55, 'volatility': 0.12},  # Deutschland
            'CH': {'base': 60, 'volatility': 0.08},  # Schweiz
            'EU': {'base': 52, 'volatility': 0.11}   # Europa Durchschnitt
        }
        
        region_config = region_prices.get(region, region_prices['AT'])
        base_price = region_config['base']
        volatility = region_config['volatility']
        
        # 2024-spezifische Ereignisse (Energiekrise, Ukraine-Konflikt, etc.)
        crisis_months = [1, 2, 3, 10, 11, 12]  # Winter-Monate mit höheren Preisen
        
        for day in range(365):  # 2024 war ein Schaltjahr
            current_date = start_date + timedelta(days=day)
            
            # Wochentag-Effekt
            weekday_factor = 1.1 if current_date.weekday() < 5 else 0.9
            
            # Jahreszeit-Effekt
            month = current_date.month
            if month in crisis_months:  # Winter-Krise
                season_factor = 1.4
            elif month in [6, 7, 8]:  # Sommer
                season_factor = 0.8
            else:  # Übergangszeit
                season_factor = 1.0
            
            # 2024-spezifische Trends
            # Höhere Preise in der ersten Jahreshälfte, dann Abnahme
            year_progress = day / 365
            if year_progress < 0.5:  # Erste Jahreshälfte
                trend_factor = 1.2
            else:  # Zweite Jahreshälfte
                trend_factor = 0.9
            
            adjusted_price = base_price * weekday_factor * season_factor * trend_factor
            
            # Zufällige Variation
            variation = np.random.normal(0, volatility)
            final_price = adjusted_price * (1 + variation)
            
            # Stündliche Preise für den Tag
            for hour in range(24):
                hour_factor = 1.0
                if 6 <= hour <= 22:  # Tag
                    hour_factor = 1.2
                elif 22 <= hour or hour <= 6:  # Nacht
                    hour_factor = 0.8
                
                hourly_price = final_price * hour_factor
                
                timestamp = current_date.replace(hour=hour, minute=0, second=0, microsecond=0)
                
                prices.append({
                    'timestamp': timestamp,
                    'price_eur_mwh': round(hourly_price, 2),
                    'region': region,
                    'year': 2024
                })
        
        return prices
    
    def categorize_prices(self, prices: list) -> dict:
        """Kategorisiert Preise in Niedrig-, Mittel- und Hochpreis"""
        price_values = [p['price_eur_mwh'] for p in prices]
        
        low_prices = [p for p in price_values if p < self.low_price_threshold]
        medium_prices = [p for p in price_values if self.low_price_threshold <= p <= self.high_price_threshold]
        high_prices = [p for p in price_values if p > self.high_price_threshold]
        
        return {
            'low_prices': {
                'count': len(low_prices),
                'avg_price': round(np.mean(low_prices), 2) if low_prices else 0,
                'hours': len(low_prices),
                'percentage': round(len(low_prices) / len(price_values) * 100, 1)
            },
            'medium_prices': {
                'count': len(medium_prices),
                'avg_price': round(np.mean(medium_prices), 2) if medium_prices else 0,
                'hours': len(medium_prices),
                'percentage': round(len(medium_prices) / len(price_values) * 100, 1)
            },
            'high_prices': {
                'count': len(high_prices),
                'avg_price': round(np.mean(high_prices), 2) if high_prices else 0,
                'hours': len(high_prices),
                'percentage': round(len(high_prices) / len(price_values) * 100, 1)
            },
            'overall': {
                'avg_price': round(np.mean(price_values), 2),
                'min_price': round(min(price_values), 2),
                'max_price': round(max(price_values), 2),
                'std_price': round(np.std(price_values), 2),
                'total_hours': len(price_values)
            }
        }
    
    def calculate_arbitrage_potential(self, prices: list, bess_capacity_kwh: float, 
                                    bess_power_kw: float, efficiency: float = 0.9) -> dict:
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
            'arbitrage_hours_per_day': n_arbitrage_hours,
            'bess_capacity_kwh': bess_capacity_kwh,
            'bess_power_kw': bess_power_kw,
            'efficiency': efficiency
        }
    
    def calculate_peak_shaving_potential(self, prices: list, bess_power_kw: float) -> dict:
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
                     annual_operation_cost: float = 0) -> dict:
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
    
    def run_complete_analysis(self, bess_capacity_kwh: float = 5000, 
                            bess_power_kw: float = 1000, days: int = 30) -> dict:
        """Führt eine vollständige Wirtschaftlichkeits-Analyse durch"""
        
        print("🚀 Starte Spot-Preis Wirtschaftlichkeits-Analyse...")
        print(f"📊 Analysiere {days} Tage Preisdaten")
        print(f"🔋 BESS-Konfiguration: {bess_capacity_kwh} kWh / {bess_power_kw} kW")
        print()
        
        # Mock-Preisdaten generieren
        prices = self.generate_mock_prices(days)
        print(f"✅ {len(prices)} Preisdatensätze generiert")
        
        # Preis-Kategorisierung
        categories = self.categorize_prices(prices)
        print("\n📈 Preis-Kategorisierung:")
        print(f"  • Niedrigpreis (< {self.low_price_threshold} €/MWh): {categories['low_prices']['count']}h ({categories['low_prices']['percentage']}%) - Ø {categories['low_prices']['avg_price']} €/MWh")
        print(f"  • Mittelpreis ({self.low_price_threshold}-{self.high_price_threshold} €/MWh): {categories['medium_prices']['count']}h ({categories['medium_prices']['percentage']}%) - Ø {categories['medium_prices']['avg_price']} €/MWh")
        print(f"  • Hochpreis (> {self.high_price_threshold} €/MWh): {categories['high_prices']['count']}h ({categories['high_prices']['percentage']}%) - Ø {categories['high_prices']['avg_price']} €/MWh")
        print(f"  • Gesamt: Ø {categories['overall']['avg_price']} €/MWh (Min: {categories['overall']['min_price']}, Max: {categories['overall']['max_price']})")
        
        # Arbitrage-Analyse
        arbitrage = self.calculate_arbitrage_potential(prices, bess_capacity_kwh, bess_power_kw)
        print(f"\n💰 Arbitrage-Potential:")
        print(f"  • Preis-Spread: {arbitrage['avg_high_price']} - {arbitrage['avg_low_price']} = {arbitrage['price_spread_eur_mwh']} €/MWh")
        print(f"  • Täglicher Umsatz: {arbitrage['daily_revenue_eur']} €")
        print(f"  • Jährlicher Umsatz: {arbitrage['annual_revenue_eur']:,} €")
        print(f"  • Optimale Zyklen/Jahr: {arbitrage['optimal_cycles_per_year']}")
        
        # Peak-Shaving-Analyse
        peak_shaving = self.calculate_peak_shaving_potential(prices, bess_power_kw)
        print(f"\n⚡ Peak-Shaving-Potential:")
        print(f"  • Durchschnittlicher Peak-Preis: {peak_shaving['avg_peak_price_eur_mwh']} €/MWh")
        print(f"  • Peak-Stunden/Tag: {peak_shaving['peak_hours_per_day']}")
        print(f"  • Tägliche Einsparungen: {peak_shaving['daily_savings_eur']} €")
        print(f"  • Jährliche Einsparungen: {peak_shaving['annual_savings_eur']:,} €")
        
        # Gesamte Wirtschaftlichkeit
        total_annual_savings = arbitrage['annual_revenue_eur'] + peak_shaving['annual_savings_eur']
        estimated_investment = bess_capacity_kwh * 800  # 800 €/kWh geschätzt
        roi_data = self.calculate_roi(total_annual_savings, estimated_investment)
        
        print(f"\n🎯 Gesamtwirtschaftlichkeit:")
        print(f"  • Gesamte jährliche Einsparungen: {total_annual_savings:,} €")
        print(f"  • Geschätzte Investition: {estimated_investment:,} €")
        print(f"  • ROI: {roi_data['roi_percentage']}%")
        print(f"  • Amortisationszeit: {roi_data['payback_years']} Jahre")
        
        # Empfehlungen
        print(f"\n💡 Empfehlungen:")
        if roi_data['roi_percentage'] > 10:
            print(f"  ✅ Sehr gute Wirtschaftlichkeit (ROI > 10%)")
        elif roi_data['roi_percentage'] > 5:
            print(f"  ⚠️  Mittlere Wirtschaftlichkeit (ROI 5-10%)")
        else:
            print(f"  ❌ Niedrige Wirtschaftlichkeit (ROI < 5%)")
        
        if arbitrage['price_spread_eur_mwh'] > 50:
            print(f"  ✅ Hohes Arbitrage-Potential (Spread > 50 €/MWh)")
        else:
            print(f"  ⚠️  Mittleres Arbitrage-Potential (Spread < 50 €/MWh)")
        
        if peak_shaving['avg_peak_price_eur_mwh'] > 100:
            print(f"  ✅ Hohes Peak-Shaving-Potential (Peak-Preis > 100 €/MWh)")
        else:
            print(f"  ⚠️  Mittleres Peak-Shaving-Potential (Peak-Preis < 100 €/MWh)")
        
        return {
            'price_categories': categories,
            'arbitrage_potential': arbitrage,
            'peak_shaving_potential': peak_shaving,
            'roi_data': roi_data,
            'total_annual_savings': total_annual_savings,
            'recommendation': 'good' if roi_data['roi_percentage'] > 10 else 'moderate'
        }

    def analyze_monthly_performance(self, prices: list, bess_capacity_kwh: float, bess_power_kw: float) -> dict:
        """Analysiert monatliche Performance für 2024-Daten"""
        monthly_data = {}
        
        for month in range(1, 13):
            month_prices = [p for p in prices if p['timestamp'].month == month]
            
            if not month_prices:
                continue
            
            # Monatliche Statistiken
            month_price_values = [p['price_eur_mwh'] for p in month_prices]
            avg_price = np.mean(month_price_values)
            min_price = min(month_price_values)
            max_price = max(month_price_values)
            
            # Arbitrage-Potential für diesen Monat
            sorted_prices = sorted(month_prices, key=lambda x: x['price_eur_mwh'])
            n_hours = len(sorted_prices)
            n_arbitrage_hours = n_hours // 4
            
            low_prices = sorted_prices[:n_arbitrage_hours]
            high_prices = sorted_prices[-n_arbitrage_hours:]
            
            avg_low_price = np.mean([p['price_eur_mwh'] for p in low_prices]) if low_prices else 0
            avg_high_price = np.mean([p['price_eur_mwh'] for p in high_prices]) if high_prices else 0
            price_spread = avg_high_price - avg_low_price
            
            # Monatliche Erträge
            daily_energy = bess_capacity_kwh * 0.9  # 90% Effizienz
            daily_revenue = daily_energy * price_spread / 1000  # MWh zu kWh
            monthly_revenue = daily_revenue * 30  # Geschätzt 30 Tage
            
            # Peak-Shaving
            peak_prices = sorted_prices[:n_hours//5]  # Top 20%
            avg_peak_price = np.mean([p['price_eur_mwh'] for p in peak_prices]) if peak_prices else 0
            daily_peak_savings = bess_power_kw * avg_peak_price / 1000
            monthly_peak_savings = daily_peak_savings * 30
            
            monthly_data[month] = {
                'month_name': datetime(2024, month, 1).strftime('%B'),
                'avg_price': round(avg_price, 2),
                'min_price': round(min_price, 2),
                'max_price': round(max_price, 2),
                'price_spread': round(price_spread, 2),
                'arbitrage_revenue': round(monthly_revenue, 2),
                'peak_shaving_savings': round(monthly_peak_savings, 2),
                'total_monthly_savings': round(monthly_revenue + monthly_peak_savings, 2),
                'hours_count': n_hours,
                'arbitrage_hours': n_arbitrage_hours
            }
        
        return monthly_data

def main():
    """Hauptfunktion für die Demo"""
    demo = SpotPriceDemo()
    
    # Verschiedene BESS-Konfigurationen testen
    configurations = [
        {'name': 'Kleine BESS', 'capacity': 2000, 'power': 500},
        {'name': 'Mittlere BESS', 'capacity': 5000, 'power': 1000},
        {'name': 'Große BESS', 'capacity': 10000, 'power': 2000}
    ]
    
    print("🔋 BESS Spot-Preis Wirtschaftlichkeits-Analyse")
    print("=" * 60)
    
    results = {}
    
    for config in configurations:
        print(f"\n{'='*20} {config['name']} {'='*20}")
        result = demo.run_complete_analysis(
            bess_capacity_kwh=config['capacity'],
            bess_power_kw=config['power'],
            days=30
        )
        results[config['name']] = result
    
    # Vergleich
    print(f"\n{'='*20} Vergleich {'='*20}")
    print(f"{'Konfiguration':<15} {'Jährl. Einsparung':<20} {'ROI %':<10} {'Amortisation':<15}")
    print("-" * 60)
    
    for name, result in results.items():
        roi = result['roi_data']['roi_percentage']
        savings = result['total_annual_savings']
        payback = result['roi_data']['payback_years']
        print(f"{name:<15} {savings:>15,.0f} € {'':<4} {roi:>6.1f}% {'':<3} {payback:>6.1f} Jahre")

if __name__ == "__main__":
    main() 