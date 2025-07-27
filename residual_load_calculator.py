#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Residuallast-Berechnung und Load-Shifting Optimierung
für BESS-Simulation
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class LoadProfile:
    """Lastprofil-Datenstruktur"""
    timestamp: datetime
    consumption_kw: float
    pv_generation_kw: float = 0.0
    hydro_generation_kw: float = 0.0
    residual_load_kw: float = 0.0

@dataclass
class BatteryState:
    """Batterie-Zustand"""
    soc_percent: float  # State of Charge in %
    capacity_kwh: float
    max_power_kw: float
    min_soc_percent: float = 10.0
    max_soc_percent: float = 90.0

@dataclass
class OptimizationResult:
    """Optimierungsergebnis"""
    timestamp: datetime
    charge_power_kw: float
    discharge_power_kw: float
    battery_soc_percent: float
    spot_price_eur_mwh: float
    cost_eur: float
    revenue_eur: float
    net_benefit_eur: float

class ResidualLoadCalculator:
    """Berechnet die Residuallast für verschiedene Use Cases"""
    
    def __init__(self, use_case_type: str):
        self.use_case_type = use_case_type
        
    def calculate_residual_load(self, 
                              consumption_data: pd.DataFrame,
                              pv_data: Optional[pd.DataFrame] = None,
                              hydro_data: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Berechnet die Residuallast basierend auf dem Use Case
        
        Args:
            consumption_data: DataFrame mit 'timestamp' und 'power_kw' Spalten
            pv_data: Optional PV-Generationsdaten
            hydro_data: Optional Wasserkraft-Daten
            
        Returns:
            DataFrame mit Residuallast
        """
        # Basis-Verbrauchsdaten kopieren
        result = consumption_data.copy()
        result['residual_load_kw'] = result['power_kw']
        
        # UC1: Nur Verbrauch
        if self.use_case_type == 'consumption_only':
            return result
            
        # UC2: Verbrauch + PV
        if self.use_case_type in ['pv_consumption', 'pv_hydro_consumption']:
            if pv_data is not None:
                # PV-Daten mit Verbrauchsdaten zusammenführen
                merged = pd.merge(result, pv_data, on='timestamp', how='left', suffixes=('', '_pv'))
                merged['pv_generation_kw'] = merged['power_kw_pv'].fillna(0)
                merged['residual_load_kw'] = merged['power_kw'] - merged['pv_generation_kw']
                result = merged[['timestamp', 'power_kw', 'pv_generation_kw', 'residual_load_kw']]
        
        # UC3: Verbrauch + PV + Wasserkraft
        if self.use_case_type == 'pv_hydro_consumption':
            if hydro_data is not None:
                # Wasserkraft-Daten hinzufügen
                merged = pd.merge(result, hydro_data, on='timestamp', how='left', suffixes=('', '_hydro'))
                merged['hydro_generation_kw'] = merged['power_kw_hydro'].fillna(0)
                merged['residual_load_kw'] = merged['residual_load_kw'] - merged['hydro_generation_kw']
                result = merged[['timestamp', 'power_kw', 'pv_generation_kw', 'hydro_generation_kw', 'residual_load_kw']]
        
        return result

class LoadShiftingOptimizer:
    """Optimiert Load-Shifting basierend auf Spotpreisen"""
    
    def __init__(self, battery: BatteryState, efficiency: float = 0.85):
        self.battery = battery
        self.efficiency = efficiency
        
    def optimize_charging_schedule(self, 
                                 residual_load_data: pd.DataFrame,
                                 spot_prices: pd.DataFrame,
                                 optimization_target: str = 'cost_minimization') -> List[OptimizationResult]:
        """
        Optimiert den Lade-/Entladeplan basierend auf Spotpreisen
        
        Args:
            residual_load_data: DataFrame mit Residuallast
            spot_prices: DataFrame mit 'timestamp' und 'price_eur_mwh'
            optimization_target: 'cost_minimization' oder 'revenue_maximization'
            
        Returns:
            Liste von OptimizationResult Objekten
        """
        # Daten zusammenführen
        merged_data = pd.merge(residual_load_data, spot_prices, on='timestamp', how='left')
        merged_data['spot_price_eur_mwh'] = merged_data['price_eur_mwh'].fillna(50.0)  # Default-Preis
        
        results = []
        current_soc = self.battery.soc_percent
        
        for _, row in merged_data.iterrows():
            timestamp = row['timestamp']
            residual_load = row['residual_load_kw']
            spot_price = row['spot_price_eur_mwh']
            
            # Batterie-Entscheidungslogik
            charge_power = 0.0
            discharge_power = 0.0
            
            # Einfache Optimierungsstrategie: Bei niedrigen Preisen laden, bei hohen Preisen entladen
            if optimization_target == 'cost_minimization':
                if spot_price < 40.0 and current_soc < self.battery.max_soc_percent:  # Niedriger Preis -> Laden
                    charge_power = min(self.battery.max_power_kw, 
                                     (self.battery.max_soc_percent - current_soc) * self.battery.capacity_kwh / 100)
                elif spot_price > 80.0 and current_soc > self.battery.min_soc_percent:  # Hoher Preis -> Entladen
                    discharge_power = min(self.battery.max_power_kw, 
                                        (current_soc - self.battery.min_soc_percent) * self.battery.capacity_kwh / 100)
            
            # SOC-Update
            if charge_power > 0:
                energy_change = charge_power * 0.25 / 1000  # 15-Minuten-Intervall in kWh
                current_soc += (energy_change * self.efficiency) / self.battery.capacity_kwh * 100
            elif discharge_power > 0:
                energy_change = discharge_power * 0.25 / 1000
                current_soc -= energy_change / self.efficiency / self.battery.capacity_kwh * 100
            
            # SOC-Grenzen einhalten
            current_soc = max(self.battery.min_soc_percent, min(self.battery.max_soc_percent, current_soc))
            
            # Kosten und Erlöse berechnen
            cost_eur = charge_power * 0.25 * spot_price / 1000  # 15-Min-Intervall
            revenue_eur = discharge_power * 0.25 * spot_price / 1000
            net_benefit = revenue_eur - cost_eur
            
            result = OptimizationResult(
                timestamp=timestamp,
                charge_power_kw=charge_power,
                discharge_power_kw=discharge_power,
                battery_soc_percent=current_soc,
                spot_price_eur_mwh=spot_price,
                cost_eur=cost_eur,
                revenue_eur=revenue_eur,
                net_benefit_eur=net_benefit
            )
            results.append(result)
        
        return results

class RevenueCalculator:
    """Berechnet Erlöse aus verschiedenen Quellen"""
    
    def __init__(self):
        self.revenue_sources = {
            'arbitrage': {'price': 0.0, 'availability': 8760, 'efficiency': 0.85},
            'srl_positive': {'price': 45.0, 'availability': 8760, 'efficiency': 0.95},
            'srl_negative': {'price': 35.0, 'availability': 8760, 'efficiency': 0.95},
            'day_ahead': {'price': 0.0, 'availability': 8760, 'efficiency': 0.90},
            'intraday': {'price': 0.0, 'availability': 8760, 'efficiency': 0.88}
        }
    
    def calculate_arbitrage_revenue(self, optimization_results: List[OptimizationResult]) -> float:
        """Berechnet Arbitrage-Erlöse"""
        total_revenue = 0.0
        for result in optimization_results:
            if result.discharge_power_kw > 0:
                # Erlös = Entladeleistung * Spotpreis * Wirkungsgrad
                revenue = (result.discharge_power_kw * 0.25 * result.spot_price_eur_mwh / 1000 * 
                          self.revenue_sources['arbitrage']['efficiency'])
                total_revenue += revenue
        return total_revenue
    
    def calculate_srl_revenue(self, battery_power_kw: float, srl_type: str = 'positive') -> float:
        """Berechnet SRL-Erlöse"""
        if srl_type == 'positive':
            source = self.revenue_sources['srl_positive']
        else:
            source = self.revenue_sources['srl_negative']
        
        # Annahme: 5% der Zeit wird SRL aktiviert
        activation_hours = source['availability'] * 0.05
        revenue = (battery_power_kw / 1000 * activation_hours * source['price'] * 
                  source['efficiency'])
        return revenue
    
    def calculate_total_revenue(self, optimization_results: List[OptimizationResult], 
                              battery_power_kw: float) -> Dict[str, float]:
        """Berechnet Gesamterlöse aus allen Quellen"""
        revenues = {
            'arbitrage': self.calculate_arbitrage_revenue(optimization_results),
            'srl_positive': self.calculate_srl_revenue(battery_power_kw, 'positive'),
            'srl_negative': self.calculate_srl_revenue(battery_power_kw, 'negative'),
            'day_ahead': 0.0,  # Wird dynamisch berechnet
            'intraday': 0.0     # Wird dynamisch berechnet
        }
        
        revenues['total'] = sum(revenues.values())
        return revenues

class CostCalculator:
    """Berechnet Kosten aus Netzentgelten und Abgaben"""
    
    def __init__(self):
        self.grid_tariffs = {
            'consumption': {'base_price': 25.0, 'spot_multiplier': 1.2},
            'feed_in': {'base_price': 15.0, 'spot_multiplier': 0.8}
        }
        
        self.legal_charges = {
            'electricity_tax': 1.0,  # 2024
            'network_loss': 8.5,
            'clearing_fee': 0.15
        }
    
    def calculate_grid_costs(self, energy_consumed_mwh: float, 
                           energy_fed_in_mwh: float,
                           avg_spot_price: float) -> Dict[str, float]:
        """Berechnet Netzentgelte"""
        consumption_tariff = (self.grid_tariffs['consumption']['base_price'] + 
                             avg_spot_price * self.grid_tariffs['consumption']['spot_multiplier'])
        feed_in_tariff = (self.grid_tariffs['feed_in']['base_price'] + 
                         avg_spot_price * self.grid_tariffs['feed_in']['spot_multiplier'])
        
        costs = {
            'consumption_cost': energy_consumed_mwh * consumption_tariff,
            'feed_in_revenue': energy_fed_in_mwh * feed_in_tariff,
            'electricity_tax': energy_consumed_mwh * self.legal_charges['electricity_tax'],
            'network_loss': energy_consumed_mwh * self.legal_charges['network_loss'],
            'clearing_fee': energy_consumed_mwh * self.legal_charges['clearing_fee']
        }
        
        costs['total_cost'] = (costs['consumption_cost'] + costs['electricity_tax'] + 
                              costs['network_loss'] + costs['clearing_fee'] - costs['feed_in_revenue'])
        
        return costs

def create_sample_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Erstellt Beispieldaten für Tests"""
    # Zeitreihe für ein Jahr (15-Minuten-Intervalle)
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31, 23, 45)
    timestamps = pd.date_range(start=start_date, end=end_date, freq='15T')
    
    # Verbrauchsdaten (typisches Lastprofil)
    np.random.seed(42)
    base_load = 500  # kW
    seasonal_variation = 100 * np.sin(2 * np.pi * np.arange(len(timestamps)) / (365 * 96))  # Jahresverlauf
    daily_variation = 50 * np.sin(2 * np.pi * np.arange(len(timestamps)) / 96)  # Tagesverlauf
    noise = np.random.normal(0, 20, len(timestamps))
    
    consumption_data = pd.DataFrame({
        'timestamp': timestamps,
        'power_kw': base_load + seasonal_variation + daily_variation + noise
    })
    
    # PV-Generationsdaten
    solar_noon = 12  # Uhrzeit der maximalen Sonneneinstrahlung
    max_pv_power = 1950  # kW (1,95 MWp)
    
    pv_generation = []
    for ts in timestamps:
        hour = ts.hour + ts.minute / 60
        day_of_year = ts.timetuple().tm_yday
        
        # Jahresverlauf (Sommer/Winter)
        seasonal_factor = 0.3 + 0.7 * np.sin(np.pi * (day_of_year - 172) / 365)
        
        # Tagesverlauf (Sinus-Kurve)
        if 6 <= hour <= 18:
            daily_factor = np.sin(np.pi * (hour - 6) / 12)
        else:
            daily_factor = 0
        
        pv_power = max_pv_power * seasonal_factor * daily_factor
        pv_generation.append(max(0, pv_power))
    
    pv_data = pd.DataFrame({
        'timestamp': timestamps,
        'power_kw': pv_generation
    })
    
    # Wasserkraft-Daten (konstanter Wert für UC3)
    hydro_data = pd.DataFrame({
        'timestamp': timestamps,
        'power_kw': [650.0] * len(timestamps)  # 650 kW konstant
    })
    
    return consumption_data, pv_data, hydro_data

def main():
    """Test-Funktion"""
    print("=== BESS-Simulation: Residuallast-Berechnung Test ===")
    
    # Beispieldaten erstellen
    consumption_data, pv_data, hydro_data = create_sample_data()
    
    # UC3: Verbrauch + PV + Wasserkraft
    calculator = ResidualLoadCalculator('pv_hydro_consumption')
    residual_load = calculator.calculate_residual_load(consumption_data, pv_data, hydro_data)
    
    print(f"Verbrauchsdaten: {len(consumption_data)} Einträge")
    print(f"PV-Daten: {len(pv_data)} Einträge")
    print(f"Residuallast: {len(residual_load)} Einträge")
    
    # Statistiken
    print(f"\nStatistiken:")
    print(f"Verbrauch: {consumption_data['power_kw'].mean():.1f} kW (Ø)")
    print(f"PV-Generation: {pv_data['power_kw'].mean():.1f} kW (Ø)")
    print(f"Wasserkraft: {hydro_data['power_kw'].mean():.1f} kW (Ø)")
    print(f"Residuallast: {residual_load['residual_load_kw'].mean():.1f} kW (Ø)")
    
    # Load-Shifting Optimierung
    battery = BatteryState(
        soc_percent=50.0,
        capacity_kwh=1000.0,  # 1 MWh
        max_power_kw=500.0    # 500 kW
    )
    
    # Spotpreise simulieren
    spot_prices = pd.DataFrame({
        'timestamp': consumption_data['timestamp'],
        'price_eur_mwh': 50 + 30 * np.sin(2 * np.pi * np.arange(len(consumption_data)) / 96) + 
                        np.random.normal(0, 10, len(consumption_data))
    })
    
    optimizer = LoadShiftingOptimizer(battery)
    optimization_results = optimizer.optimize_charging_schedule(residual_load, spot_prices)
    
    print(f"\nLoad-Shifting Optimierung:")
    print(f"Optimierungsergebnisse: {len(optimization_results)} Einträge")
    
    # Erlöse berechnen
    revenue_calc = RevenueCalculator()
    revenues = revenue_calc.calculate_total_revenue(optimization_results, battery.max_power_kw)
    
    print(f"\nErlöse:")
    for source, revenue in revenues.items():
        print(f"  {source}: {revenue:,.0f} EUR")
    
    print("\n✓ Test erfolgreich abgeschlossen!")

if __name__ == "__main__":
    main() 