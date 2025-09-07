#!/usr/bin/env python3
"""
CO₂-Tracking System für BESS-Simulation
Berechnet CO₂-Einsparungen und Nachhaltigkeits-Metriken
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional, Tuple

class CO2TrackingSystem:
    """CO₂-Tracking und Nachhaltigkeits-Analytics System"""
    
    def __init__(self, db_path: str = "instance/bess.db"):
        self.db_path = db_path
        self.co2_factors = {
            # CO₂-Emissionsfaktoren (kg CO₂/kWh)
            'grid_mix_de': 0.485,  # Deutschland 2023
            'grid_mix_at': 0.156,  # Österreich 2023
            'grid_mix_ch': 0.012,  # Schweiz 2023
            'solar': 0.041,        # Photovoltaik
            'wind': 0.011,         # Windkraft
            'hydro': 0.024,        # Wasserkraft
            'battery': 0.100,      # Batterie (Herstellung + Betrieb)
            'grid_loss': 0.05      # Netzverluste
        }
        
    def create_co2_tables(self):
        """Erstellt CO₂-Tracking Tabellen"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # CO₂-Bilanz Tabelle
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS co2_balance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            date DATE NOT NULL,
            energy_stored_kwh REAL NOT NULL,
            energy_discharged_kwh REAL NOT NULL,
            grid_energy_kwh REAL NOT NULL,
            renewable_energy_kwh REAL NOT NULL,
            co2_saved_kg REAL NOT NULL,
            co2_emitted_kg REAL NOT NULL,
            net_co2_balance_kg REAL NOT NULL,
            efficiency_percent REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES project (id)
        )
        ''')
        
        # CO₂-Faktoren Tabelle
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS co2_factors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            energy_source VARCHAR(50) NOT NULL,
            country VARCHAR(10) NOT NULL,
            co2_factor_kg_per_kwh REAL NOT NULL,
            year INTEGER NOT NULL,
            source VARCHAR(255),
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Nachhaltigkeits-Metriken Tabelle
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sustainability_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            period_start DATE NOT NULL,
            period_end DATE NOT NULL,
            period_type VARCHAR(20) NOT NULL, -- daily, weekly, monthly, yearly
            total_energy_kwh REAL NOT NULL,
            renewable_share_percent REAL NOT NULL,
            co2_saved_total_kg REAL NOT NULL,
            co2_intensity_kg_per_kwh REAL NOT NULL,
            energy_efficiency_percent REAL NOT NULL,
            cost_savings_eur REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES project (id)
        )
        ''')
        
        # ESG-Reporting Tabelle
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS esg_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            report_type VARCHAR(50) NOT NULL, -- monthly, quarterly, yearly
            report_period_start DATE NOT NULL,
            report_period_end DATE NOT NULL,
            environmental_score REAL NOT NULL,
            social_score REAL NOT NULL,
            governance_score REAL NOT NULL,
            overall_esg_score REAL NOT NULL,
            co2_reduction_kg REAL NOT NULL,
            renewable_energy_share_percent REAL NOT NULL,
            energy_efficiency_improvement_percent REAL NOT NULL,
            report_data TEXT, -- JSON mit detaillierten Daten
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES project (id)
        )
        ''')
        
        # Indizes erstellen
        indices = [
            "CREATE INDEX IF NOT EXISTS idx_co2_balance_project_date ON co2_balance(project_id, date)",
            "CREATE INDEX IF NOT EXISTS idx_co2_balance_date ON co2_balance(date)",
            "CREATE INDEX IF NOT EXISTS idx_sustainability_metrics_project_period ON sustainability_metrics(project_id, period_type, period_start)",
            "CREATE INDEX IF NOT EXISTS idx_esg_reports_project_type ON esg_reports(project_id, report_type, report_period_start)"
        ]
        
        for index_sql in indices:
            cursor.execute(index_sql)
        
        # Standard CO₂-Faktoren einfügen
        self._insert_default_co2_factors(cursor)
        
        conn.commit()
        conn.close()
        print("✅ CO₂-Tracking Tabellen erfolgreich erstellt")
    
    def _insert_default_co2_factors(self, cursor):
        """Fügt Standard CO₂-Faktoren ein"""
        factors = [
            ('grid_mix', 'DE', 0.485, 2023, 'Umweltbundesamt Deutschland'),
            ('grid_mix', 'AT', 0.156, 2023, 'Umweltbundesamt Österreich'),
            ('grid_mix', 'CH', 0.012, 2023, 'Bundesamt für Energie Schweiz'),
            ('solar', 'EU', 0.041, 2023, 'IEA Photovoltaic Power Systems Programme'),
            ('wind', 'EU', 0.011, 2023, 'IEA Wind Technology Collaboration Programme'),
            ('hydro', 'EU', 0.024, 2023, 'IEA Hydropower Technology Collaboration Programme'),
            ('battery', 'EU', 0.100, 2023, 'Fraunhofer ISE Studie'),
            ('grid_loss', 'EU', 0.050, 2023, 'ENTSO-E Grid Losses')
        ]
        
        for source, country, factor, year, source_ref in factors:
            cursor.execute('''
            INSERT OR IGNORE INTO co2_factors (energy_source, country, co2_factor_kg_per_kwh, year, source)
            VALUES (?, ?, ?, ?, ?)
            ''', (source, country, factor, year, source_ref))
    
    def calculate_co2_balance(self, project_id: int, date: str, 
                            energy_data: Dict) -> Dict:
        """Berechnet CO₂-Bilanz für einen Tag"""
        
        # Energie-Daten extrahieren
        energy_stored = energy_data.get('energy_stored_kwh', 0)
        energy_discharged = energy_data.get('energy_discharged_kwh', 0)
        grid_energy = energy_data.get('grid_energy_kwh', 0)
        renewable_energy = energy_data.get('renewable_energy_kwh', 0)
        
        # CO₂-Faktoren anwenden
        co2_factor_grid = self.co2_factors.get('grid_mix_at', 0.156)  # Österreich
        co2_factor_renewable = self.co2_factors.get('solar', 0.041)   # Erneuerbare
        co2_factor_battery = self.co2_factors.get('battery', 0.100)   # Batterie
        
        # CO₂-Berechnungen
        co2_saved = (energy_discharged * co2_factor_grid) - (energy_discharged * co2_factor_renewable)
        co2_emitted = (grid_energy * co2_factor_grid) + (energy_stored * co2_factor_battery)
        net_co2_balance = co2_saved - co2_emitted
        
        # Effizienz berechnen
        total_energy = energy_stored + energy_discharged
        efficiency = (energy_discharged / total_energy * 100) if total_energy > 0 else 0
        
        return {
            'project_id': project_id,
            'date': date,
            'energy_stored_kwh': energy_stored,
            'energy_discharged_kwh': energy_discharged,
            'grid_energy_kwh': grid_energy,
            'renewable_energy_kwh': renewable_energy,
            'co2_saved_kg': round(co2_saved, 2),
            'co2_emitted_kg': round(co2_emitted, 2),
            'net_co2_balance_kg': round(net_co2_balance, 2),
            'efficiency_percent': round(efficiency, 2)
        }
    
    def save_co2_balance(self, co2_data: Dict):
        """Speichert CO₂-Bilanz in der Datenbank"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT OR REPLACE INTO co2_balance 
        (project_id, date, energy_stored_kwh, energy_discharged_kwh, 
         grid_energy_kwh, renewable_energy_kwh, co2_saved_kg, co2_emitted_kg, 
         net_co2_balance_kg, efficiency_percent)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            co2_data['project_id'],
            co2_data['date'],
            co2_data['energy_stored_kwh'],
            co2_data['energy_discharged_kwh'],
            co2_data['grid_energy_kwh'],
            co2_data['renewable_energy_kwh'],
            co2_data['co2_saved_kg'],
            co2_data['co2_emitted_kg'],
            co2_data['net_co2_balance_kg'],
            co2_data['efficiency_percent']
        ))
        
        conn.commit()
        conn.close()
    
    def generate_sustainability_metrics(self, project_id: int, 
                                      period_start: str, period_end: str,
                                      period_type: str = 'monthly') -> Dict:
        """Generiert Nachhaltigkeits-Metriken für einen Zeitraum"""
        
        conn = sqlite3.connect(self.db_path)
        
        # CO₂-Daten für den Zeitraum abrufen
        query = '''
        SELECT 
            SUM(energy_stored_kwh) as total_energy_stored,
            SUM(energy_discharged_kwh) as total_energy_discharged,
            SUM(grid_energy_kwh) as total_grid_energy,
            SUM(renewable_energy_kwh) as total_renewable_energy,
            SUM(co2_saved_kg) as total_co2_saved,
            SUM(co2_emitted_kg) as total_co2_emitted,
            AVG(efficiency_percent) as avg_efficiency
        FROM co2_balance 
        WHERE project_id = ? AND date BETWEEN ? AND ?
        '''
        
        df = pd.read_sql_query(query, conn, params=(project_id, period_start, period_end))
        
        if df.empty or df.iloc[0]['total_energy_stored'] is None:
            conn.close()
            return self._get_empty_metrics(project_id, period_start, period_end, period_type)
        
        row = df.iloc[0]
        
        # Metriken berechnen
        total_energy = row['total_energy_stored'] + row['total_energy_discharged']
        renewable_share = (row['total_renewable_energy'] / total_energy * 100) if total_energy > 0 else 0
        co2_intensity = (row['total_co2_emitted'] / total_energy) if total_energy > 0 else 0
        
        # Kosteneinsparungen schätzen (0.30€/kWh für erneuerbare Energie)
        cost_savings = row['total_renewable_energy'] * 0.30
        
        metrics = {
            'project_id': project_id,
            'period_start': period_start,
            'period_end': period_end,
            'period_type': period_type,
            'total_energy_kwh': round(total_energy, 2),
            'renewable_share_percent': round(renewable_share, 2),
            'co2_saved_total_kg': round(row['total_co2_saved'], 2),
            'co2_intensity_kg_per_kwh': round(co2_intensity, 3),
            'energy_efficiency_percent': round(row['avg_efficiency'], 2),
            'cost_savings_eur': round(cost_savings, 2)
        }
        
        # Metriken speichern
        cursor = conn.cursor()
        cursor.execute('''
        INSERT OR REPLACE INTO sustainability_metrics 
        (project_id, period_start, period_end, period_type, total_energy_kwh,
         renewable_share_percent, co2_saved_total_kg, co2_intensity_kg_per_kwh,
         energy_efficiency_percent, cost_savings_eur)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            metrics['project_id'], metrics['period_start'], metrics['period_end'],
            metrics['period_type'], metrics['total_energy_kwh'],
            metrics['renewable_share_percent'], metrics['co2_saved_total_kg'],
            metrics['co2_intensity_kg_per_kwh'], metrics['energy_efficiency_percent'],
            metrics['cost_savings_eur']
        ))
        
        conn.commit()
        conn.close()
        
        return metrics
    
    def _get_empty_metrics(self, project_id: int, period_start: str, 
                          period_end: str, period_type: str) -> Dict:
        """Gibt leere Metriken zurück wenn keine Daten vorhanden"""
        return {
            'project_id': project_id,
            'period_start': period_start,
            'period_end': period_end,
            'period_type': period_type,
            'total_energy_kwh': 0,
            'renewable_share_percent': 0,
            'co2_saved_total_kg': 0,
            'co2_intensity_kg_per_kwh': 0,
            'energy_efficiency_percent': 0,
            'cost_savings_eur': 0
        }
    
    def generate_esg_report(self, project_id: int, report_type: str = 'monthly') -> Dict:
        """Generiert ESG-Report für ein Projekt"""
        
        # Zeitraum basierend auf Report-Typ bestimmen
        end_date = datetime.now().date()
        if report_type == 'monthly':
            start_date = end_date.replace(day=1)
        elif report_type == 'quarterly':
            quarter = (end_date.month - 1) // 3 + 1
            start_date = end_date.replace(month=(quarter - 1) * 3 + 1, day=1)
        elif report_type == 'yearly':
            start_date = end_date.replace(month=1, day=1)
        else:
            start_date = end_date - timedelta(days=30)
        
        # Nachhaltigkeits-Metriken generieren
        metrics = self.generate_sustainability_metrics(
            project_id, start_date.strftime('%Y-%m-%d'), 
            end_date.strftime('%Y-%m-%d'), report_type
        )
        
        # ESG-Scores berechnen (0-100 Skala)
        environmental_score = min(100, max(0, 
            (metrics['renewable_share_percent'] * 0.4) + 
            (min(100, metrics['co2_saved_total_kg'] / 1000) * 0.6)
        ))
        
        social_score = min(100, max(0, 
            (metrics['energy_efficiency_percent'] * 0.5) + 
            (min(100, metrics['cost_savings_eur'] / 1000) * 0.5)
        ))
        
        governance_score = 85  # Standard-Score für Governance
        
        overall_esg_score = (environmental_score * 0.4) + (social_score * 0.3) + (governance_score * 0.3)
        
        esg_report = {
            'project_id': project_id,
            'report_type': report_type,
            'report_period_start': start_date.strftime('%Y-%m-%d'),
            'report_period_end': end_date.strftime('%Y-%m-%d'),
            'environmental_score': round(environmental_score, 1),
            'social_score': round(social_score, 1),
            'governance_score': round(governance_score, 1),
            'overall_esg_score': round(overall_esg_score, 1),
            'co2_reduction_kg': metrics['co2_saved_total_kg'],
            'renewable_energy_share_percent': metrics['renewable_share_percent'],
            'energy_efficiency_improvement_percent': metrics['energy_efficiency_percent'],
            'report_data': json.dumps(metrics)
        }
        
        # ESG-Report speichern
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT OR REPLACE INTO esg_reports 
        (project_id, report_type, report_period_start, report_period_end,
         environmental_score, social_score, governance_score, overall_esg_score,
         co2_reduction_kg, renewable_energy_share_percent, 
         energy_efficiency_improvement_percent, report_data)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            esg_report['project_id'], esg_report['report_type'],
            esg_report['report_period_start'], esg_report['report_period_end'],
            esg_report['environmental_score'], esg_report['social_score'],
            esg_report['governance_score'], esg_report['overall_esg_score'],
            esg_report['co2_reduction_kg'], esg_report['renewable_energy_share_percent'],
            esg_report['energy_efficiency_improvement_percent'], esg_report['report_data']
        ))
        
        conn.commit()
        conn.close()
        
        return esg_report

def main():
    """Hauptfunktion für CO₂-Tracking System"""
    print("🌱 CO₂-Tracking System für BESS-Simulation")
    print("=" * 50)
    
    # CO₂-Tracking System initialisieren
    co2_system = CO2TrackingSystem()
    
    # Tabellen erstellen
    co2_system.create_co2_tables()
    
    print("✅ CO₂-Tracking System erfolgreich initialisiert")
    print("📊 Tabellen erstellt:")
    print("   - co2_balance")
    print("   - co2_factors") 
    print("   - sustainability_metrics")
    print("   - esg_reports")
    print("🔍 Indizes erstellt für optimale Performance")

if __name__ == '__main__':
    main()
