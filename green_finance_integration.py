#!/usr/bin/env python3
"""
Green Finance Integration für BESS-Simulation
Implementiert Green Bonds, Sustainability Bonds und Green Investment Portfolios
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import requests
import asyncio
import aiohttp
from enum import Enum

class GreenFinanceType(Enum):
    """Green Finance Produkttypen"""
    GREEN_BOND = "green_bond"
    SUSTAINABILITY_BOND = "sustainability_bond"
    GREEN_LOAN = "green_loan"
    SUSTAINABILITY_LOAN = "sustainability_loan"
    CARBON_CREDIT = "carbon_credit"
    RENEWABLE_ENERGY_CERTIFICATE = "renewable_energy_certificate"
    GREEN_ETF = "green_etf"
    SUSTAINABILITY_ETF = "sustainability_etf"

@dataclass
class GreenFinanceProduct:
    """Green Finance Produkt Datenstruktur"""
    id: Optional[int]
    project_id: int
    product_type: GreenFinanceType
    name: str
    issuer: str
    volume_eur: float
    currency: str
    interest_rate_percent: float
    maturity_date: datetime
    coupon_frequency: str  # 'annual', 'semi_annual', 'quarterly'
    credit_rating: str
    sustainability_rating: str
    green_use_proceeds: str
    purchase_price_eur: float
    current_price_eur: float
    purchase_date: datetime
    status: str  # 'active', 'matured', 'sold', 'defaulted'
    esg_score: float
    carbon_impact_tonnes_co2: float

class GreenFinanceIntegration:
    """Green Finance Integration System"""
    
    def __init__(self, db_path: str = "instance/bess.db"):
        self.db_path = db_path
        
        # Green Finance Marktdaten
        self.market_data = {
            'green_bonds': {
                'average_yield': 2.8,
                'average_maturity': 7.5,
                'average_rating': 'AA-',
                'market_size_eur': 500_000_000_000  # 500 Milliarden EUR
            },
            'sustainability_bonds': {
                'average_yield': 3.2,
                'average_maturity': 8.2,
                'average_rating': 'A+',
                'market_size_eur': 300_000_000_000  # 300 Milliarden EUR
            },
            'green_loans': {
                'average_rate': 2.5,
                'average_maturity': 5.0,
                'average_rating': 'A',
                'market_size_eur': 200_000_000_000  # 200 Milliarden EUR
            }
        }
        
        # Green Finance APIs
        self.apis = {
            'green_bond_api': 'https://api.greenbond.com/v1/bonds',
            'sustainability_api': 'https://api.sustainability.org/v1/products',
            'carbon_market_api': 'https://api.carbonmarket.com/v1/prices'
        }
    
    def create_green_finance_tables(self):
        """Erstellt Green Finance Tabellen"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Green Finance Products Tabelle
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS green_finance_products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            product_type VARCHAR(50) NOT NULL,
            name VARCHAR(200) NOT NULL,
            issuer VARCHAR(200) NOT NULL,
            volume_eur REAL NOT NULL,
            currency VARCHAR(10) DEFAULT 'EUR',
            interest_rate_percent REAL NOT NULL,
            maturity_date DATE NOT NULL,
            coupon_frequency VARCHAR(20) DEFAULT 'annual',
            credit_rating VARCHAR(10) NOT NULL,
            sustainability_rating VARCHAR(10) NOT NULL,
            green_use_proceeds TEXT NOT NULL,
            purchase_price_eur REAL NOT NULL,
            current_price_eur REAL NOT NULL,
            purchase_date DATE NOT NULL,
            status VARCHAR(20) DEFAULT 'active',
            esg_score REAL NOT NULL,
            carbon_impact_tonnes_co2 REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES project (id)
        )
        ''')
        
        # Green Finance Transactions Tabelle
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS green_finance_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            project_id INTEGER NOT NULL,
            transaction_type VARCHAR(20) NOT NULL, -- 'buy', 'sell', 'coupon_payment', 'maturity'
            volume_eur REAL NOT NULL,
            price_eur REAL NOT NULL,
            transaction_date DATE NOT NULL,
            counterparty VARCHAR(200),
            fees_eur REAL DEFAULT 0,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES green_finance_products (id),
            FOREIGN KEY (project_id) REFERENCES project (id)
        )
        ''')
        
        # Green Finance Performance Tabelle
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS green_finance_performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            reporting_date DATE NOT NULL,
            total_portfolio_value_eur REAL NOT NULL,
            total_invested_eur REAL NOT NULL,
            total_returns_eur REAL NOT NULL,
            total_returns_percent REAL NOT NULL,
            annualized_return_percent REAL NOT NULL,
            esg_weighted_return_percent REAL NOT NULL,
            carbon_impact_total_tonnes_co2 REAL NOT NULL,
            green_alignment_score REAL NOT NULL,
            risk_score REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES project (id)
        )
        ''')
        
        # Green Finance Market Data Tabelle
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS green_finance_market_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_type VARCHAR(50) NOT NULL,
            date DATE NOT NULL,
            average_yield REAL NOT NULL,
            average_price REAL NOT NULL,
            market_size_eur REAL NOT NULL,
            volume_traded_eur REAL NOT NULL,
            volatility_percent REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Indizes erstellen
        indices = [
            "CREATE INDEX IF NOT EXISTS idx_green_finance_products_project ON green_finance_products(project_id, status)",
            "CREATE INDEX IF NOT EXISTS idx_green_finance_products_type ON green_finance_products(product_type, maturity_date)",
            "CREATE INDEX IF NOT EXISTS idx_transactions_date ON green_finance_transactions(transaction_date)",
            "CREATE INDEX IF NOT EXISTS idx_performance_date ON green_finance_performance(project_id, reporting_date)",
            "CREATE INDEX IF NOT EXISTS idx_market_data_date ON green_finance_market_data(product_type, date)"
        ]
        
        for index_sql in indices:
            cursor.execute(index_sql)
        
        conn.commit()
        conn.close()
        print("✅ Green Finance Tabellen erfolgreich erstellt")
    
    def get_available_green_bonds(self, min_rating: str = 'BBB', 
                                 max_yield: float = 5.0) -> List[Dict]:
        """Ruft verfügbare Green Bonds ab"""
        
        # Simulierte Green Bond Daten (in Realität würde man echte APIs verwenden)
        available_bonds = [
            {
                'name': 'EU Green Bond 2025',
                'issuer': 'European Union',
                'volume_eur': 100_000_000,
                'interest_rate_percent': 2.8,
                'maturity_date': '2030-12-31',
                'credit_rating': 'AAA',
                'sustainability_rating': 'AAA',
                'green_use_proceeds': 'Renewable energy, energy efficiency, sustainable transport',
                'esg_score': 95.0,
                'carbon_impact_tonnes_co2': 50000
            },
            {
                'name': 'KfW Green Bond 2025',
                'issuer': 'KfW Bank',
                'volume_eur': 75_000_000,
                'interest_rate_percent': 3.2,
                'maturity_date': '2028-06-30',
                'credit_rating': 'AAA',
                'sustainability_rating': 'AA+',
                'green_use_proceeds': 'Climate change mitigation, renewable energy projects',
                'esg_score': 92.0,
                'carbon_impact_tonnes_co2': 35000
            },
            {
                'name': 'Österreich Green Bond 2025',
                'issuer': 'Republic of Austria',
                'volume_eur': 50_000_000,
                'interest_rate_percent': 2.5,
                'maturity_date': '2032-03-15',
                'credit_rating': 'AA+',
                'sustainability_rating': 'AA',
                'green_use_proceeds': 'Sustainable infrastructure, renewable energy',
                'esg_score': 88.0,
                'carbon_impact_tonnes_co2': 25000
            },
            {
                'name': 'Siemens Green Bond 2025',
                'issuer': 'Siemens AG',
                'volume_eur': 30_000_000,
                'interest_rate_percent': 3.8,
                'maturity_date': '2027-09-30',
                'credit_rating': 'A+',
                'sustainability_rating': 'A+',
                'green_use_proceeds': 'Clean technology, energy efficiency',
                'esg_score': 85.0,
                'carbon_impact_tonnes_co2': 15000
            }
        ]
        
        # Filterung basierend auf Kriterien
        filtered_bonds = []
        for bond in available_bonds:
            if (self._rating_to_number(bond['credit_rating']) >= self._rating_to_number(min_rating) and
                bond['interest_rate_percent'] <= max_yield):
                filtered_bonds.append(bond)
        
        return filtered_bonds
    
    def _rating_to_number(self, rating: str) -> int:
        """Konvertiert Rating zu numerischem Wert für Vergleich"""
        rating_map = {
            'AAA': 100, 'AA+': 95, 'AA': 90, 'AA-': 85,
            'A+': 80, 'A': 75, 'A-': 70,
            'BBB+': 65, 'BBB': 60, 'BBB-': 55,
            'BB+': 50, 'BB': 45, 'BB-': 40,
            'B+': 35, 'B': 30, 'B-': 25
        }
        return rating_map.get(rating, 0)
    
    def purchase_green_bond(self, project_id: int, bond_data: Dict, 
                           volume_eur: float) -> Dict:
        """Kauft Green Bond für ein Projekt"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Green Bond in Portfolio einfügen
            cursor.execute('''
            INSERT INTO green_finance_products 
            (project_id, product_type, name, issuer, volume_eur, currency,
             interest_rate_percent, maturity_date, coupon_frequency, credit_rating,
             sustainability_rating, green_use_proceeds, purchase_price_eur,
             current_price_eur, purchase_date, status, esg_score, carbon_impact_tonnes_co2)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                project_id,
                'green_bond',
                bond_data['name'],
                bond_data['issuer'],
                volume_eur,
                'EUR',
                bond_data['interest_rate_percent'],
                bond_data['maturity_date'],
                'annual',
                bond_data['credit_rating'],
                bond_data['sustainability_rating'],
                bond_data['green_use_proceeds'],
                volume_eur,  # purchase_price = volume
                volume_eur,  # current_price = volume (initial)
                datetime.now().date(),
                'active',
                bond_data['esg_score'],
                bond_data['carbon_impact_tonnes_co2'] * (volume_eur / bond_data['volume_eur'])
            ))
            
            product_id = cursor.lastrowid
            
            # Transaktion protokollieren
            cursor.execute('''
            INSERT INTO green_finance_transactions 
            (product_id, project_id, transaction_type, volume_eur, price_eur, transaction_date)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                product_id,
                project_id,
                'buy',
                volume_eur,
                volume_eur,
                datetime.now().date()
            ))
            
            conn.commit()
            
            return {
                'success': True,
                'product_id': product_id,
                'volume_eur': volume_eur,
                'annual_coupon_eur': volume_eur * (bond_data['interest_rate_percent'] / 100)
            }
            
        except Exception as e:
            conn.rollback()
            return {'success': False, 'error': str(e)}
        
        finally:
            conn.close()
    
    def calculate_portfolio_performance(self, project_id: int) -> Dict:
        """Berechnet Portfolio-Performance"""
        
        conn = sqlite3.connect(self.db_path)
        
        # Aktive Produkte abrufen
        products_query = '''
        SELECT * FROM green_finance_products 
        WHERE project_id = ? AND status = 'active'
        '''
        
        products_df = pd.read_sql_query(products_query, conn, params=(project_id,))
        
        if products_df.empty:
            conn.close()
            return self._get_empty_portfolio_performance()
        
        # Performance berechnen
        total_invested = products_df['purchase_price_eur'].sum()
        total_current_value = products_df['current_price_eur'].sum()
        total_returns = total_current_value - total_invested
        total_returns_percent = (total_returns / total_invested * 100) if total_invested > 0 else 0
        
        # ESG-gewichtete Rendite
        esg_weighted_return = 0
        if not products_df.empty:
            esg_scores = products_df['esg_score']
            volumes = products_df['volume_eur']
            esg_weighted_return = (esg_scores * volumes).sum() / volumes.sum()
        
        # Carbon Impact
        total_carbon_impact = products_df['carbon_impact_tonnes_co2'].sum()
        
        # Green Alignment Score (0-100)
        green_alignment_score = min(100, max(0, esg_weighted_return))
        
        # Risk Score (basierend auf Credit Ratings)
        risk_scores = []
        for _, product in products_df.iterrows():
            risk_score = 100 - self._rating_to_number(product['credit_rating'])
            risk_scores.append(risk_score * (product['volume_eur'] / total_invested))
        
        portfolio_risk_score = sum(risk_scores) if risk_scores else 0
        
        # Annualized Return (vereinfacht)
        days_held = (datetime.now().date() - pd.to_datetime(products_df['purchase_date']).min().date()).days
        annualized_return = (total_returns_percent * 365 / days_held) if days_held > 0 else 0
        
        performance = {
            'total_portfolio_value_eur': round(total_current_value, 2),
            'total_invested_eur': round(total_invested, 2),
            'total_returns_eur': round(total_returns, 2),
            'total_returns_percent': round(total_returns_percent, 2),
            'annualized_return_percent': round(annualized_return, 2),
            'esg_weighted_return_percent': round(esg_weighted_return, 2),
            'carbon_impact_total_tonnes_co2': round(total_carbon_impact, 2),
            'green_alignment_score': round(green_alignment_score, 2),
            'risk_score': round(portfolio_risk_score, 2),
            'product_count': len(products_df),
            'average_esg_score': round(products_df['esg_score'].mean(), 2) if not products_df.empty else 0
        }
        
        # Performance in Datenbank speichern
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO green_finance_performance 
        (project_id, reporting_date, total_portfolio_value_eur, total_invested_eur,
         total_returns_eur, total_returns_percent, annualized_return_percent,
         esg_weighted_return_percent, carbon_impact_total_tonnes_co2,
         green_alignment_score, risk_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            project_id,
            datetime.now().date(),
            performance['total_portfolio_value_eur'],
            performance['total_invested_eur'],
            performance['total_returns_eur'],
            performance['total_returns_percent'],
            performance['annualized_return_percent'],
            performance['esg_weighted_return_percent'],
            performance['carbon_impact_total_tonnes_co2'],
            performance['green_alignment_score'],
            performance['risk_score']
        ))
        
        conn.commit()
        conn.close()
        
        return performance
    
    def _get_empty_portfolio_performance(self) -> Dict:
        """Gibt leere Portfolio-Performance zurück"""
        return {
            'total_portfolio_value_eur': 0,
            'total_invested_eur': 0,
            'total_returns_eur': 0,
            'total_returns_percent': 0,
            'annualized_return_percent': 0,
            'esg_weighted_return_percent': 0,
            'carbon_impact_total_tonnes_co2': 0,
            'green_alignment_score': 0,
            'risk_score': 0,
            'product_count': 0,
            'average_esg_score': 0
        }
    
    def get_green_finance_recommendations(self, project_id: int, 
                                        available_capital_eur: float) -> List[Dict]:
        """Generiert Green Finance Empfehlungen"""
        
        recommendations = []
        
        # Portfolio Performance abrufen
        performance = self.calculate_portfolio_performance(project_id)
        
        # Verfügbare Green Bonds abrufen
        available_bonds = self.get_available_green_bonds()
        
        # Empfehlungen basierend auf Portfolio-Status
        if performance['product_count'] == 0:
            # Erste Investition
            recommendations.append({
                'type': 'first_investment',
                'priority': 'high',
                'title': 'Erste Green Bond Investition',
                'description': 'Beginnen Sie mit einer Green Bond Investition für nachhaltige Renditen',
                'suggested_product': available_bonds[0] if available_bonds else None,
                'suggested_amount_eur': min(available_capital_eur, 100_000),
                'expected_return_percent': available_bonds[0]['interest_rate_percent'] if available_bonds else 0,
                'esg_impact': 'hoch'
            })
        
        elif performance['esg_weighted_return_percent'] < 85:
            # ESG-Score verbessern
            high_esg_bonds = [b for b in available_bonds if b['esg_score'] >= 90]
            if high_esg_bonds:
                recommendations.append({
                    'type': 'esg_improvement',
                    'priority': 'medium',
                    'title': 'ESG-Score verbessern',
                    'description': 'Investieren Sie in hochwertige ESG-Produkte',
                    'suggested_product': high_esg_bonds[0],
                    'suggested_amount_eur': min(available_capital_eur * 0.3, 50_000),
                    'expected_return_percent': high_esg_bonds[0]['interest_rate_percent'],
                    'esg_impact': 'sehr hoch'
                })
        
        if performance['risk_score'] > 30:
            # Risiko reduzieren
            low_risk_bonds = [b for b in available_bonds if self._rating_to_number(b['credit_rating']) >= 85]
            if low_risk_bonds:
                recommendations.append({
                    'type': 'risk_reduction',
                    'priority': 'high',
                    'title': 'Portfolio-Risiko reduzieren',
                    'description': 'Investieren Sie in hochwertige, risikoarme Green Bonds',
                    'suggested_product': low_risk_bonds[0],
                    'suggested_amount_eur': min(available_capital_eur * 0.4, 75_000),
                    'expected_return_percent': low_risk_bonds[0]['interest_rate_percent'],
                    'esg_impact': 'hoch'
                })
        
        # Diversifikation
        if performance['product_count'] < 3 and available_capital_eur > 50_000:
            recommendations.append({
                'type': 'diversification',
                'priority': 'medium',
                'title': 'Portfolio diversifizieren',
                'description': 'Erweitern Sie Ihr Portfolio um verschiedene Green Finance Produkte',
                'suggested_product': available_bonds[1] if len(available_bonds) > 1 else available_bonds[0],
                'suggested_amount_eur': min(available_capital_eur * 0.2, 25_000),
                'expected_return_percent': available_bonds[1]['interest_rate_percent'] if len(available_bonds) > 1 else 0,
                'esg_impact': 'mittel'
            })
        
        return recommendations
    
    async def fetch_market_data(self) -> Dict:
        """Ruft aktuelle Green Finance Marktdaten ab"""
        
        market_data = {}
        
        try:
            # Simulierte API-Aufrufe (in Realität würde man echte APIs verwenden)
            async with aiohttp.ClientSession() as session:
                # Green Bond Marktdaten
                market_data['green_bonds'] = {
                    'average_yield': 2.8 + (await self._get_random_change()),
                    'average_price': 102.5 + (await self._get_random_change()),
                    'market_size_eur': 500_000_000_000,
                    'volume_traded_eur': 2_500_000_000,
                    'volatility_percent': 0.8
                }
                
                # Sustainability Bond Marktdaten
                market_data['sustainability_bonds'] = {
                    'average_yield': 3.2 + (await self._get_random_change()),
                    'average_price': 101.8 + (await self._get_random_change()),
                    'market_size_eur': 300_000_000_000,
                    'volume_traded_eur': 1_800_000_000,
                    'volatility_percent': 1.2
                }
                
                # Carbon Credit Marktdaten
                market_data['carbon_credits'] = {
                    'average_price_eur_per_tonne': 85.50 + (await self._get_random_change()),
                    'market_size_eur': 950_000_000_000,
                    'volume_traded_eur': 3_200_000_000,
                    'volatility_percent': 2.5
                }
                
        except Exception as e:
            print(f"Fehler beim Abrufen der Marktdaten: {e}")
            # Fallback zu Standard-Daten
            market_data = self.market_data
        
        return market_data
    
    async def _get_random_change(self) -> float:
        """Simuliert zufällige Marktbewegungen"""
        import random
        return random.uniform(-0.1, 0.1)
    
    def calculate_green_finance_contribution_to_esg(self, project_id: int) -> Dict:
        """Berechnet Beitrag der Green Finance zu ESG-Scores"""
        
        performance = self.calculate_portfolio_performance(project_id)
        
        # ESG-Beitrag berechnen
        esg_contribution = {
            'environmental_contribution': {
                'carbon_impact_tonnes_co2': performance['carbon_impact_total_tonnes_co2'],
                'green_alignment_score': performance['green_alignment_score'],
                'contribution_percent': min(20, performance['carbon_impact_total_tonnes_co2'] * 0.1)
            },
            'social_contribution': {
                'portfolio_value_eur': performance['total_portfolio_value_eur'],
                'sustainable_investment_share': 100 if performance['total_portfolio_value_eur'] > 0 else 0,
                'contribution_percent': min(15, performance['total_portfolio_value_eur'] / 10000)
            },
            'governance_contribution': {
                'average_esg_score': performance['average_esg_score'],
                'risk_score': performance['risk_score'],
                'contribution_percent': min(10, max(0, 10 - performance['risk_score'] / 10))
            },
            'overall_esg_boost': min(30, 
                min(20, performance['carbon_impact_total_tonnes_co2'] * 0.1) +
                min(15, performance['total_portfolio_value_eur'] / 10000) +
                min(10, max(0, 10 - performance['risk_score'] / 10))
            )
        }
        
        return esg_contribution

def main():
    """Hauptfunktion für Green Finance Integration"""
    print("🌱 Green Finance Integration für BESS-Simulation")
    print("=" * 60)
    
    # Green Finance Integration initialisieren
    green_finance = GreenFinanceIntegration()
    
    # Tabellen erstellen
    green_finance.create_green_finance_tables()
    
    print("✅ Green Finance Integration erfolgreich initialisiert")
    print("📊 Features:")
    print("   - Green Bonds Trading")
    print("   - Sustainability Bonds")
    print("   - Portfolio Performance Tracking")
    print("   - ESG-gewichtete Renditen")
    print("   - Carbon Impact Tracking")
    print("   - Intelligente Empfehlungen")
    print("   - Marktdaten Integration")
    print("💰 Verfügbare Produkte:")
    
    # Verfügbare Green Bonds anzeigen
    available_bonds = green_finance.get_available_green_bonds()
    for bond in available_bonds[:3]:  # Erste 3 anzeigen
        print(f"   - {bond['name']}: {bond['interest_rate_percent']}% p.a., Rating: {bond['credit_rating']}")

if __name__ == '__main__':
    main()
