#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BESS Sizing Optimizer mit PS/LL-Exhaustionsmethode
Integriert Peak Shaving und Load Leveling in die BESS-Simulation
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import json
import os

# Integration bestehender Module
try:
    from economic_analysis_enhanced import EconomicAnalysisEnhanced, InvestmentData, OperatingData
    from advanced_optimization_algorithms import MILPOptimizer, OptimizationParameters
    EXISTING_MODULES_AVAILABLE = True
except ImportError as e:
    EXISTING_MODULES_AVAILABLE = False
    print(f"Warnung: Bestehende Module nicht verfügbar: {e}")

# C-Rate-Module (optional)
try:
    from c_rate.bess.battery import Battery
    from c_rate.bess.crate import CRConfig, compute_power_bounds, apply_bounds
    C_RATE_AVAILABLE = True
except ImportError:
    C_RATE_AVAILABLE = False
    print("Warnung: C-Rate-Module nicht verfügbar - verwende vereinfachte Constraints")

logger = logging.getLogger(__name__)

@dataclass
class PSLLConstraints:
    """Constraints für PS/LL-Sizing"""
    max_investment_eur: float = 1000000.0
    available_space_m2: float = 100.0
    grid_connection_mw: float = 1.0
    min_soc_percent: float = 20.0
    max_soc_percent: float = 90.0
    efficiency_charge: float = 0.95
    efficiency_discharge: float = 0.95
    c_rate_charge: float = 1.0
    c_rate_discharge: float = 1.0

@dataclass
class SizingResult:
    """Ergebnis der BESS-Sizing-Optimierung"""
    optimal_power_kw: float
    optimal_capacity_kwh: float
    total_investment_eur: float
    annual_savings_eur: float
    payback_period_years: float
    roi_percent: float
    feasible_region: List[Dict[str, float]]
    cost_heatmap_data: Dict[str, Any]
    strategy_comparison: Dict[str, Any]

class BESSSizingOptimizer:
    """Hauptklasse für BESS-Sizing mit PS/LL-Exhaustionsmethode"""
    
    def __init__(self, project_data: Dict, load_profile: pd.DataFrame, 
                 market_data: pd.DataFrame, constraints: PSLLConstraints):
        self.project = project_data
        self.load_profile = load_profile
        self.market_data = market_data
        self.constraints = constraints
        
        # PS/LL-Parameter
        self.monthly_limits = {}
        self.feasible_combinations = []
        
    def calculate_monthly_limits(self) -> Dict[int, float]:
        """Berechnet monatliche P_limit,m aus 95%-Quantil der Last"""
        monthly_limits = {}
        
        for month in range(1, 13):
            month_data = self.load_profile[self.load_profile.index.month == month]
            if not month_data.empty:
                # 95%-Quantil als P_limit,m
                p_limit = np.quantile(month_data['load_kw'], 0.95)
                monthly_limits[month] = p_limit
                logger.info(f"Monat {month}: P_limit = {p_limit:.2f} kW")
        
        self.monthly_limits = monthly_limits
        return monthly_limits
    
    def simulate_ps_ll_strategy(self, p_ess_kw: float, q_ess_kwh: float) -> Dict[str, Any]:
        """
        Simuliert PS/LL-Strategie für gegebene BESS-Parameter
        Basierend auf PS/sizing_ps_ll.py mit C-Rate-Constraints
        """
        soc = 0.5 * q_ess_kwh  # Start-SoC bei 50%
        soc_trace = []
        clipped_load = []
        monthly_results = {}
        
        # C-Rate-Config erstellen
        if C_RATE_AVAILABLE:
            c_rate_config = CRConfig(
                E_nom_kWh=q_ess_kwh,
                C_chg_rate=self.constraints.c_rate_charge,
                C_dis_rate=self.constraints.c_rate_discharge,
                derating_enable=True
            )
        
        for month in range(1, 13):
            month_data = self.load_profile[self.load_profile.index.month == month]
            if month_data.empty:
                continue
                
            p_limit = self.monthly_limits.get(month, np.quantile(month_data['load_kw'], 0.95))
            month_soc = soc
            month_clipped = []
            
            for timestamp, row in month_data.iterrows():
                load = row['load_kw']
                current_soc_pct = (month_soc / q_ess_kwh) * 100
                
                # PS/LL-Entscheidungslogik mit C-Rate-Constraints
                if load > p_limit and month_soc > 0:
                    # Peak Shaving: Entladen
                    if C_RATE_AVAILABLE:
                        # C-Rate-Constraints anwenden
                        bounds = compute_power_bounds(
                            q_ess_kwh,
                            self.constraints.c_rate_charge,
                            self.constraints.c_rate_discharge,
                            SoC=current_soc_pct,
                            cfg=c_rate_config
                        )
                        max_discharge = bounds["P_dis_max_kW"]
                        discharge = min(p_ess_kw, max_discharge, month_soc / 1.0)
                    else:
                        discharge = min(p_ess_kw, month_soc / 1.0)
                    
                    month_soc -= discharge * 0.25 * self.constraints.efficiency_discharge
                    clipped_load_val = load - discharge
                    
                elif load < p_limit and month_soc < q_ess_kwh:
                    # Load Leveling: Laden
                    if C_RATE_AVAILABLE:
                        # C-Rate-Constraints anwenden
                        bounds = compute_power_bounds(
                            q_ess_kwh,
                            self.constraints.c_rate_charge,
                            self.constraints.c_rate_discharge,
                            SoC=current_soc_pct,
                            cfg=c_rate_config
                        )
                        max_charge = bounds["P_chg_max_kW"]
                        charge = min(p_ess_kw, max_charge, (q_ess_kwh - month_soc) / 1.0)
                    else:
                        charge = min(p_ess_kw, (q_ess_kwh - month_soc) / 1.0)
                    
                    month_soc += charge * 0.25 * self.constraints.efficiency_charge
                    clipped_load_val = load + charge
                else:
                    clipped_load_val = load
                
                # SoC-Grenzen einhalten
                min_soc_kwh = (self.constraints.min_soc_percent / 100) * q_ess_kwh
                max_soc_kwh = (self.constraints.max_soc_percent / 100) * q_ess_kwh
                month_soc = max(min_soc_kwh, min(max_soc_kwh, month_soc))
                month_clipped.append(clipped_load_val)
                soc_trace.append(month_soc)
            
            # Monatliche Ergebnisse
            original_peak = month_data['load_kw'].max()
            new_peak = max(month_clipped) if month_clipped else original_peak
            peak_reduction = original_peak - new_peak
            
            monthly_results[month] = {
                'original_peak': original_peak,
                'new_peak': new_peak,
                'peak_reduction': peak_reduction,
                'feasible': peak_reduction > 0
            }
        
        clipped_load.extend([item for sublist in [month_clipped for month_clipped in 
                        [month_data['load_kw'].tolist() for month_data in 
                         [self.load_profile[self.load_profile.index.month == m] for m in range(1, 13)]]] 
                        for item in sublist])
        
        return {
            'soc_trace': soc_trace,
            'clipped_load': clipped_load,
            'monthly_results': monthly_results,
            'feasible': all(result['feasible'] for result in monthly_results.values())
        }
    
    def find_feasible_region(self, p_range: Tuple[float, float], q_range: Tuple[float, float],
                           step_size: float = 0.5) -> List[Dict[str, float]]:
        """Findet alle machbaren (P_ESS, Q_ESS) Kombinationen"""
        feasible_combinations = []
        
        p_min, p_max = p_range
        q_min, q_max = q_range
        
        p_steps = int((p_max - p_min) / step_size) + 1
        q_steps = int((q_max - q_min) / step_size) + 1
        
        logger.info(f"Suche Feasible Region: {p_steps} x {q_steps} = {p_steps * q_steps} Kombinationen")
        
        for i in range(p_steps):
            p_ess = p_min + i * step_size
            for j in range(q_steps):
                q_ess = q_min + j * step_size
                
                # C-Rate-Constraint prüfen
                if C_RATE_AVAILABLE:
                    # Erweiterte C-Rate-Prüfung mit SoC-abhängigen Constraints
                    bounds = compute_power_bounds(
                        q_ess,
                        self.constraints.c_rate_charge,
                        self.constraints.c_rate_discharge,
                        SoC=50.0,  # Mittlerer SoC für Prüfung
                        cfg=CRConfig(q_ess, self.constraints.c_rate_charge, self.constraints.c_rate_discharge)
                    )
                    if p_ess > bounds["P_dis_max_kW"] or p_ess > bounds["P_chg_max_kW"]:
                        continue
                else:
                    # Vereinfachte C-Rate-Prüfung
                    if p_ess > q_ess * self.constraints.c_rate_discharge:
                        continue
                
                # Simulation durchführen
                result = self.simulate_ps_ll_strategy(p_ess, q_ess)
                
                if result['feasible']:
                    # Kosten berechnen
                    investment_cost = self._calculate_investment_cost(p_ess, q_ess)
                    annual_savings = self._calculate_annual_savings(result)
                    
                    feasible_combinations.append({
                        'p_ess_kw': p_ess,
                        'q_ess_kwh': q_ess,
                        'investment_cost_eur': investment_cost,
                        'annual_savings_eur': annual_savings,
                        'payback_years': investment_cost / annual_savings if annual_savings > 0 else float('inf'),
                        'roi_percent': (annual_savings * 20 - investment_cost) / investment_cost * 100 if investment_cost > 0 else 0
                    })
        
        self.feasible_combinations = feasible_combinations
        logger.info(f"Feasible Region: {len(feasible_combinations)} Kombinationen gefunden")
        return feasible_combinations
    
    def optimize_bess_size(self) -> SizingResult:
        """Hauptoptimierungsfunktion - findet optimale BESS-Größe"""
        logger.info("Starte BESS-Sizing-Optimierung mit PS/LL-Exhaustionsmethode")
        
        # 1. Monatliche Grenzwerte berechnen
        self.calculate_monthly_limits()
        
        # 2. Feasible Region finden
        p_range = (100, 5000)  # 100 kW bis 5 MW
        q_range = (200, 20000)  # 200 kWh bis 20 MWh
        feasible_combinations = self.find_feasible_region(p_range, q_range)
        
        if not feasible_combinations:
            raise ValueError("Keine machbaren BESS-Kombinationen gefunden!")
        
        # 3. Optimale Kombination finden (höchster ROI)
        optimal_combination = max(feasible_combinations, key=lambda x: x['roi_percent'])
        
        # 4. Heatmap-Daten für Visualisierung
        heatmap_data = self._create_heatmap_data(feasible_combinations)
        
        # 5. Strategievergleich
        strategy_comparison = self._compare_strategies(optimal_combination)
        
        return SizingResult(
            optimal_power_kw=optimal_combination['p_ess_kw'],
            optimal_capacity_kwh=optimal_combination['q_ess_kwh'],
            total_investment_eur=optimal_combination['investment_cost_eur'],
            annual_savings_eur=optimal_combination['annual_savings_eur'],
            payback_period_years=optimal_combination['payback_years'],
            roi_percent=optimal_combination['roi_percent'],
            feasible_region=feasible_combinations,
            cost_heatmap_data=heatmap_data,
            strategy_comparison=strategy_comparison
        )
    
    def _calculate_investment_cost(self, p_ess_kw: float, q_ess_kwh: float) -> float:
        """Berechnet Investitionskosten für BESS"""
        # Vereinfachte Kostenberechnung
        power_cost_per_kw = 800  # €/kW
        capacity_cost_per_kwh = 400  # €/kWh
        
        return p_ess_kw * power_cost_per_kw + q_ess_kwh * capacity_cost_per_kwh
    
    def _calculate_annual_savings(self, simulation_result: Dict) -> float:
        """Berechnet jährliche Einsparungen aus PS/LL"""
        total_savings = 0.0
        
        for month, result in simulation_result['monthly_results'].items():
            # Peak Shaving Einsparungen (Leistungspreis)
            peak_reduction = result['peak_reduction']
            power_price_eur_kw_month = 15.0  # €/kW/Monat
            monthly_savings = peak_reduction * power_price_eur_kw_month
            total_savings += monthly_savings
        
        return total_savings
    
    def _create_heatmap_data(self, feasible_combinations: List[Dict]) -> Dict[str, Any]:
        """Erstellt Heatmap-Daten für Visualisierung"""
        if not feasible_combinations:
            return {}
        
        # Daten für Heatmap extrahieren
        p_values = [combo['p_ess_kw'] for combo in feasible_combinations]
        q_values = [combo['q_ess_kwh'] for combo in feasible_combinations]
        roi_values = [combo['roi_percent'] for combo in feasible_combinations]
        
        return {
            'p_ess_kw': p_values,
            'q_ess_kwh': q_values,
            'roi_percent': roi_values,
            'investment_cost_eur': [combo['investment_cost_eur'] for combo in feasible_combinations],
            'payback_years': [combo['payback_years'] for combo in feasible_combinations]
        }
    
    def _compare_strategies(self, optimal_combination: Dict) -> Dict[str, Any]:
        """Vergleicht PS/LL mit anderen Strategien"""
        # Vereinfachter Vergleich - in Produktion würde man echte Arbitrage-Simulation durchführen
        return {
            'ps_ll': {
                'roi_percent': optimal_combination['roi_percent'],
                'payback_years': optimal_combination['payback_years'],
                'strategy': 'Peak Shaving + Load Leveling'
            },
            'arbitrage': {
                'roi_percent': optimal_combination['roi_percent'] * 0.8,  # Geschätzt
                'payback_years': optimal_combination['payback_years'] * 1.2,
                'strategy': 'Spot-Preis-Arbitrage'
            },
            'grid_services': {
                'roi_percent': optimal_combination['roi_percent'] * 0.6,  # Geschätzt
                'payback_years': optimal_combination['payback_years'] * 1.5,
                'strategy': 'Netzstabilitätsdienstleistungen'
            }
        }

def create_demo_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Erstellt Demo-Daten für Tests"""
    # Demo-Lastprofil (1 Monat, 15-min Auflösung für schnelleren Test)
    np.random.seed(42)
    dates = pd.date_range("2024-01-01", periods=30*96, freq="15min")  # 1 Monat
    
    # Vereinfachtes Lastprofil
    base_load = 1000  # kW
    daily_pattern = 1 + 0.5 * np.sin(2 * np.pi * np.arange(len(dates)) / 96)
    random_noise = np.random.normal(0, 0.1, len(dates))
    
    load_kw = base_load * daily_pattern * (1 + random_noise)
    
    load_profile = pd.DataFrame({
        'load_kw': load_kw
    }, index=dates)
    
    # Demo-Marktdaten
    market_data = pd.DataFrame({
        'spot_price_eur_mwh': 50 + 30 * np.sin(2 * np.pi * np.arange(len(dates)) / 96) + np.random.normal(0, 10, len(dates))
    }, index=dates)
    
    return load_profile, market_data

if __name__ == "__main__":
    # Demo-Test
    print("🚀 BESS Sizing Optimizer - Demo-Test")
    
    # Demo-Daten erstellen
    load_profile, market_data = create_demo_data()
    
    # Projekt-Daten
    project_data = {
        'name': 'Demo BESS Projekt',
        'location': 'Wien, Österreich',
        'annual_consumption_mwh': 8760
    }
    
    # Constraints
    constraints = PSLLConstraints(
        max_investment_eur=2000000.0,
        available_space_m2=200.0,
        grid_connection_mw=2.0
    )
    
    # Optimizer erstellen und ausführen
    optimizer = BESSSizingOptimizer(project_data, load_profile, market_data, constraints)
    
    try:
        result = optimizer.optimize_bess_size()
        
        print(f"\n✅ Optimierung erfolgreich!")
        print(f"📊 Optimale BESS-Größe:")
        print(f"   Leistung: {result.optimal_power_kw:.1f} kW")
        print(f"   Kapazität: {result.optimal_capacity_kwh:.1f} kWh")
        print(f"   Investition: {result.total_investment_eur:,.0f} €")
        print(f"   Jährliche Einsparungen: {result.annual_savings_eur:,.0f} €")
        print(f"   Amortisationszeit: {result.payback_period_years:.1f} Jahre")
        print(f"   ROI (20 Jahre): {result.roi_percent:.1f}%")
        print(f"   Feasible Kombinationen: {len(result.feasible_region)}")
        
    except Exception as e:
        print(f"❌ Fehler bei der Optimierung: {e}")
        logger.error(f"Optimierung fehlgeschlagen: {e}")
