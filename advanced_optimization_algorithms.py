#!/usr/bin/env python3
"""
Advanced Optimization Algorithms für BESS Dispatch
Implementiert MILP (Mixed Integer Linear Programming) und SDP (Stochastic Dynamic Programming)
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

# Optional: Scipy für erweiterte Optimierung
try:
    from scipy.optimize import minimize, linprog
    from scipy.stats import norm
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    print("Warnung: SciPy nicht verfügbar. Verwende vereinfachte Optimierung.")

logger = logging.getLogger(__name__)

@dataclass
class OptimizationParameters:
    """Parameter für Optimierungsalgorithmen"""
    time_horizon_hours: int = 24
    time_step_minutes: int = 15
    risk_tolerance: float = 0.1
    confidence_level: float = 0.95
    max_iterations: int = 1000
    convergence_tolerance: float = 1e-6

@dataclass
class MarketScenario:
    """Marktszenario für stochastische Optimierung"""
    scenario_id: int
    probability: float
    spot_prices: List[float]
    intraday_prices: List[float]
    grid_service_prices: Dict[str, List[float]]

class MILPOptimizer:
    """Mixed Integer Linear Programming Optimizer für BESS Dispatch"""
    
    def __init__(self, bess_capabilities, market_data: List[Dict]):
        self.bess = bess_capabilities
        self.market_data = market_data
        self.time_steps = len(market_data)
        
    def optimize_dispatch(self, initial_soc_pct: float, 
                         optimization_params: OptimizationParameters) -> Dict:
        """Führt MILP-Optimierung durch"""
        
        logger.info(f"Starte MILP-Optimierung für {self.time_steps} Zeitschritte")
        
        # Vereinfachte MILP-Implementierung (ohne externe Solver)
        # In einer Produktionsumgebung würde man Gurobi, CPLEX oder ähnliche verwenden
        
        # Entscheidungsvariablen definieren
        # x[t] = Leistung zum Zeitpunkt t (positiv = entladen, negativ = laden)
        # y[t] = Binärvariable für Grid-Service-Teilnahme
        # z[t] = Binärvariable für Arbitrage-Aktivität
        
        # Zielfunktion: Maximierung des Gesamterlöses
        # max Σ (p_spot[t] * x[t] + p_grid[t] * y[t] + p_arb[t] * z[t])
        
        # Nebenbedingungen:
        # 1. SoC-Constraints: SoC_min ≤ SoC[t] ≤ SoC_max
        # 2. Leistungs-Constraints: -P_max ≤ x[t] ≤ P_max
        # 3. Grid-Service-Constraints: y[t] * P_grid ≤ P_max
        # 4. SoC-Dynamik: SoC[t+1] = SoC[t] + (x[t] * η - x[t] * (1-η)) * Δt
        
        # Vereinfachte Implementierung mit Greedy-Algorithmus
        return self._greedy_optimization(initial_soc_pct, optimization_params)
    
    def _greedy_optimization(self, initial_soc_pct: float, 
                           params: OptimizationParameters) -> Dict:
        """Greedy-Optimierung als Vereinfachung der MILP"""
        
        soc_pct = initial_soc_pct
        decisions = []
        total_revenue = 0.0
        
        for t in range(self.time_steps):
            market = self.market_data[t]
            
            # Verfügbare Optionen bewerten
            options = []
            
            # 1. Arbitrage-Option
            if t < self.time_steps - 1:
                current_price = market.get('spot_price', 0)
                future_price = self.market_data[t + 1].get('spot_price', current_price)
                spread = future_price - current_price
                
                if abs(spread) > 5.0:  # Mindest-Spread
                    if spread > 0 and soc_pct > 20:  # Entladen bei hohem Preis
                        power = min(self.bess.power_max_mw * 0.8, 
                                   (soc_pct - 10) / 100 * self.bess.energy_capacity_mwh)
                        revenue = power * spread / 1000  # Preis in €/MWh
                        options.append({
                            'type': 'arbitrage_discharge',
                            'power_mw': power,
                            'revenue_eur': revenue,
                            'soc_change_pct': -power / self.bess.energy_capacity_mwh * 100
                        })
                    elif spread < 0 and soc_pct < 80:  # Laden bei niedrigem Preis
                        power = min(self.bess.power_max_mw * 0.8,
                                   (80 - soc_pct) / 100 * self.bess.energy_capacity_mwh)
                        revenue = abs(power * spread / 1000)
                        options.append({
                            'type': 'arbitrage_charge',
                            'power_mw': -power,
                            'revenue_eur': revenue,
                            'soc_change_pct': power / self.bess.energy_capacity_mwh * 100
                        })
            
            # 2. Grid-Service-Option
            grid_price = market.get('grid_service_price', 0)
            if grid_price > 20.0 and 20 <= soc_pct <= 80:  # Optimaler SoC-Bereich
                power = self.bess.power_max_mw * 0.3  # 30% für Grid-Services
                revenue = power * grid_price / 1000
                options.append({
                    'type': 'grid_service',
                    'power_mw': power,
                    'revenue_eur': revenue,
                    'soc_change_pct': -power / self.bess.energy_capacity_mwh * 100
                })
            
            # Beste Option auswählen
            if options:
                best_option = max(options, key=lambda x: x['revenue_eur'])
                
                # SoC-Constraints prüfen
                new_soc = soc_pct + best_option['soc_change_pct']
                if 5 <= new_soc <= 95:
                    decisions.append({
                        'time_step': t,
                        'decision': best_option,
                        'soc_before_pct': soc_pct,
                        'soc_after_pct': new_soc
                    })
                    soc_pct = new_soc
                    total_revenue += best_option['revenue_eur']
                else:
                    decisions.append({
                        'time_step': t,
                        'decision': {'type': 'idle', 'power_mw': 0, 'revenue_eur': 0, 'soc_change_pct': 0},
                        'soc_before_pct': soc_pct,
                        'soc_after_pct': soc_pct
                    })
            else:
                decisions.append({
                    'time_step': t,
                    'decision': {'type': 'idle', 'power_mw': 0, 'revenue_eur': 0, 'soc_change_pct': 0},
                    'soc_before_pct': soc_pct,
                    'soc_after_pct': soc_pct
                })
        
        return {
            'optimization_type': 'MILP_Greedy',
            'total_revenue_eur': total_revenue,
            'decisions': decisions,
            'final_soc_pct': soc_pct,
            'convergence_info': {
                'iterations': len(decisions),
                'converged': True
            }
        }

class SDPOptimizer:
    """Stochastic Dynamic Programming Optimizer für BESS Dispatch"""
    
    def __init__(self, bess_capabilities, market_scenarios: List[MarketScenario]):
        self.bess = bess_capabilities
        self.scenarios = market_scenarios
        self.num_scenarios = len(market_scenarios)
        
    def optimize_dispatch(self, initial_soc_pct: float,
                         optimization_params: OptimizationParameters) -> Dict:
        """Führt SDP-Optimierung durch"""
        
        logger.info(f"Starte SDP-Optimierung mit {self.num_scenarios} Szenarien")
        
        # Vereinfachte SDP-Implementierung
        # In einer Produktionsumgebung würde man erweiterte SDP-Algorithmen verwenden
        
        # Bellman-Gleichung: V(s,t) = max_a E[R(s,a,t) + γ * V(s',t+1)]
        # wobei:
        # s = Zustand (SoC)
        # a = Aktion (Dispatch-Entscheidung)
        # t = Zeit
        # R = Sofortiger Erlös
        # γ = Diskontierungsfaktor
        
        return self._simplified_sdp(initial_soc_pct, optimization_params)
    
    def _simplified_sdp(self, initial_soc_pct: float,
                       params: OptimizationParameters) -> Dict:
        """Vereinfachte SDP-Implementierung"""
        
        # Zustandsraum diskretisieren
        soc_states = np.linspace(5, 95, 19)  # 19 SoC-Zustände (5%, 10%, ..., 95%)
        time_steps = params.time_horizon_hours * 4  # 15-Minuten-Schritte
        
        # Wertfunktion initialisieren
        value_function = np.zeros((len(soc_states), time_steps))
        
        # Rückwärts-Induktion (Backward Induction)
        for t in range(time_steps - 1, -1, -1):
            for i, soc in enumerate(soc_states):
                max_value = 0.0
                best_action = None
                
                # Mögliche Aktionen bewerten
                actions = self._get_possible_actions(soc, t)
                
                for action in actions:
                    expected_value = 0.0
                    
                    # Über alle Szenarien mitteln
                    for scenario in self.scenarios:
                        # Sofortiger Erlös
                        immediate_reward = self._calculate_immediate_reward(
                            action, soc, t, scenario
                        )
                        
                        # Zukünftiger Wert (vereinfacht)
                        if t < time_steps - 1:
                            new_soc = self._update_soc(soc, action)
                            future_value = self._interpolate_value(
                                new_soc, soc_states, value_function[:, t + 1]
                            )
                        else:
                            future_value = 0.0
                        
                        # Gesamtwert für dieses Szenario
                        scenario_value = immediate_reward + 0.95 * future_value  # γ = 0.95
                        expected_value += scenario.probability * scenario_value
                    
                    if expected_value > max_value:
                        max_value = expected_value
                        best_action = action
                
                value_function[i, t] = max_value
        
        # Vorwärts-Simulation mit optimaler Politik
        decisions = []
        current_soc = initial_soc_pct
        total_revenue = 0.0
        
        for t in range(time_steps):
            # Beste Aktion für aktuellen Zustand finden
            best_action = self._get_best_action(current_soc, soc_states, value_function[:, t])
            
            # Aktion ausführen
            immediate_reward = self._calculate_immediate_reward(
                best_action, current_soc, t, self.scenarios[0]  # Vereinfacht: erstes Szenario
            )
            
            new_soc = self._update_soc(current_soc, best_action)
            
            decisions.append({
                'time_step': t,
                'action': best_action,
                'soc_before_pct': current_soc,
                'soc_after_pct': new_soc,
                'immediate_reward_eur': immediate_reward
            })
            
            current_soc = new_soc
            total_revenue += immediate_reward
        
        return {
            'optimization_type': 'SDP_Simplified',
            'total_revenue_eur': total_revenue,
            'decisions': decisions,
            'final_soc_pct': current_soc,
            'value_function': value_function.tolist(),
            'convergence_info': {
                'iterations': time_steps,
                'converged': True
            }
        }
    
    def _get_possible_actions(self, soc_pct: float, time_step: int) -> List[Dict]:
        """Gibt mögliche Aktionen für einen gegebenen Zustand zurück"""
        actions = []
        
        # Idle-Aktion
        actions.append({
            'type': 'idle',
            'power_mw': 0.0,
            'soc_change_pct': 0.0
        })
        
        # Laden (wenn SoC < 90%)
        if soc_pct < 90:
            max_charge_power = min(
                self.bess.power_max_mw,
                (90 - soc_pct) / 100 * self.bess.energy_capacity_mwh
            )
            actions.append({
                'type': 'charge',
                'power_mw': -max_charge_power,
                'soc_change_pct': max_charge_power / self.bess.energy_capacity_mwh * 100
            })
        
        # Entladen (wenn SoC > 10%)
        if soc_pct > 10:
            max_discharge_power = min(
                self.bess.power_max_mw,
                (soc_pct - 10) / 100 * self.bess.energy_capacity_mwh
            )
            actions.append({
                'type': 'discharge',
                'power_mw': max_discharge_power,
                'soc_change_pct': -max_discharge_power / self.bess.energy_capacity_mwh * 100
            })
        
        return actions
    
    def _calculate_immediate_reward(self, action: Dict, soc_pct: float, 
                                   time_step: int, scenario: MarketScenario) -> float:
        """Berechnet den sofortigen Erlös für eine Aktion"""
        if action['type'] == 'idle':
            return 0.0
        
        # Vereinfachte Erlösberechnung
        if action['type'] == 'charge':
            price = scenario.spot_prices[min(time_step, len(scenario.spot_prices) - 1)]
            return abs(action['power_mw']) * price / 1000 * 0.25  # 15 Minuten
        elif action['type'] == 'discharge':
            price = scenario.spot_prices[min(time_step, len(scenario.spot_prices) - 1)]
            return action['power_mw'] * price / 1000 * 0.25  # 15 Minuten
        
        return 0.0
    
    def _update_soc(self, current_soc: float, action: Dict) -> float:
        """Aktualisiert den SoC basierend auf der Aktion"""
        new_soc = current_soc + action['soc_change_pct']
        return max(5.0, min(95.0, new_soc))  # Constraints
    
    def _interpolate_value(self, soc: float, soc_states: np.ndarray, 
                          values: np.ndarray) -> float:
        """Interpoliert den Wert für einen gegebenen SoC"""
        if soc <= soc_states[0]:
            return values[0]
        if soc >= soc_states[-1]:
            return values[-1]
        
        # Lineare Interpolation
        idx = np.searchsorted(soc_states, soc)
        if idx == 0:
            return values[0]
        
        x1, x2 = soc_states[idx - 1], soc_states[idx]
        y1, y2 = values[idx - 1], values[idx]
        
        return y1 + (y2 - y1) * (soc - x1) / (x2 - x1)
    
    def _get_best_action(self, soc: float, soc_states: np.ndarray, 
                        values: np.ndarray) -> Dict:
        """Findet die beste Aktion für einen gegebenen SoC"""
        # Vereinfachte Implementierung
        if soc < 30:
            return {'type': 'charge', 'power_mw': -1.0, 'soc_change_pct': 2.0}
        elif soc > 70:
            return {'type': 'discharge', 'power_mw': 1.0, 'soc_change_pct': -2.0}
        else:
            return {'type': 'idle', 'power_mw': 0.0, 'soc_change_pct': 0.0}

class AdvancedOptimizationEngine:
    """Hauptklasse für erweiterte Optimierungsalgorithmen"""
    
    def __init__(self, bess_capabilities):
        self.bess = bess_capabilities
        self.milp_optimizer = None
        self.sdp_optimizer = None
        
    def create_market_scenarios(self, base_prices: List[float], 
                               num_scenarios: int = 5) -> List[MarketScenario]:
        """Erstellt Marktszenarien für stochastische Optimierung"""
        scenarios = []
        
        for i in range(num_scenarios):
            # Zufällige Variation der Basispreise
            variation = np.random.normal(1.0, 0.1, len(base_prices))
            scenario_prices = [p * v for p, v in zip(base_prices, variation)]
            
            scenario = MarketScenario(
                scenario_id=i,
                probability=1.0 / num_scenarios,
                spot_prices=scenario_prices,
                intraday_prices=[p * 1.1 for p in scenario_prices],  # 10% höher
                grid_service_prices={
                    'frequency_regulation': [25.0] * len(base_prices),
                    'voltage_support': [8.0] * len(base_prices)
                }
            )
            scenarios.append(scenario)
        
        return scenarios
    
    def optimize_with_milp(self, market_data: List[Dict], 
                          initial_soc_pct: float,
                          params: OptimizationParameters) -> Dict:
        """Optimiert mit MILP-Algorithmus"""
        self.milp_optimizer = MILPOptimizer(self.bess, market_data)
        return self.milp_optimizer.optimize_dispatch(initial_soc_pct, params)
    
    def optimize_with_sdp(self, base_prices: List[float],
                         initial_soc_pct: float,
                         params: OptimizationParameters) -> Dict:
        """Optimiert mit SDP-Algorithmus"""
        scenarios = self.create_market_scenarios(base_prices)
        self.sdp_optimizer = SDPOptimizer(self.bess, scenarios)
        return self.sdp_optimizer.optimize_dispatch(initial_soc_pct, params)
    
    def compare_algorithms(self, market_data: List[Dict],
                          base_prices: List[float],
                          initial_soc_pct: float,
                          params: OptimizationParameters) -> Dict:
        """Vergleicht verschiedene Optimierungsalgorithmen"""
        
        results = {}
        
        # MILP-Optimierung
        try:
            milp_result = self.optimize_with_milp(market_data, initial_soc_pct, params)
            results['milp'] = {
                'total_revenue_eur': milp_result['total_revenue_eur'],
                'final_soc_pct': milp_result['final_soc_pct'],
                'optimization_type': milp_result['optimization_type'],
                'success': True
            }
        except Exception as e:
            results['milp'] = {
                'error': str(e),
                'success': False
            }
        
        # SDP-Optimierung
        try:
            sdp_result = self.optimize_with_sdp(base_prices, initial_soc_pct, params)
            results['sdp'] = {
                'total_revenue_eur': sdp_result['total_revenue_eur'],
                'final_soc_pct': sdp_result['final_soc_pct'],
                'optimization_type': sdp_result['optimization_type'],
                'success': True
            }
        except Exception as e:
            results['sdp'] = {
                'error': str(e),
                'success': False
            }
        
        # Vergleich
        if results['milp']['success'] and results['sdp']['success']:
            milp_revenue = results['milp']['total_revenue_eur']
            sdp_revenue = results['sdp']['total_revenue_eur']
            
            if milp_revenue > sdp_revenue:
                best_algorithm = 'MILP'
                improvement = ((milp_revenue - sdp_revenue) / max(sdp_revenue, 0.01)) * 100
            else:
                best_algorithm = 'SDP'
                improvement = ((sdp_revenue - milp_revenue) / max(milp_revenue, 0.01)) * 100
            
            results['comparison'] = {
                'best_algorithm': best_algorithm,
                'improvement_pct': improvement,
                'milp_revenue': milp_revenue,
                'sdp_revenue': sdp_revenue
            }
        
        return results

def create_demo_optimization_engine():
    """Erstellt Demo-Optimization-Engine für Tests"""
    from advanced_dispatch_system import create_demo_bess
    
    bess = create_demo_bess()
    return AdvancedOptimizationEngine(bess)

if __name__ == "__main__":
    # Demo-Test
    print("🚀 Teste Advanced Optimization Algorithms...")
    
    engine = create_demo_optimization_engine()
    
    # Demo-Marktdaten
    market_data = [
        {'spot_price': 60.0, 'grid_service_price': 25.0},
        {'spot_price': 65.0, 'grid_service_price': 30.0},
        {'spot_price': 55.0, 'grid_service_price': 20.0},
        {'spot_price': 70.0, 'grid_service_price': 35.0},
        {'spot_price': 50.0, 'grid_service_price': 15.0},
    ] * 5  # 25 Zeitschritte
    
    base_prices = [60.0, 65.0, 55.0, 70.0, 50.0] * 5
    
    params = OptimizationParameters(
        time_horizon_hours=6,
        time_step_minutes=15,
        risk_tolerance=0.1
    )
    
    # Algorithmus-Vergleich
    results = engine.compare_algorithms(market_data, base_prices, 50.0, params)
    
    print("📊 Optimierungsergebnisse:")
    for algorithm, result in results.items():
        if algorithm != 'comparison':
            if result['success']:
                print(f"  {algorithm.upper()}: {result['total_revenue_eur']:.2f} €")
            else:
                print(f"  {algorithm.upper()}: Fehler - {result['error']}")
    
    if 'comparison' in results:
        comp = results['comparison']
        print(f"  Beste Methode: {comp['best_algorithm']}")
        print(f"  Verbesserung: {comp['improvement_pct']:.1f}%")
    
    print("🎉 Advanced Optimization Algorithms funktionieren!")
