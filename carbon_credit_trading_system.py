#!/usr/bin/env python3
"""
Carbon Credit Trading System für BESS-Simulation
Implementiert CO₂-Zertifikate Trading und Green Finance Integration
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional, Tuple
import requests
from dataclasses import dataclass
import asyncio
import aiohttp

@dataclass
class CarbonCredit:
    """Carbon Credit Datenstruktur"""
    id: Optional[int]
    project_id: int
    credit_type: str  # 'VER', 'CER', 'VCS', 'Gold Standard'
    volume_tonnes_co2: float
    price_eur_per_tonne: float
    certification_standard: str
    vintage_year: int
    country: str
    status: str  # 'available', 'reserved', 'sold', 'retired'
    created_at: datetime
    expires_at: Optional[datetime] = None

class CarbonCreditTradingSystem:
    """Carbon Credit Trading und Green Finance System"""
    
    def __init__(self, db_path: str = "instance/bess.db"):
        self.db_path = db_path
        self.credit_prices = {
            'VER': 8.50,      # Verified Emission Reductions
            'CER': 2.30,      # Certified Emission Reductions
            'VCS': 12.00,     # Verified Carbon Standard
            'Gold Standard': 15.50,  # Gold Standard
            'CCER': 5.20      # Chinese Certified Emission Reductions
        }
        
        # Carbon Credit Markt-APIs
        self.market_apis = {
            'verra': 'https://registry.verra.org/api',
            'gold_standard': 'https://www.goldstandard.org/api',
            'carbon_trade_exchange': 'https://ctx.green/api'
        }
    
    def create_carbon_credit_tables(self):
        """Erstellt Carbon Credit Trading Tabellen"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Carbon Credits Tabelle
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS carbon_credits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            credit_type VARCHAR(50) NOT NULL,
            volume_tonnes_co2 REAL NOT NULL,
            price_eur_per_tonne REAL NOT NULL,
            certification_standard VARCHAR(100) NOT NULL,
            vintage_year INTEGER NOT NULL,
            country VARCHAR(10) NOT NULL,
            status VARCHAR(20) DEFAULT 'available',
            co2_reduction_kg REAL NOT NULL,
            verification_date DATE,
            expires_at DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES project (id)
        )
        ''')
        
        # Carbon Credit Transactions Tabelle
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS carbon_credit_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            credit_id INTEGER NOT NULL,
            buyer_project_id INTEGER,
            seller_project_id INTEGER NOT NULL,
            transaction_type VARCHAR(20) NOT NULL, -- 'buy', 'sell', 'retire', 'transfer'
            volume_tonnes_co2 REAL NOT NULL,
            price_eur_per_tonne REAL NOT NULL,
            total_value_eur REAL NOT NULL,
            transaction_date DATE NOT NULL,
            status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'completed', 'cancelled'
            payment_status VARCHAR(20) DEFAULT 'pending',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (credit_id) REFERENCES carbon_credits (id),
            FOREIGN KEY (buyer_project_id) REFERENCES project (id),
            FOREIGN KEY (seller_project_id) REFERENCES project (id)
        )
        ''')
        
        # Green Finance Portfolio Tabelle
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS green_finance_portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            portfolio_type VARCHAR(50) NOT NULL, -- 'carbon_credits', 'green_bonds', 'sustainability_bonds'
            asset_name VARCHAR(100) NOT NULL,
            volume REAL NOT NULL,
            unit VARCHAR(20) NOT NULL,
            purchase_price_eur REAL NOT NULL,
            current_price_eur REAL NOT NULL,
            current_value_eur REAL NOT NULL,
            profit_loss_eur REAL NOT NULL,
            profit_loss_percent REAL NOT NULL,
            purchase_date DATE NOT NULL,
            maturity_date DATE,
            status VARCHAR(20) DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES project (id)
        )
        ''')
        
        # ESG Performance Tracking Tabelle
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS esg_performance_tracking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            reporting_period_start DATE NOT NULL,
            reporting_period_end DATE NOT NULL,
            environmental_score REAL NOT NULL,
            social_score REAL NOT NULL,
            governance_score REAL NOT NULL,
            overall_esg_score REAL NOT NULL,
            carbon_footprint_tonnes_co2 REAL NOT NULL,
            carbon_credits_generated INTEGER NOT NULL,
            carbon_credits_sold INTEGER NOT NULL,
            carbon_credits_retired INTEGER NOT NULL,
            green_finance_value_eur REAL NOT NULL,
            sustainability_rating VARCHAR(10), -- 'AAA', 'AA', 'A', 'BBB', 'BB', 'B'
            compliance_status VARCHAR(20) DEFAULT 'compliant',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES project (id)
        )
        ''')
        
        # Indizes erstellen
        indices = [
            "CREATE INDEX IF NOT EXISTS idx_carbon_credits_project_status ON carbon_credits(project_id, status)",
            "CREATE INDEX IF NOT EXISTS idx_carbon_credits_type_vintage ON carbon_credits(credit_type, vintage_year)",
            "CREATE INDEX IF NOT EXISTS idx_transactions_date ON carbon_credit_transactions(transaction_date)",
            "CREATE INDEX IF NOT EXISTS idx_green_finance_project_type ON green_finance_portfolio(project_id, portfolio_type)",
            "CREATE INDEX IF NOT EXISTS idx_esg_performance_period ON esg_performance_tracking(project_id, reporting_period_start)"
        ]
        
        for index_sql in indices:
            cursor.execute(index_sql)
        
        conn.commit()
        conn.close()
        print("✅ Carbon Credit Trading Tabellen erfolgreich erstellt")
    
    def generate_carbon_credits_from_co2_reduction(self, project_id: int, 
                                                  co2_reduction_kg: float,
                                                  credit_type: str = 'VER') -> CarbonCredit:
        """Generiert Carbon Credits aus CO₂-Einsparungen"""
        
        # CO₂ von kg in Tonnen umrechnen
        volume_tonnes = co2_reduction_kg / 1000
        
        # Preis basierend auf Credit-Typ
        price_per_tonne = self.credit_prices.get(credit_type, 8.50)
        
        # Carbon Credit erstellen
        credit = CarbonCredit(
            id=None,
            project_id=project_id,
            credit_type=credit_type,
            volume_tonnes_co2=volume_tonnes,
            price_eur_per_tonne=price_per_tonne,
            certification_standard=credit_type,
            vintage_year=datetime.now().year,
            country='AT',  # Österreich
            status='available',
            created_at=datetime.now()
        )
        
        return credit
    
    def save_carbon_credit(self, credit: CarbonCredit) -> int:
        """Speichert Carbon Credit in der Datenbank"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO carbon_credits 
        (project_id, credit_type, volume_tonnes_co2, price_eur_per_tonne,
         certification_standard, vintage_year, country, status, co2_reduction_kg)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            credit.project_id,
            credit.credit_type,
            credit.volume_tonnes_co2,
            credit.price_eur_per_tonne,
            credit.certification_standard,
            credit.vintage_year,
            credit.country,
            credit.status,
            credit.volume_tonnes_co2 * 1000  # Tonnen zu kg
        ))
        
        credit_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return credit_id
    
    def get_available_credits(self, project_id: Optional[int] = None) -> List[Dict]:
        """Ruft verfügbare Carbon Credits ab"""
        conn = sqlite3.connect(self.db_path)
        
        if project_id:
            query = '''
            SELECT * FROM carbon_credits 
            WHERE status = 'available' AND project_id = ?
            ORDER BY created_at DESC
            '''
            df = pd.read_sql_query(query, conn, params=(project_id,))
        else:
            query = '''
            SELECT * FROM carbon_credits 
            WHERE status = 'available'
            ORDER BY created_at DESC
            '''
            df = pd.read_sql_query(query, conn)
        
        conn.close()
        return df.to_dict('records')
    
    def execute_credit_transaction(self, credit_id: int, buyer_project_id: int,
                                  transaction_type: str = 'buy',
                                  volume_tonnes: Optional[float] = None) -> Dict:
        """Führt Carbon Credit Transaktion aus"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Credit-Details abrufen
        cursor.execute('SELECT * FROM carbon_credits WHERE id = ?', (credit_id,))
        credit = cursor.fetchone()
        
        if not credit:
            conn.close()
            return {'success': False, 'error': 'Carbon Credit nicht gefunden'}
        
        if credit[9] != 'available':  # status
            conn.close()
            return {'success': False, 'error': 'Carbon Credit nicht verfügbar'}
        
        # Transaktions-Volumen bestimmen
        if volume_tonnes is None:
            volume_tonnes = credit[3]  # volume_tonnes_co2
        
        if volume_tonnes > credit[3]:
            conn.close()
            return {'success': False, 'error': 'Transaktions-Volumen zu hoch'}
        
        # Transaktion erstellen
        total_value = volume_tonnes * credit[4]  # volume * price_eur_per_tonne
        
        cursor.execute('''
        INSERT INTO carbon_credit_transactions 
        (credit_id, buyer_project_id, seller_project_id, transaction_type,
         volume_tonnes_co2, price_eur_per_tonne, total_value_eur, transaction_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            credit_id,
            buyer_project_id,
            credit[1],  # seller_project_id
            transaction_type,
            volume_tonnes,
            credit[4],  # price_eur_per_tonne
            total_value,
            datetime.now().date()
        ))
        
        transaction_id = cursor.lastrowid
        
        # Credit-Status aktualisieren
        if volume_tonnes == credit[3]:  # Vollständige Transaktion
            cursor.execute('''
            UPDATE carbon_credits SET status = 'sold', updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            ''', (credit_id,))
        else:  # Teilweise Transaktion
            cursor.execute('''
            UPDATE carbon_credits 
            SET volume_tonnes_co2 = volume_tonnes_co2 - ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            ''', (volume_tonnes, credit_id))
        
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'transaction_id': transaction_id,
            'total_value_eur': total_value,
            'volume_tonnes_co2': volume_tonnes
        }
    
    def get_green_finance_portfolio(self, project_id: int) -> Dict:
        """Ruft Green Finance Portfolio ab"""
        conn = sqlite3.connect(self.db_path)
        
        # Portfolio-Daten abrufen
        query = '''
        SELECT 
            portfolio_type,
            SUM(current_value_eur) as total_value,
            SUM(profit_loss_eur) as total_pnl,
            COUNT(*) as asset_count
        FROM green_finance_portfolio 
        WHERE project_id = ? AND status = 'active'
        GROUP BY portfolio_type
        '''
        
        df = pd.read_sql_query(query, conn, params=(project_id,))
        conn.close()
        
        portfolio = {
            'total_value_eur': df['total_value'].sum() if not df.empty else 0,
            'total_pnl_eur': df['total_pnl'].sum() if not df.empty else 0,
            'asset_types': df.to_dict('records') if not df.empty else [],
            'performance_percent': 0
        }
        
        if portfolio['total_value_eur'] > 0:
            portfolio['performance_percent'] = (
                portfolio['total_pnl_eur'] / portfolio['total_value_eur'] * 100
            )
        
        return portfolio
    
    def update_esg_performance(self, project_id: int, 
                              reporting_period_start: str,
                              reporting_period_end: str) -> Dict:
        """Aktualisiert ESG Performance Tracking"""
        
        # CO₂-Daten aus bestehendem System abrufen
        conn = sqlite3.connect(self.db_path)
        
        # CO₂-Einsparungen berechnen
        co2_query = '''
        SELECT 
            SUM(co2_saved_kg) as total_co2_saved,
            SUM(renewable_energy_kwh) as total_renewable_energy,
            AVG(efficiency_percent) as avg_efficiency
        FROM co2_balance 
        WHERE project_id = ? AND date BETWEEN ? AND ?
        '''
        
        co2_df = pd.read_sql_query(co2_query, conn, params=(
            project_id, reporting_period_start, reporting_period_end
        ))
        
        # Carbon Credits generiert/verkauft
        credits_query = '''
        SELECT 
            COUNT(*) as credits_generated,
            SUM(volume_tonnes_co2) as total_volume_generated
        FROM carbon_credits 
        WHERE project_id = ? AND created_at BETWEEN ? AND ?
        '''
        
        credits_df = pd.read_sql_query(credits_query, conn, params=(
            project_id, reporting_period_start, reporting_period_end
        ))
        
        # Carbon Credits verkauft
        sold_query = '''
        SELECT COUNT(*) as credits_sold
        FROM carbon_credit_transactions 
        WHERE seller_project_id = ? AND transaction_date BETWEEN ? AND ?
        '''
        
        sold_df = pd.read_sql_query(sold_query, conn, params=(
            project_id, reporting_period_start, reporting_period_end
        ))
        
        conn.close()
        
        # ESG-Scores berechnen
        co2_saved = co2_df.iloc[0]['total_co2_saved'] if not co2_df.empty else 0
        renewable_energy = co2_df.iloc[0]['total_renewable_energy'] if not co2_df.empty else 0
        efficiency = co2_df.iloc[0]['avg_efficiency'] if not co2_df.empty else 0
        
        # Environmental Score (0-100)
        environmental_score = min(100, max(0, 
            (min(100, co2_saved / 1000) * 0.6) +  # CO₂-Einsparungen
            (min(100, renewable_energy / 10000) * 0.4)  # Erneuerbare Energie
        ))
        
        # Social Score (0-100)
        social_score = min(100, max(0, 
            efficiency * 0.8 +  # Energieeffizienz
            (min(100, (co2_saved / 1000) * 10) * 0.2)  # CO₂-Reduktion
        ))
        
        # Governance Score (Standard 85)
        governance_score = 85
        
        # Overall ESG Score
        overall_esg_score = (
            environmental_score * 0.4 + 
            social_score * 0.3 + 
            governance_score * 0.3
        )
        
        # Sustainability Rating bestimmen
        if overall_esg_score >= 90:
            sustainability_rating = 'AAA'
        elif overall_esg_score >= 80:
            sustainability_rating = 'AA'
        elif overall_esg_score >= 70:
            sustainability_rating = 'A'
        elif overall_esg_score >= 60:
            sustainability_rating = 'BBB'
        elif overall_esg_score >= 50:
            sustainability_rating = 'BB'
        else:
            sustainability_rating = 'B'
        
        # Green Finance Portfolio Value
        portfolio = self.get_green_finance_portfolio(project_id)
        
        esg_data = {
            'project_id': project_id,
            'reporting_period_start': reporting_period_start,
            'reporting_period_end': reporting_period_end,
            'environmental_score': round(environmental_score, 1),
            'social_score': round(social_score, 1),
            'governance_score': governance_score,
            'overall_esg_score': round(overall_esg_score, 1),
            'carbon_footprint_tonnes_co2': round(co2_saved / 1000, 2),
            'carbon_credits_generated': credits_df.iloc[0]['credits_generated'] if not credits_df.empty else 0,
            'carbon_credits_sold': sold_df.iloc[0]['credits_sold'] if not sold_df.empty else 0,
            'carbon_credits_retired': 0,  # TODO: Implementieren
            'green_finance_value_eur': portfolio['total_value_eur'],
            'sustainability_rating': sustainability_rating,
            'compliance_status': 'compliant'
        }
        
        # ESG Performance speichern
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT OR REPLACE INTO esg_performance_tracking 
        (project_id, reporting_period_start, reporting_period_end,
         environmental_score, social_score, governance_score, overall_esg_score,
         carbon_footprint_tonnes_co2, carbon_credits_generated, carbon_credits_sold,
         carbon_credits_retired, green_finance_value_eur, sustainability_rating,
         compliance_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            esg_data['project_id'], esg_data['reporting_period_start'], esg_data['reporting_period_end'],
            esg_data['environmental_score'], esg_data['social_score'], esg_data['governance_score'],
            esg_data['overall_esg_score'], esg_data['carbon_footprint_tonnes_co2'],
            esg_data['carbon_credits_generated'], esg_data['carbon_credits_sold'],
            esg_data['carbon_credits_retired'], esg_data['green_finance_value_eur'],
            esg_data['sustainability_rating'], esg_data['compliance_status']
        ))
        
        conn.commit()
        conn.close()
        
        return esg_data
    
    async def fetch_market_prices(self) -> Dict:
        """Ruft aktuelle Carbon Credit Marktpreise ab"""
        prices = {}
        
        try:
            # Simulierte API-Aufrufe (in Realität würde man echte APIs verwenden)
            async with aiohttp.ClientSession() as session:
                # Verra Registry (simuliert)
                prices['VER'] = 8.50
                prices['VCS'] = 12.00
                
                # Gold Standard (simuliert)
                prices['Gold Standard'] = 15.50
                
                # Carbon Trade Exchange (simuliert)
                prices['CER'] = 2.30
                prices['CCER'] = 5.20
                
        except Exception as e:
            print(f"Fehler beim Abrufen der Marktpreise: {e}")
            # Fallback zu Standard-Preisen
            prices = self.credit_prices
        
        return prices
    
    def calculate_carbon_credit_revenue(self, project_id: int, 
                                      period_start: str, period_end: str) -> Dict:
        """Berechnet Carbon Credit Erlöse für einen Zeitraum"""
        conn = sqlite3.connect(self.db_path)
        
        # CO₂-Einsparungen für den Zeitraum
        co2_query = '''
        SELECT SUM(co2_saved_kg) as total_co2_saved
        FROM co2_balance 
        WHERE project_id = ? AND date BETWEEN ? AND ?
        '''
        
        co2_df = pd.read_sql_query(co2_query, conn, params=(
            project_id, period_start, period_end
        ))
        
        # Verkaufte Carbon Credits
        sales_query = '''
        SELECT 
            SUM(total_value_eur) as total_revenue,
            SUM(volume_tonnes_co2) as total_volume_sold,
            COUNT(*) as transaction_count
        FROM carbon_credit_transactions 
        WHERE seller_project_id = ? AND transaction_date BETWEEN ? AND ?
        '''
        
        sales_df = pd.read_sql_query(sales_query, conn, params=(
            project_id, period_start, period_end
        ))
        
        conn.close()
        
        co2_saved = co2_df.iloc[0]['total_co2_saved'] if not co2_df.empty else 0
        total_revenue = sales_df.iloc[0]['total_revenue'] if not sales_df.empty else 0
        total_volume_sold = sales_df.iloc[0]['total_volume_sold'] if not sales_df.empty else 0
        
        # Potentielle Erlöse (wenn alle CO₂-Einsparungen als Credits verkauft würden)
        potential_credits = co2_saved / 1000  # kg zu Tonnen
        potential_revenue = potential_credits * self.credit_prices['VER']
        
        return {
            'co2_saved_kg': co2_saved,
            'potential_credits_tonnes': round(potential_credits, 2),
            'potential_revenue_eur': round(potential_revenue, 2),
            'actual_revenue_eur': total_revenue,
            'actual_credits_sold_tonnes': total_volume_sold,
            'revenue_utilization_percent': round(
                (total_revenue / potential_revenue * 100) if potential_revenue > 0 else 0, 1
            )
        }

def main():
    """Hauptfunktion für Carbon Credit Trading System"""
    print("🌱 Carbon Credit Trading System für BESS-Simulation")
    print("=" * 60)
    
    # Carbon Credit Trading System initialisieren
    trading_system = CarbonCreditTradingSystem()
    
    # Tabellen erstellen
    trading_system.create_carbon_credit_tables()
    
    print("✅ Carbon Credit Trading System erfolgreich initialisiert")
    print("📊 Tabellen erstellt:")
    print("   - carbon_credits")
    print("   - carbon_credit_transactions")
    print("   - green_finance_portfolio")
    print("   - esg_performance_tracking")
    print("🔍 Indizes erstellt für optimale Performance")
    print("💰 Carbon Credit Preise:")
    for credit_type, price in trading_system.credit_prices.items():
        print(f"   - {credit_type}: {price} €/tCO₂")

if __name__ == '__main__':
    main()
