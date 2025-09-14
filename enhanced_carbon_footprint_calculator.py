#!/usr/bin/env python3
"""
Enhanced Carbon Footprint Calculator für BESS-Simulation
Erweiterte CO₂-Bilanzierung mit detaillierter Analyse und Empfehlungen
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional, Tuple
import math
from dataclasses import dataclass
from enum import Enum

class CarbonFootprintScope(Enum):
    """CO₂-Fußabdruck Scopes nach GHG Protocol"""
    SCOPE_1 = "scope_1"      # Direkte Emissionen
    SCOPE_2 = "scope_2"      # Indirekte Emissionen (Strom)
    SCOPE_3 = "scope_3"      # Andere indirekte Emissionen

@dataclass
class CarbonFootprintData:
    """CO₂-Fußabdruck Datenstruktur"""
    project_id: int
    calculation_date: datetime
    scope_1_emissions_kg_co2: float
    scope_2_emissions_kg_co2: float
    scope_3_emissions_kg_co2: float
    total_emissions_kg_co2: float
    co2_savings_kg_co2: float
    net_carbon_footprint_kg_co2: float
    carbon_intensity_kg_co2_per_kwh: float
    renewable_energy_share_percent: float
    carbon_neutrality_percent: float

class EnhancedCarbonFootprintCalculator:
    """Erweiterter CO₂-Fußabdruck Rechner"""
    
    def __init__(self, db_path: str = "instance/bess.db"):
        self.db_path = db_path
        
        # CO₂-Emissionsfaktoren (kg CO₂/kWh)
        self.emission_factors = {
            # Scope 1 - Direkte Emissionen
            'scope_1': {
                'diesel_generator': 0.82,      # Diesel-Generator
                'gas_turbine': 0.49,           # Gas-Turbine
                'biomass': 0.02,               # Biomasse
                'fuel_oil': 0.78               # Heizöl
            },
            
            # Scope 2 - Strombezug
            'scope_2': {
                'grid_mix_at': 0.156,          # Österreichischer Strommix
                'grid_mix_de': 0.485,          # Deutscher Strommix
                'grid_mix_ch': 0.012,          # Schweizer Strommix
                'grid_mix_eu': 0.298           # EU-Strommix
            },
            
            # Scope 3 - Indirekte Emissionen
            'scope_3': {
                'battery_production': 0.100,   # Batterie-Herstellung
                'pv_production': 0.041,        # PV-Herstellung
                'wind_production': 0.011,      # Wind-Herstellung
                'transport': 0.050,            # Transport
                'maintenance': 0.005,          # Wartung
                'disposal': 0.015              # Entsorgung
            }
        }
        
        # Erneuerbare Energien Faktoren
        self.renewable_factors = {
            'solar': 0.041,                    # Photovoltaik
            'wind': 0.011,                     # Windkraft
            'hydro': 0.024,                    # Wasserkraft
            'biomass': 0.020,                  # Biomasse
            'geothermal': 0.045                # Geothermie
        }
        
        # CO₂-Äquivalente für andere Treibhausgase
        self.gwp_factors = {
            'co2': 1.0,                        # CO₂
            'ch4': 25.0,                       # Methan
            'n2o': 298.0,                      # Lachgas
            'sf6': 22800.0,                    # Schwefelhexafluorid
            'hfc': 1430.0                      # Fluorkohlenwasserstoffe
        }
    
    def create_carbon_footprint_tables(self):
        """Erstellt Tabellen für erweiterten CO₂-Fußabdruck"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # CO₂-Fußabdruck Berechnungen Tabelle
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS carbon_footprint_calculations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            calculation_date DATE NOT NULL,
            scope_1_emissions_kg_co2 REAL NOT NULL,
            scope_2_emissions_kg_co2 REAL NOT NULL,
            scope_3_emissions_kg_co2 REAL NOT NULL,
            total_emissions_kg_co2 REAL NOT NULL,
            co2_savings_kg_co2 REAL NOT NULL,
            net_carbon_footprint_kg_co2 REAL NOT NULL,
            carbon_intensity_kg_co2_per_kwh REAL NOT NULL,
            renewable_energy_share_percent REAL NOT NULL,
            carbon_neutrality_percent REAL NOT NULL,
            calculation_method VARCHAR(50) DEFAULT 'enhanced',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES project (id)
        )
        ''')
        
        # CO₂-Fußabdruck Details Tabelle
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS carbon_footprint_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            calculation_id INTEGER NOT NULL,
            scope VARCHAR(20) NOT NULL,
            category VARCHAR(100) NOT NULL,
            energy_source VARCHAR(100) NOT NULL,
            energy_consumption_kwh REAL NOT NULL,
            emission_factor_kg_co2_per_kwh REAL NOT NULL,
            emissions_kg_co2 REAL NOT NULL,
            co2_equivalent_kg REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (calculation_id) REFERENCES carbon_footprint_calculations (id)
        )
        ''')
        
        # CO₂-Fußabdruck Benchmarks Tabelle
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS carbon_footprint_benchmarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_type VARCHAR(100) NOT NULL,
            country VARCHAR(10) NOT NULL,
            year INTEGER NOT NULL,
            average_intensity_kg_co2_per_kwh REAL NOT NULL,
            best_practice_kg_co2_per_kwh REAL NOT NULL,
            worst_practice_kg_co2_per_kwh REAL NOT NULL,
            sample_size INTEGER NOT NULL,
            source VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # CO₂-Reduktionsziele Tabelle
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS carbon_reduction_targets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            target_year INTEGER NOT NULL,
            baseline_year INTEGER NOT NULL,
            baseline_emissions_kg_co2 REAL NOT NULL,
            target_emissions_kg_co2 REAL NOT NULL,
            reduction_percent REAL NOT NULL,
            target_type VARCHAR(50) NOT NULL, -- 'absolute', 'intensity', 'neutrality'
            status VARCHAR(20) DEFAULT 'active', -- 'active', 'achieved', 'missed'
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES project (id)
        )
        ''')
        
        # Indizes erstellen
        indices = [
            "CREATE INDEX IF NOT EXISTS idx_carbon_footprint_project_date ON carbon_footprint_calculations(project_id, calculation_date)",
            "CREATE INDEX IF NOT EXISTS idx_carbon_footprint_details_calc ON carbon_footprint_details(calculation_id, scope)",
            "CREATE INDEX IF NOT EXISTS idx_carbon_benchmarks_type_country ON carbon_footprint_benchmarks(project_type, country, year)",
            "CREATE INDEX IF NOT EXISTS idx_carbon_targets_project ON carbon_reduction_targets(project_id, target_year)"
        ]
        
        for index_sql in indices:
            cursor.execute(index_sql)
        
        # Standard-Benchmarks einfügen
        self._insert_default_benchmarks(cursor)
        
        conn.commit()
        conn.close()
        print("✅ Enhanced Carbon Footprint Calculator Tabellen erfolgreich erstellt")
    
    def _insert_default_benchmarks(self, cursor):
        """Fügt Standard-Benchmarks ein"""
        benchmarks = [
            ('BESS_Project', 'AT', 2024, 0.120, 0.080, 0.200, 150, 'BESS-Simulation Database'),
            ('BESS_Project', 'DE', 2024, 0.180, 0.120, 0.280, 200, 'BESS-Simulation Database'),
            ('BESS_Project', 'CH', 2024, 0.050, 0.030, 0.100, 100, 'BESS-Simulation Database'),
            ('PV_Project', 'AT', 2024, 0.080, 0.050, 0.150, 300, 'BESS-Simulation Database'),
            ('Wind_Project', 'AT', 2024, 0.060, 0.040, 0.120, 250, 'BESS-Simulation Database'),
            ('Hydro_Project', 'AT', 2024, 0.040, 0.020, 0.080, 180, 'BESS-Simulation Database')
        ]
        
        for project_type, country, year, avg_intensity, best_practice, worst_practice, sample_size, source in benchmarks:
            cursor.execute('''
            INSERT OR IGNORE INTO carbon_footprint_benchmarks 
            (project_type, country, year, average_intensity_kg_co2_per_kwh,
             best_practice_kg_co2_per_kwh, worst_practice_kg_co2_per_kwh,
             sample_size, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (project_type, country, year, avg_intensity, best_practice, worst_practice, sample_size, source))
    
    def calculate_enhanced_carbon_footprint(self, project_id: int, 
                                          calculation_date: Optional[datetime] = None) -> CarbonFootprintData:
        """Berechnet erweiterten CO₂-Fußabdruck"""
        
        if calculation_date is None:
            calculation_date = datetime.now().date()
        
        # Projekt-Daten abrufen
        project_data = self._get_project_data(project_id)
        if not project_data:
            raise ValueError(f"Projekt {project_id} nicht gefunden")
        
        # Energieverbrauchsdaten abrufen
        energy_data = self._get_energy_consumption_data(project_id, calculation_date)
        
        # Scope 1 Emissionen berechnen
        scope_1_emissions = self._calculate_scope_1_emissions(project_data, energy_data)
        
        # Scope 2 Emissionen berechnen
        scope_2_emissions = self._calculate_scope_2_emissions(project_data, energy_data)
        
        # Scope 3 Emissionen berechnen
        scope_3_emissions = self._calculate_scope_3_emissions(project_data, energy_data)
        
        # CO₂-Einsparungen berechnen
        co2_savings = self._calculate_co2_savings(project_data, energy_data)
        
        # Gesamtemissionen
        total_emissions = scope_1_emissions['total'] + scope_2_emissions['total'] + scope_3_emissions['total']
        
        # Netto CO₂-Fußabdruck
        net_footprint = total_emissions - co2_savings
        
        # Carbon Intensity
        total_energy = energy_data.get('total_energy_consumption_kwh', 1)
        carbon_intensity = total_emissions / total_energy if total_energy > 0 else 0
        
        # Erneuerbare Energie Anteil
        renewable_share = self._calculate_renewable_energy_share(project_data, energy_data)
        
        # Carbon Neutrality
        carbon_neutrality = max(0, (co2_savings / total_emissions * 100)) if total_emissions > 0 else 100
        
        return CarbonFootprintData(
            project_id=project_id,
            calculation_date=calculation_date,
            scope_1_emissions_kg_co2=scope_1_emissions['total'],
            scope_2_emissions_kg_co2=scope_2_emissions['total'],
            scope_3_emissions_kg_co2=scope_3_emissions['total'],
            total_emissions_kg_co2=total_emissions,
            co2_savings_kg_co2=co2_savings,
            net_carbon_footprint_kg_co2=net_footprint,
            carbon_intensity_kg_co2_per_kwh=carbon_intensity,
            renewable_energy_share_percent=renewable_share,
            carbon_neutrality_percent=carbon_neutrality
        )
    
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
    
    def _get_energy_consumption_data(self, project_id: int, calculation_date: datetime) -> Dict:
        """Ruft Energieverbrauchsdaten ab"""
        conn = sqlite3.connect(self.db_path)
        
        # Letztes Jahr Daten
        start_date = calculation_date - timedelta(days=365)
        
        # CO₂-Balance Daten
        query = '''
        SELECT 
            SUM(energy_stored_kwh) as total_energy_stored,
            SUM(energy_discharged_kwh) as total_energy_discharged,
            SUM(grid_energy_kwh) as total_grid_energy,
            SUM(renewable_energy_kwh) as total_renewable_energy
        FROM co2_balance 
        WHERE project_id = ? AND date BETWEEN ? AND ?
        '''
        
        df = pd.read_sql_query(query, conn, params=(
            project_id, start_date.strftime('%Y-%m-%d'), calculation_date.strftime('%Y-%m-%d')
        ))
        
        conn.close()
        
        if not df.empty and df.iloc[0]['total_energy_stored'] is not None:
            return {
                'total_energy_stored_kwh': df.iloc[0]['total_energy_stored'],
                'total_energy_discharged_kwh': df.iloc[0]['total_energy_discharged'],
                'total_grid_energy_kwh': df.iloc[0]['total_grid_energy'],
                'total_renewable_energy_kwh': df.iloc[0]['total_renewable_energy'],
                'total_energy_consumption_kwh': df.iloc[0]['total_energy_stored'] + df.iloc[0]['total_energy_discharged']
            }
        
        # Fallback: Geschätzte Werte basierend auf Projekt-Daten
        project_data = self._get_project_data(project_id)
        estimated_annual_generation = (
            (project_data['pv_power'] or 0) * 1000 +      # PV: 1000 kWh/kW/a
            (project_data['wind_power'] or 0) * 2000 +    # Wind: 2000 kWh/kW/a
            (project_data['hydro_power'] or 0) * 3000     # Hydro: 3000 kWh/kW/a
        )
        
        return {
            'total_energy_stored_kwh': estimated_annual_generation * 0.5,
            'total_energy_discharged_kwh': estimated_annual_generation * 0.45,
            'total_grid_energy_kwh': estimated_annual_generation * 0.2,
            'total_renewable_energy_kwh': estimated_annual_generation * 0.8,
            'total_energy_consumption_kwh': estimated_annual_generation
        }
    
    def _calculate_scope_1_emissions(self, project_data: Dict, energy_data: Dict) -> Dict:
        """Berechnet Scope 1 Emissionen (direkte Emissionen)"""
        
        scope_1_emissions = {
            'total': 0,
            'breakdown': {}
        }
        
        # BESS-System (direkte Emissionen minimal)
        if project_data['bess_size'] > 0:
            # Annahme: 1% direkte Emissionen durch Betrieb
            bess_emissions = energy_data['total_energy_consumption_kwh'] * 0.01 * self.emission_factors['scope_1']['diesel_generator']
            scope_1_emissions['breakdown']['bess_operation'] = bess_emissions
            scope_1_emissions['total'] += bess_emissions
        
        # Backup-Generator (falls vorhanden)
        # Annahme: 5% der Zeit Backup-Generator
        if project_data.get('backup_generator_kw', 0) > 0:
            backup_energy = energy_data['total_energy_consumption_kwh'] * 0.05
            backup_emissions = backup_energy * self.emission_factors['scope_1']['diesel_generator']
            scope_1_emissions['breakdown']['backup_generator'] = backup_emissions
            scope_1_emissions['total'] += backup_emissions
        
        return scope_1_emissions
    
    def _calculate_scope_2_emissions(self, project_data: Dict, energy_data: Dict) -> Dict:
        """Berechnet Scope 2 Emissionen (Strombezug)"""
        
        scope_2_emissions = {
            'total': 0,
            'breakdown': {}
        }
        
        # Strombezug aus dem Netz
        grid_energy = energy_data.get('total_grid_energy_kwh', 0)
        
        # Länder-spezifischer Emissionsfaktor
        country = project_data.get('location', 'AT')
        if 'DE' in country:
            emission_factor = self.emission_factors['scope_2']['grid_mix_de']
        elif 'CH' in country:
            emission_factor = self.emission_factors['scope_2']['grid_mix_ch']
        else:
            emission_factor = self.emission_factors['scope_2']['grid_mix_at']  # Standard: Österreich
        
        grid_emissions = grid_energy * emission_factor
        scope_2_emissions['breakdown']['grid_electricity'] = grid_emissions
        scope_2_emissions['total'] += grid_emissions
        
        return scope_2_emissions
    
    def _calculate_scope_3_emissions(self, project_data: Dict, energy_data: Dict) -> Dict:
        """Berechnet Scope 3 Emissionen (indirekte Emissionen)"""
        
        scope_3_emissions = {
            'total': 0,
            'breakdown': {}
        }
        
        # Batterie-Herstellung
        if project_data['bess_size'] > 0:
            battery_emissions = project_data['bess_size'] * self.emission_factors['scope_3']['battery_production']
            scope_3_emissions['breakdown']['battery_production'] = battery_emissions
            scope_3_emissions['total'] += battery_emissions
        
        # PV-Herstellung
        if project_data['pv_power'] > 0:
            pv_emissions = project_data['pv_power'] * 1000 * self.emission_factors['scope_3']['pv_production']
            scope_3_emissions['breakdown']['pv_production'] = pv_emissions
            scope_3_emissions['total'] += pv_emissions
        
        # Wind-Herstellung
        if project_data['wind_power'] > 0:
            wind_emissions = project_data['wind_power'] * 1000 * self.emission_factors['scope_3']['wind_production']
            scope_3_emissions['breakdown']['wind_production'] = wind_emissions
            scope_3_emissions['total'] += wind_emissions
        
        # Transport
        total_equipment_weight = (project_data['bess_size'] * 10 +  # 10 kg/kWh
                                project_data['pv_power'] * 20 +    # 20 kg/kW
                                project_data['wind_power'] * 100)  # 100 kg/kW
        
        transport_emissions = total_equipment_weight * self.emission_factors['scope_3']['transport']
        scope_3_emissions['breakdown']['transport'] = transport_emissions
        scope_3_emissions['total'] += transport_emissions
        
        # Wartung
        maintenance_emissions = energy_data['total_energy_consumption_kwh'] * self.emission_factors['scope_3']['maintenance']
        scope_3_emissions['breakdown']['maintenance'] = maintenance_emissions
        scope_3_emissions['total'] += maintenance_emissions
        
        return scope_3_emissions
    
    def _calculate_co2_savings(self, project_data: Dict, energy_data: Dict) -> float:
        """Berechnet CO₂-Einsparungen durch erneuerbare Energien"""
        
        total_savings = 0
        
        # Erneuerbare Energie Einsparungen
        renewable_energy = energy_data.get('total_renewable_energy_kwh', 0)
        
        # Länder-spezifischer Strommix als Referenz
        country = project_data.get('location', 'AT')
        if 'DE' in country:
            grid_emission_factor = self.emission_factors['scope_2']['grid_mix_de']
        elif 'CH' in country:
            grid_emission_factor = self.emission_factors['scope_2']['grid_mix_ch']
        else:
            grid_emission_factor = self.emission_factors['scope_2']['grid_mix_at']
        
        # PV-Einsparungen
        if project_data['pv_power'] > 0:
            pv_energy = project_data['pv_power'] * 1000  # 1000 kWh/kW/a
            pv_savings = pv_energy * (grid_emission_factor - self.renewable_factors['solar'])
            total_savings += pv_savings
        
        # Wind-Einsparungen
        if project_data['wind_power'] > 0:
            wind_energy = project_data['wind_power'] * 2000  # 2000 kWh/kW/a
            wind_savings = wind_energy * (grid_emission_factor - self.renewable_factors['wind'])
            total_savings += wind_savings
        
        # Hydro-Einsparungen
        if project_data['hydro_power'] > 0:
            hydro_energy = project_data['hydro_power'] * 3000  # 3000 kWh/kW/a
            hydro_savings = hydro_energy * (grid_emission_factor - self.renewable_factors['hydro'])
            total_savings += hydro_savings
        
        return max(0, total_savings)
    
    def _calculate_renewable_energy_share(self, project_data: Dict, energy_data: Dict) -> float:
        """Berechnet Anteil erneuerbarer Energien"""
        
        total_renewable = (
            (project_data['pv_power'] or 0) * 1000 +
            (project_data['wind_power'] or 0) * 2000 +
            (project_data['hydro_power'] or 0) * 3000
        )
        
        total_energy = energy_data.get('total_energy_consumption_kwh', 1)
        
        return (total_renewable / total_energy * 100) if total_energy > 0 else 0
    
    def save_carbon_footprint_calculation(self, footprint_data: CarbonFootprintData) -> int:
        """Speichert CO₂-Fußabdruck Berechnung in der Datenbank"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Hauptberechnung speichern
            cursor.execute('''
            INSERT INTO carbon_footprint_calculations 
            (project_id, calculation_date, scope_1_emissions_kg_co2, scope_2_emissions_kg_co2,
             scope_3_emissions_kg_co2, total_emissions_kg_co2, co2_savings_kg_co2,
             net_carbon_footprint_kg_co2, carbon_intensity_kg_co2_per_kwh,
             renewable_energy_share_percent, carbon_neutrality_percent)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                footprint_data.project_id,
                footprint_data.calculation_date,
                footprint_data.scope_1_emissions_kg_co2,
                footprint_data.scope_2_emissions_kg_co2,
                footprint_data.scope_3_emissions_kg_co2,
                footprint_data.total_emissions_kg_co2,
                footprint_data.co2_savings_kg_co2,
                footprint_data.net_carbon_footprint_kg_co2,
                footprint_data.carbon_intensity_kg_co2_per_kwh,
                footprint_data.renewable_energy_share_percent,
                footprint_data.carbon_neutrality_percent
            ))
            
            calculation_id = cursor.lastrowid
            conn.commit()
            
            return calculation_id
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_carbon_footprint_trend(self, project_id: int, months: int = 12) -> List[Dict]:
        """Ruft CO₂-Fußabdruck Trend ab"""
        conn = sqlite3.connect(self.db_path)
        
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=months * 30)
        
        query = '''
        SELECT calculation_date, total_emissions_kg_co2, co2_savings_kg_co2,
               net_carbon_footprint_kg_co2, carbon_intensity_kg_co2_per_kwh,
               renewable_energy_share_percent, carbon_neutrality_percent
        FROM carbon_footprint_calculations 
        WHERE project_id = ? AND calculation_date BETWEEN ? AND ?
        ORDER BY calculation_date
        '''
        
        df = pd.read_sql_query(query, conn, params=(
            project_id, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
        ))
        conn.close()
        
        return df.to_dict('records')
    
    def compare_with_benchmarks(self, footprint_data: CarbonFootprintData, 
                               project_type: str = 'BESS_Project') -> Dict:
        """Vergleicht CO₂-Fußabdruck mit Benchmarks"""
        
        conn = sqlite3.connect(self.db_path)
        
        # Länder bestimmen
        project_data = self._get_project_data(footprint_data.project_id)
        country = project_data.get('location', 'AT')
        
        # Benchmarks abrufen
        query = '''
        SELECT average_intensity_kg_co2_per_kwh, best_practice_kg_co2_per_kwh,
               worst_practice_kg_co2_per_kwh, sample_size
        FROM carbon_footprint_benchmarks 
        WHERE project_type = ? AND country = ? AND year = ?
        ORDER BY year DESC
        LIMIT 1
        '''
        
        df = pd.read_sql_query(query, conn, params=(
            project_type, country, datetime.now().year
        ))
        conn.close()
        
        if df.empty:
            # Fallback zu allgemeinen Benchmarks
            benchmarks = {
                'average_intensity_kg_co2_per_kwh': 0.120,
                'best_practice_kg_co2_per_kwh': 0.080,
                'worst_practice_kg_co2_per_kwh': 0.200,
                'sample_size': 100
            }
        else:
            benchmarks = df.iloc[0].to_dict()
        
        # Vergleich
        current_intensity = footprint_data.carbon_intensity_kg_co2_per_kwh
        average_intensity = benchmarks['average_intensity_kg_co2_per_kwh']
        best_practice = benchmarks['best_practice_kg_co2_per_kwh']
        
        # Performance Rating
        if current_intensity <= best_practice:
            performance_rating = 'excellent'
        elif current_intensity <= average_intensity:
            performance_rating = 'good'
        elif current_intensity <= benchmarks['worst_practice_kg_co2_per_kwh']:
            performance_rating = 'average'
        else:
            performance_rating = 'poor'
        
        # Verbesserungspotential
        improvement_potential = max(0, current_intensity - best_practice)
        improvement_percent = (improvement_potential / current_intensity * 100) if current_intensity > 0 else 0
        
        return {
            'current_intensity_kg_co2_per_kwh': current_intensity,
            'benchmarks': benchmarks,
            'performance_rating': performance_rating,
            'improvement_potential_kg_co2_per_kwh': improvement_potential,
            'improvement_percent': improvement_percent,
            'ranking_percentile': self._calculate_percentile_ranking(current_intensity, benchmarks)
        }
    
    def _calculate_percentile_ranking(self, current_intensity: float, benchmarks: Dict) -> float:
        """Berechnet Percentile Ranking"""
        
        best = benchmarks['best_practice_kg_co2_per_kwh']
        worst = benchmarks['worst_practice_kg_co2_per_kwh']
        
        if current_intensity <= best:
            return 95.0  # Top 5%
        elif current_intensity >= worst:
            return 5.0   # Bottom 5%
        else:
            # Lineare Interpolation
            percentile = 95 - ((current_intensity - best) / (worst - best) * 90)
            return max(5.0, min(95.0, percentile))
    
    def generate_carbon_reduction_recommendations(self, footprint_data: CarbonFootprintData) -> List[Dict]:
        """Generiert CO₂-Reduktionsempfehlungen"""
        
        recommendations = []
        
        # Scope 1 Empfehlungen
        if footprint_data.scope_1_emissions_kg_co2 > 0:
            recommendations.append({
                'scope': 'Scope 1',
                'priority': 'high',
                'title': 'Direkte Emissionen reduzieren',
                'description': f'Scope 1 Emissionen: {footprint_data.scope_1_emissions_kg_co2:.1f} kg CO₂',
                'actions': [
                    'Backup-Generator durch erneuerbare Energien ersetzen',
                    'BESS-Effizienz optimieren',
                    'Regenerative Energien ausbauen'
                ],
                'potential_reduction_kg_co2': footprint_data.scope_1_emissions_kg_co2 * 0.8
            })
        
        # Scope 2 Empfehlungen
        if footprint_data.scope_2_emissions_kg_co2 > 0:
            recommendations.append({
                'scope': 'Scope 2',
                'priority': 'high',
                'title': 'Strombezug optimieren',
                'description': f'Scope 2 Emissionen: {footprint_data.scope_2_emissions_kg_co2:.1f} kg CO₂',
                'actions': [
                    'Grünen Strom beziehen',
                    'Eigenverbrauch erhöhen',
                    'Lastmanagement optimieren'
                ],
                'potential_reduction_kg_co2': footprint_data.scope_2_emissions_kg_co2 * 0.6
            })
        
        # Scope 3 Empfehlungen
        if footprint_data.scope_3_emissions_kg_co2 > 0:
            recommendations.append({
                'scope': 'Scope 3',
                'priority': 'medium',
                'title': 'Indirekte Emissionen reduzieren',
                'description': f'Scope 3 Emissionen: {footprint_data.scope_3_emissions_kg_co2:.1f} kg CO₂',
                'actions': [
                    'Nachhaltige Lieferketten wählen',
                    'Wartungszyklen optimieren',
                    'Recycling-Programme implementieren'
                ],
                'potential_reduction_kg_co2': footprint_data.scope_3_emissions_kg_co2 * 0.3
            })
        
        # Erneuerbare Energien Empfehlungen
        if footprint_data.renewable_energy_share_percent < 80:
            recommendations.append({
                'scope': 'Renewable Energy',
                'priority': 'high',
                'title': 'Erneuerbare Energien ausbauen',
                'description': f'Aktueller Anteil: {footprint_data.renewable_energy_share_percent:.1f}%',
                'actions': [
                    'PV-Anlage erweitern',
                    'Windkraft hinzufügen',
                    'Wasserkraft nutzen'
                ],
                'potential_reduction_kg_co2': footprint_data.total_emissions_kg_co2 * 0.4
            })
        
        # Carbon Neutrality Empfehlungen
        if footprint_data.carbon_neutrality_percent < 100:
            recommendations.append({
                'scope': 'Carbon Neutrality',
                'priority': 'medium',
                'title': 'Carbon Neutrality erreichen',
                'description': f'Aktueller Status: {footprint_data.carbon_neutrality_percent:.1f}%',
                'actions': [
                    'Carbon Credits kaufen',
                    'Aufforstungsprojekte unterstützen',
                    'Energieeffizienz steigern'
                ],
                'potential_reduction_kg_co2': footprint_data.net_carbon_footprint_kg_co2
            })
        
        return recommendations

def main():
    """Hauptfunktion für Enhanced Carbon Footprint Calculator"""
    print("🌱 Enhanced Carbon Footprint Calculator für BESS-Simulation")
    print("=" * 70)
    
    # System initialisieren
    calculator = EnhancedCarbonFootprintCalculator()
    
    # Tabellen erstellen
    calculator.create_carbon_footprint_tables()
    
    print("✅ Enhanced Carbon Footprint Calculator erfolgreich initialisiert")
    print("📊 Features:")
    print("   - Scope 1, 2, 3 Emissionen Berechnung")
    print("   - CO₂-Fußabdruck Tracking")
    print("   - Benchmark-Vergleiche")
    print("   - Reduktionsempfehlungen")
    print("   - Carbon Neutrality Tracking")
    print("   - Trend-Analysen")
    print("🌍 Emissionsfaktoren:")
    print("   - Österreich: 0.156 kg CO₂/kWh")
    print("   - Deutschland: 0.485 kg CO₂/kWh")
    print("   - Schweiz: 0.012 kg CO₂/kWh")

if __name__ == '__main__':
    main()
