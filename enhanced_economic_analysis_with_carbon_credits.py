#!/usr/bin/env python3
"""
Enhanced Economic Analysis mit CO₂-Zertifikaten Integration
Erweitert die bestehende Wirtschaftlichkeitsanalyse um Carbon Credits und Green Finance
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json

# Import der bestehenden Systeme
from carbon_credit_trading_system import CarbonCreditTradingSystem
from enhanced_esg_reporting_system import EnhancedESGReportingSystem
from green_finance_integration import GreenFinanceIntegration
from co2_tracking_system import CO2TrackingSystem

class EnhancedEconomicAnalysisWithCarbonCredits:
    """Erweiterte Wirtschaftlichkeitsanalyse mit CO₂-Zertifikaten"""
    
    def __init__(self, db_path: str = "instance/bess.db"):
        self.db_path = db_path
        self.carbon_trading = CarbonCreditTradingSystem(db_path)
        self.esg_system = EnhancedESGReportingSystem(db_path)
        self.green_finance = GreenFinanceIntegration(db_path)
        self.co2_system = CO2TrackingSystem(db_path)
        
        # Carbon Credit Preise (EUR/tonne CO₂)
        self.carbon_credit_prices = {
            'VER': 8.50,
            'CER': 2.30,
            'VCS': 12.00,
            'Gold Standard': 15.50,
            'CCER': 5.20
        }
        
        # Green Finance Renditen
        self.green_finance_returns = {
            'green_bonds': 0.028,  # 2.8% p.a.
            'sustainability_bonds': 0.032,  # 3.2% p.a.
            'green_loans': 0.025  # 2.5% p.a.
        }
    
    def calculate_enhanced_economic_analysis(self, project_id: int, 
                                           analysis_period_years: int = 20) -> Dict:
        """Berechnet erweiterte Wirtschaftlichkeitsanalyse mit CO₂-Zertifikaten"""
        
        try:
            # 1. Projekt-Daten abrufen
            project_data = self._get_project_data(project_id)
            if not project_data:
                return {'error': 'Projekt nicht gefunden'}
            
            # 2. Basis-Wirtschaftlichkeitsanalyse
            base_analysis = self._calculate_base_economic_analysis(project_data, analysis_period_years)
            
            # 3. CO₂-Zertifikate Erlöse berechnen
            carbon_credit_revenues = self._calculate_carbon_credit_revenues(project_id, analysis_period_years)
            
            # 4. Green Finance Portfolio berechnen
            green_finance_revenues = self._calculate_green_finance_revenues(project_id, analysis_period_years)
            
            # 5. ESG-Bonus berechnen
            esg_bonus = self._calculate_esg_bonus(project_id, analysis_period_years)
            
            # 6. Erweiterte ROI-Berechnung
            enhanced_roi = self._calculate_enhanced_roi(
                base_analysis, carbon_credit_revenues, green_finance_revenues, esg_bonus
            )
            
            # 7. Risiko-Adjustierte Bewertung
            risk_adjusted_analysis = self._calculate_risk_adjusted_analysis(enhanced_roi, project_id)
            
            # 8. Szenario-Analyse
            scenario_analysis = self._calculate_scenario_analysis(
                base_analysis, carbon_credit_revenues, green_finance_revenues
            )
            
            return {
                'success': True,
                'project_id': project_id,
                'analysis_period_years': analysis_period_years,
                'analysis_date': datetime.now().isoformat(),
                'base_analysis': base_analysis,
                'carbon_credit_revenues': carbon_credit_revenues,
                'green_finance_revenues': green_finance_revenues,
                'esg_bonus': esg_bonus,
                'enhanced_roi': enhanced_roi,
                'risk_adjusted_analysis': risk_adjusted_analysis,
                'scenario_analysis': scenario_analysis,
                'recommendations': self._generate_recommendations(enhanced_roi, project_id)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _get_project_data(self, project_id: int) -> Optional[Dict]:
        """Ruft Projekt-Daten ab"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, name, location, bess_size, bess_power, pv_power, 
               wind_power, hydro_power, hp_power
        FROM project WHERE id = ?
        ''', (project_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'name': result[1],
                'location': result[2],
                'bess_size': result[3] or 0,
                'bess_power': result[4] or 0,
                'pv_power': result[5] or 0,
                'wind_power': result[6] or 0,
                'hydro_power': result[7] or 0,
                'hp_power': result[8] or 0
            }
        return None
    
    def _calculate_base_economic_analysis(self, project_data: Dict, 
                                        analysis_period_years: int) -> Dict:
        """Berechnet Basis-Wirtschaftlichkeitsanalyse"""
        
        # Investitionskosten
        bess_investment = project_data['bess_size'] * 1000  # 1000 EUR/kWh
        pv_investment = project_data['pv_power'] * 1200     # 1200 EUR/kW
        wind_investment = project_data['wind_power'] * 1500 # 1500 EUR/kW
        hydro_investment = project_data['hydro_power'] * 2000 # 2000 EUR/kW
        
        total_investment = bess_investment + pv_investment + wind_investment + hydro_investment
        
        # Jährliche Betriebskosten (2% der Investition)
        annual_operating_costs = total_investment * 0.02
        
        # Jährliche Energiemengen
        annual_energy_generation = (
            project_data['pv_power'] * 1000 +      # PV: 1000 kWh/kW/a
            project_data['wind_power'] * 2000 +    # Wind: 2000 kWh/kW/a
            project_data['hydro_power'] * 3000     # Hydro: 3000 kWh/kW/a
        )
        
        # BESS-Nutzung (70% der generierten Energie)
        bess_energy_throughput = annual_energy_generation * 0.7
        
        # Erlöse aus Energieverkauf (0.05 EUR/kWh)
        energy_revenue = bess_energy_throughput * 0.05
        
        # Arbitrage-Erlöse (geschätzt 0.03 EUR/kWh)
        arbitrage_revenue = bess_energy_throughput * 0.03
        
        # Regelenergie-Erlöse (geschätzt 0.02 EUR/kWh)
        regulation_revenue = bess_energy_throughput * 0.02
        
        total_annual_revenue = energy_revenue + arbitrage_revenue + regulation_revenue
        annual_net_benefit = total_annual_revenue - annual_operating_costs
        
        # Amortisationszeit
        payback_period = total_investment / annual_net_benefit if annual_net_benefit > 0 else float('inf')
        
        # ROI über Analyseperiode
        total_benefits = annual_net_benefit * analysis_period_years
        roi_percent = ((total_benefits - total_investment) / total_investment * 100) if total_investment > 0 else 0
        
        return {
            'total_investment_eur': total_investment,
            'annual_operating_costs_eur': annual_operating_costs,
            'annual_energy_generation_kwh': annual_energy_generation,
            'annual_revenue_eur': total_annual_revenue,
            'annual_net_benefit_eur': annual_net_benefit,
            'payback_period_years': payback_period,
            'roi_percent': roi_percent,
            'total_benefits_eur': total_benefits,
            'investment_breakdown': {
                'bess_investment_eur': bess_investment,
                'pv_investment_eur': pv_investment,
                'wind_investment_eur': wind_investment,
                'hydro_investment_eur': hydro_investment
            }
        }
    
    def _calculate_carbon_credit_revenues(self, project_id: int, 
                                        analysis_period_years: int) -> Dict:
        """Berechnet CO₂-Zertifikate Erlöse"""
        
        try:
            # CO₂-Einsparungen für das letzte Jahr berechnen
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=365)
            
            conn = sqlite3.connect(self.db_path)
            query = '''
            SELECT SUM(co2_saved_kg) as total_co2_saved
            FROM co2_balance 
            WHERE project_id = ? AND date BETWEEN ? AND ?
            '''
            
            df = pd.read_sql_query(query, conn, params=(
                project_id, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
            ))
            conn.close()
            
            annual_co2_saved_kg = df.iloc[0]['total_co2_saved'] if not df.empty else 0
            
            if annual_co2_saved_kg <= 0:
                return {
                    'annual_co2_saved_tonnes': 0,
                    'annual_carbon_credit_revenue_eur': 0,
                    'total_carbon_credit_revenue_eur': 0,
                    'carbon_credit_type': 'VER',
                    'carbon_credit_price_eur_per_tonne': self.carbon_credit_prices['VER']
                }
            
            # CO₂ in Tonnen umrechnen
            annual_co2_saved_tonnes = annual_co2_saved_kg / 1000
            
            # Carbon Credit Erlöse (VER-Standard)
            carbon_credit_price = self.carbon_credit_prices['VER']
            annual_carbon_credit_revenue = annual_co2_saved_tonnes * carbon_credit_price
            
            # Gesamte Erlöse über Analyseperiode
            total_carbon_credit_revenue = annual_carbon_credit_revenue * analysis_period_years
            
            return {
                'annual_co2_saved_tonnes': annual_co2_saved_tonnes,
                'annual_carbon_credit_revenue_eur': annual_carbon_credit_revenue,
                'total_carbon_credit_revenue_eur': total_carbon_credit_revenue,
                'carbon_credit_type': 'VER',
                'carbon_credit_price_eur_per_tonne': carbon_credit_price
            }
            
        except Exception as e:
            print(f"Fehler bei Carbon Credit Berechnung: {e}")
            return {
                'annual_co2_saved_tonnes': 0,
                'annual_carbon_credit_revenue_eur': 0,
                'total_carbon_credit_revenue_eur': 0,
                'carbon_credit_type': 'VER',
                'carbon_credit_price_eur_per_tonne': self.carbon_credit_prices['VER']
            }
    
    def _calculate_green_finance_revenues(self, project_id: int, 
                                        analysis_period_years: int) -> Dict:
        """Berechnet Green Finance Portfolio Erlöse"""
        
        try:
            # Portfolio Performance abrufen
            portfolio_performance = self.green_finance.calculate_portfolio_performance(project_id)
            
            # Verfügbare Green Bonds
            available_bonds = self.green_finance.get_available_green_bonds()
            
            # Empfehlungen für Green Finance
            recommendations = self.green_finance.get_green_finance_recommendations(
                project_id, 100000  # 100k EUR verfügbares Kapital
            )
            
            # Potentielle Green Finance Investitionen
            potential_investments = []
            total_potential_investment = 0
            total_potential_revenue = 0
            
            for bond in available_bonds[:3]:  # Top 3 Bonds
                investment_amount = min(50000, 100000 - total_potential_investment)
                if investment_amount > 0:
                    annual_coupon = investment_amount * (bond['interest_rate_percent'] / 100)
                    total_revenue = annual_coupon * analysis_period_years
                    
                    potential_investments.append({
                        'bond_name': bond['name'],
                        'investment_amount_eur': investment_amount,
                        'annual_coupon_eur': annual_coupon,
                        'total_revenue_eur': total_revenue,
                        'yield_percent': bond['interest_rate_percent']
                    })
                    
                    total_potential_investment += investment_amount
                    total_potential_revenue += total_revenue
            
            return {
                'current_portfolio_value_eur': portfolio_performance.get('total_portfolio_value_eur', 0),
                'current_annual_returns_eur': portfolio_performance.get('total_returns_eur', 0),
                'current_returns_percent': portfolio_performance.get('total_returns_percent', 0),
                'potential_investments': potential_investments,
                'total_potential_investment_eur': total_potential_investment,
                'total_potential_revenue_eur': total_potential_revenue,
                'recommendations': recommendations
            }
            
        except Exception as e:
            print(f"Fehler bei Green Finance Berechnung: {e}")
            return {
                'current_portfolio_value_eur': 0,
                'current_annual_returns_eur': 0,
                'current_returns_percent': 0,
                'potential_investments': [],
                'total_potential_investment_eur': 0,
                'total_potential_revenue_eur': 0,
                'recommendations': []
            }
    
    def _calculate_esg_bonus(self, project_id: int, analysis_period_years: int) -> Dict:
        """Berechnet ESG-Bonus (Förderungen, bessere Finanzierungskonditionen)"""
        
        try:
            # ESG-Report generieren
            esg_report = self.esg_system.generate_comprehensive_esg_report(project_id, 'yearly')
            
            esg_score = esg_report.overall_esg_score
            
            # ESG-basierte Förderungen
            if esg_score >= 90:
                # AAA-Rating: 15% Förderung
                esg_funding_percent = 0.15
            elif esg_score >= 80:
                # AA-Rating: 10% Förderung
                esg_funding_percent = 0.10
            elif esg_score >= 70:
                # A-Rating: 5% Förderung
                esg_funding_percent = 0.05
            else:
                # Unter A-Rating: Keine Förderung
                esg_funding_percent = 0.0
            
            # Bessere Finanzierungskonditionen
            if esg_score >= 85:
                interest_rate_reduction = 0.005  # 0.5% Zinssenkung
            elif esg_score >= 75:
                interest_rate_reduction = 0.003  # 0.3% Zinssenkung
            elif esg_score >= 65:
                interest_rate_reduction = 0.001  # 0.1% Zinssenkung
            else:
                interest_rate_reduction = 0.0
            
            return {
                'esg_score': esg_score,
                'sustainability_rating': esg_report.sustainability_rating,
                'esg_funding_percent': esg_funding_percent,
                'interest_rate_reduction': interest_rate_reduction,
                'annual_esg_bonus_eur': 0,  # Wird in der Hauptberechnung verwendet
                'total_esg_bonus_eur': 0    # Wird in der Hauptberechnung verwendet
            }
            
        except Exception as e:
            print(f"Fehler bei ESG-Bonus Berechnung: {e}")
            return {
                'esg_score': 0,
                'sustainability_rating': 'B-',
                'esg_funding_percent': 0.0,
                'interest_rate_reduction': 0.0,
                'annual_esg_bonus_eur': 0,
                'total_esg_bonus_eur': 0
            }
    
    def _calculate_enhanced_roi(self, base_analysis: Dict, carbon_credit_revenues: Dict,
                              green_finance_revenues: Dict, esg_bonus: Dict) -> Dict:
        """Berechnet erweiterten ROI mit allen neuen Erlösquellen"""
        
        # Basis-Erlöse
        base_annual_benefit = base_analysis['annual_net_benefit_eur']
        base_total_benefit = base_analysis['total_benefits_eur']
        
        # Carbon Credit Erlöse
        carbon_annual_revenue = carbon_credit_revenues['annual_carbon_credit_revenue_eur']
        carbon_total_revenue = carbon_credit_revenues['total_carbon_credit_revenue_eur']
        
        # Green Finance Erlöse
        green_annual_revenue = green_finance_revenues['current_annual_returns_eur']
        green_total_revenue = green_finance_revenues['total_potential_revenue_eur']
        
        # ESG-Bonus (vereinfacht als jährlicher Bonus)
        esg_annual_bonus = esg_bonus['esg_score'] * 100  # 1 Punkt = 100 EUR Bonus
        esg_total_bonus = esg_annual_bonus * 20  # 20 Jahre
        
        # Gesamte erweiterte Erlöse
        enhanced_annual_benefit = base_annual_benefit + carbon_annual_revenue + green_annual_revenue + esg_annual_bonus
        enhanced_total_benefit = base_total_benefit + carbon_total_revenue + green_total_revenue + esg_total_bonus
        
        # Investitionskosten mit ESG-Förderung
        base_investment = base_analysis['total_investment_eur']
        esg_funding = base_investment * esg_bonus['esg_funding_percent']
        adjusted_investment = base_investment - esg_funding
        
        # Erweiterte ROI-Berechnung
        enhanced_roi_percent = ((enhanced_total_benefit - adjusted_investment) / adjusted_investment * 100) if adjusted_investment > 0 else 0
        enhanced_payback_period = adjusted_investment / enhanced_annual_benefit if enhanced_annual_benefit > 0 else float('inf')
        
        # Erlösaufschlüsselung
        revenue_breakdown = {
            'base_revenue_percent': (base_annual_benefit / enhanced_annual_benefit * 100) if enhanced_annual_benefit > 0 else 0,
            'carbon_credit_percent': (carbon_annual_revenue / enhanced_annual_benefit * 100) if enhanced_annual_benefit > 0 else 0,
            'green_finance_percent': (green_annual_revenue / enhanced_annual_benefit * 100) if enhanced_annual_benefit > 0 else 0,
            'esg_bonus_percent': (esg_annual_bonus / enhanced_annual_benefit * 100) if enhanced_annual_benefit > 0 else 0
        }
        
        return {
            'enhanced_annual_benefit_eur': enhanced_annual_benefit,
            'enhanced_total_benefit_eur': enhanced_total_benefit,
            'adjusted_investment_eur': adjusted_investment,
            'esg_funding_eur': esg_funding,
            'enhanced_roi_percent': enhanced_roi_percent,
            'enhanced_payback_period_years': enhanced_payback_period,
            'revenue_breakdown': revenue_breakdown,
            'additional_revenues': {
                'carbon_credit_annual_eur': carbon_annual_revenue,
                'carbon_credit_total_eur': carbon_total_revenue,
                'green_finance_annual_eur': green_annual_revenue,
                'green_finance_total_eur': green_total_revenue,
                'esg_bonus_annual_eur': esg_annual_bonus,
                'esg_bonus_total_eur': esg_total_bonus
            }
        }
    
    def _calculate_risk_adjusted_analysis(self, enhanced_roi: Dict, project_id: int) -> Dict:
        """Berechnet risiko-adjustierte Bewertung"""
        
        # Risikofaktoren
        risk_factors = {
            'carbon_credit_price_volatility': 0.15,  # 15% Volatilität
            'green_finance_market_risk': 0.10,       # 10% Marktrisiko
            'regulatory_risk': 0.05,                 # 5% Regulierungsrisiko
            'technology_risk': 0.08                  # 8% Technologierisiko
        }
        
        # Gesamtrisiko
        total_risk = sum(risk_factors.values())
        
        # Risiko-adjustierte Rendite
        risk_free_rate = 0.02  # 2% risikofreie Rendite
        risk_adjusted_return = enhanced_roi['enhanced_roi_percent'] - (total_risk * 100)
        
        # Value at Risk (VaR) - 95% Konfidenzintervall
        var_95 = enhanced_roi['enhanced_total_benefit_eur'] * 0.1  # 10% VaR
        
        return {
            'total_risk_percent': total_risk * 100,
            'risk_factors': risk_factors,
            'risk_adjusted_return_percent': risk_adjusted_return,
            'value_at_risk_95_eur': var_95,
            'risk_level': 'hoch' if total_risk > 0.3 else 'mittel' if total_risk > 0.15 else 'niedrig'
        }
    
    def _calculate_scenario_analysis(self, base_analysis: Dict, carbon_credit_revenues: Dict,
                                   green_finance_revenues: Dict) -> Dict:
        """Berechnet Szenario-Analyse (Optimistisch, Realistisch, Pessimistisch)"""
        
        scenarios = {}
        
        # Carbon Credit Preise
        carbon_prices = {
            'optimistic': self.carbon_credit_prices['VER'] * 1.5,  # +50%
            'realistic': self.carbon_credit_prices['VER'],         # Basis
            'pessimistic': self.carbon_credit_prices['VER'] * 0.5  # -50%
        }
        
        for scenario_name, carbon_price in carbon_prices.items():
            # Carbon Credit Erlöse anpassen
            scenario_carbon_revenue = carbon_credit_revenues['annual_co2_saved_tonnes'] * carbon_price
            
            # Gesamte Erlöse
            total_annual_revenue = (
                base_analysis['annual_net_benefit_eur'] + 
                scenario_carbon_revenue + 
                green_finance_revenues['current_annual_returns_eur']
            )
            
            # ROI
            scenario_roi = ((total_annual_revenue * 20 - base_analysis['total_investment_eur']) / 
                          base_analysis['total_investment_eur'] * 100) if base_analysis['total_investment_eur'] > 0 else 0
            
            scenarios[scenario_name] = {
                'carbon_credit_price_eur_per_tonne': carbon_price,
                'annual_revenue_eur': total_annual_revenue,
                'roi_percent': scenario_roi,
                'payback_period_years': base_analysis['total_investment_eur'] / total_annual_revenue if total_annual_revenue > 0 else float('inf')
            }
        
        return scenarios
    
    def _generate_recommendations(self, enhanced_roi: Dict, project_id: int) -> List[Dict]:
        """Generiert Empfehlungen basierend auf der Analyse"""
        
        recommendations = []
        
        # ROI-basierte Empfehlungen
        if enhanced_roi['enhanced_roi_percent'] < 10:
            recommendations.append({
                'type': 'investment',
                'priority': 'high',
                'title': 'Investition überdenken',
                'description': 'ROI unter 10% - prüfen Sie alternative Investitionsmöglichkeiten',
                'action': 'Analyse der Investitionskosten und Erlöspotentiale'
            })
        elif enhanced_roi['enhanced_roi_percent'] > 20:
            recommendations.append({
                'type': 'expansion',
                'priority': 'medium',
                'title': 'Projekt erweitern',
                'description': 'Hohe ROI - Erwägen Sie eine Erweiterung des Projekts',
                'action': 'Kapazitätserhöhung oder zusätzliche Standorte prüfen'
            })
        
        # Carbon Credit Empfehlungen
        if enhanced_roi['additional_revenues']['carbon_credit_annual_eur'] > 0:
            recommendations.append({
                'type': 'carbon_credits',
                'priority': 'medium',
                'title': 'Carbon Credits optimieren',
                'description': f'Jährliche Carbon Credit Erlöse: {enhanced_roi["additional_revenues"]["carbon_credit_annual_eur"]:,.0f} EUR',
                'action': 'Carbon Credit Trading Strategien verfeinern'
            })
        
        # Green Finance Empfehlungen
        if enhanced_roi['additional_revenues']['green_finance_annual_eur'] > 0:
            recommendations.append({
                'type': 'green_finance',
                'priority': 'low',
                'title': 'Green Finance ausbauen',
                'description': f'Green Finance Portfolio zeigt positive Renditen',
                'action': 'Portfolio diversifizieren und erweitern'
            })
        
        # ESG Empfehlungen
        if enhanced_roi['additional_revenues']['esg_bonus_annual_eur'] > 0:
            recommendations.append({
                'type': 'esg',
                'priority': 'medium',
                'title': 'ESG-Performance beibehalten',
                'description': f'ESG-Bonus: {enhanced_roi["additional_revenues"]["esg_bonus_annual_eur"]:,.0f} EUR/Jahr',
                'action': 'ESG-Metriken kontinuierlich überwachen und verbessern'
            })
        
        return recommendations
    
    def save_enhanced_analysis(self, analysis_result: Dict) -> bool:
        """Speichert erweiterte Analyse in der Datenbank"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Tabelle erstellen falls nicht vorhanden
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS enhanced_economic_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                analysis_period_years INTEGER NOT NULL,
                base_investment_eur REAL NOT NULL,
                enhanced_investment_eur REAL NOT NULL,
                base_annual_benefit_eur REAL NOT NULL,
                enhanced_annual_benefit_eur REAL NOT NULL,
                base_roi_percent REAL NOT NULL,
                enhanced_roi_percent REAL NOT NULL,
                carbon_credit_revenue_eur REAL NOT NULL,
                green_finance_revenue_eur REAL NOT NULL,
                esg_bonus_eur REAL NOT NULL,
                analysis_data TEXT, -- JSON
                FOREIGN KEY (project_id) REFERENCES project (id)
            )
            ''')
            
            # Analyse speichern
            cursor.execute('''
            INSERT INTO enhanced_economic_analysis 
            (project_id, analysis_period_years, base_investment_eur, enhanced_investment_eur,
             base_annual_benefit_eur, enhanced_annual_benefit_eur, base_roi_percent,
             enhanced_roi_percent, carbon_credit_revenue_eur, green_finance_revenue_eur,
             esg_bonus_eur, analysis_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                analysis_result['project_id'],
                analysis_result['analysis_period_years'],
                analysis_result['base_analysis']['total_investment_eur'],
                analysis_result['enhanced_roi']['adjusted_investment_eur'],
                analysis_result['base_analysis']['annual_net_benefit_eur'],
                analysis_result['enhanced_roi']['enhanced_annual_benefit_eur'],
                analysis_result['base_analysis']['roi_percent'],
                analysis_result['enhanced_roi']['enhanced_roi_percent'],
                analysis_result['carbon_credit_revenues']['annual_carbon_credit_revenue_eur'],
                analysis_result['green_finance_revenues']['current_annual_returns_eur'],
                analysis_result['enhanced_roi']['additional_revenues']['esg_bonus_annual_eur'],
                json.dumps(analysis_result)
            ))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Fehler beim Speichern der Analyse: {e}")
            return False

def main():
    """Hauptfunktion für Enhanced Economic Analysis mit Carbon Credits"""
    print("💰 Enhanced Economic Analysis mit CO₂-Zertifikaten")
    print("=" * 60)
    
    # System initialisieren
    analysis_system = EnhancedEconomicAnalysisWithCarbonCredits()
    
    print("✅ Enhanced Economic Analysis System erfolgreich initialisiert")
    print("📊 Features:")
    print("   - CO₂-Zertifikate Integration")
    print("   - Green Finance Portfolio")
    print("   - ESG-Bonus Berechnung")
    print("   - Risiko-adjustierte Bewertung")
    print("   - Szenario-Analyse")
    print("   - Intelligente Empfehlungen")
    print("💰 Carbon Credit Preise:")
    for credit_type, price in analysis_system.carbon_credit_prices.items():
        print(f"   - {credit_type}: {price} EUR/tCO₂")

if __name__ == '__main__':
    main()
