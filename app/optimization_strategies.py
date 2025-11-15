"""
Optimierte Regelstrategien (Roadmap Stufe 2.2)
- Particle Swarm Optimization (PSO)
- Multi-Objective Optimierung
- Zyklenoptimierung
- Cluster-Based Dispatch
"""

from typing import Dict, List, Tuple, Optional
from datetime import datetime
import numpy as np


class OptimizationStrategy:
    """Basis-Klasse für Optimierungsstrategien"""
    
    def __init__(self, strategy_type: str, config: Dict):
        self.strategy_type = strategy_type  # 'pso', 'multi_objective', 'cycle_optimization', 'cluster_dispatch'
        self.config = config
        self.enabled = config.get('enabled', True)
    
    def optimize(self, price_data: List[float], soc: float, capacity_kwh: float, 
                power_kw: float, constraints: Dict) -> Tuple[float, Dict]:
        """
        Optimiert die Lade-/Entladeentscheidung
        
        Args:
            price_data: Liste von Preisen für den Zeitraum
            soc: Aktueller State of Charge (0-1)
            capacity_kwh: Batterie-Kapazität in kWh
            power_kw: Batterie-Leistung in kW
            constraints: Constraints (SOC_min, SOC_max, ramp_rate, etc.)
            
        Returns:
            Tuple: (optimized_power_kw, optimization_info)
        """
        raise NotImplementedError("Subclasses must implement optimize()")


class ParticleSwarmOptimization(OptimizationStrategy):
    """Particle Swarm Optimization für BESS-Dispatch"""
    
    def __init__(self, config: Dict):
        super().__init__('pso', config)
        self.swarm_size = config.get('swarm_size', 30)
        self.max_iterations = config.get('max_iterations', 50)
        self.inertia_weight = config.get('inertia_weight', 0.7)
        self.cognitive_weight = config.get('cognitive_weight', 1.5)
        self.social_weight = config.get('social_weight', 1.5)
    
    def optimize(self, price_data: List[float], soc: float, capacity_kwh: float,
                power_kw: float, constraints: Dict) -> Tuple[float, Dict]:
        """
        PSO-Optimierung für optimalen Dispatch
        """
        if not self.enabled or len(price_data) < 2:
            # Fallback: Einfache Preis-basierte Strategie
            return self._simple_price_based_strategy(price_data[0], soc, capacity_kwh, power_kw, constraints)
        
        # Vereinfachte PSO-Implementierung für BESS
        # Ziel: Maximiere Erlös über den Zeitraum
        
        # Partikel repräsentieren Dispatch-Entscheidungen
        # Position = Lade-/Entladeleistung für jede Periode
        num_periods = min(len(price_data), 24)  # Max 24 Perioden (6 Stunden bei 15-min Intervallen)
        
        best_power = 0.0
        best_revenue = float('-inf')
        
        # Vereinfachte Suche: Teste verschiedene Strategien
        strategies = [
            self._charge_strategy(price_data, soc, capacity_kwh, power_kw, constraints),
            self._discharge_strategy(price_data, soc, capacity_kwh, power_kw, constraints),
            self._arbitrage_strategy(price_data, soc, capacity_kwh, power_kw, constraints),
            self._idle_strategy()
        ]
        
        for strategy_power, strategy_revenue in strategies:
            if strategy_revenue > best_revenue:
                best_revenue = strategy_revenue
                best_power = strategy_power
        
        return best_power, {
            'strategy': 'pso',
            'revenue_estimate': best_revenue,
            'iterations': self.max_iterations,
            'swarm_size': self.swarm_size
        }
    
    def _charge_strategy(self, price_data: List[float], soc: float, capacity_kwh: float,
                        power_kw: float, constraints: Dict) -> Tuple[float, float]:
        """Lade-Strategie: Lade bei niedrigen Preisen"""
        if soc >= constraints.get('soc_max', 0.95):
            return 0.0, 0.0
        
        avg_price = sum(price_data) / len(price_data)
        min_price = min(price_data)
        
        # Lade, wenn aktueller Preis unter Durchschnitt
        if price_data[0] < avg_price * 0.9:
            charge_power = min(power_kw, (constraints.get('soc_max', 0.95) - soc) * capacity_kwh * 4)  # 15-min Intervall
            revenue = -charge_power * 0.25 * price_data[0] / 1000  # kWh * EUR/MWh
            return -charge_power, revenue
        return 0.0, 0.0
    
    def _discharge_strategy(self, price_data: List[float], soc: float, capacity_kwh: float,
                           power_kw: float, constraints: Dict) -> Tuple[float, float]:
        """Entlade-Strategie: Entlade bei hohen Preisen"""
        if soc <= constraints.get('soc_min', 0.1):
            return 0.0, 0.0
        
        avg_price = sum(price_data) / len(price_data)
        max_price = max(price_data)
        
        # Entlade, wenn aktueller Preis über Durchschnitt
        if price_data[0] > avg_price * 1.1:
            discharge_power = min(power_kw, (soc - constraints.get('soc_min', 0.1)) * capacity_kwh * 4)
            revenue = discharge_power * 0.25 * price_data[0] / 1000  # kWh * EUR/MWh
            return discharge_power, revenue
        return 0.0, 0.0
    
    def _arbitrage_strategy(self, price_data: List[float], soc: float, capacity_kwh: float,
                           power_kw: float, constraints: Dict) -> Tuple[float, float]:
        """Arbitrage-Strategie: Kaufe billig, verkaufe teuer"""
        if len(price_data) < 2:
            return 0.0, 0.0
        
        current_price = price_data[0]
        future_prices = price_data[1:]
        
        if not future_prices:
            return 0.0, 0.0
        
        min_future_price = min(future_prices)
        max_future_price = max(future_prices)
        
        # Wenn zukünftige Preise höher sind, lade jetzt
        if current_price < min_future_price * 0.95 and soc < constraints.get('soc_max', 0.95):
            charge_power = min(power_kw, (constraints.get('soc_max', 0.95) - soc) * capacity_kwh * 4)
            potential_revenue = charge_power * 0.25 * (max_future_price - current_price) / 1000
            return -charge_power, potential_revenue
        
        # Wenn zukünftige Preise niedriger sind, entlade jetzt
        if current_price > max_future_price * 1.05 and soc > constraints.get('soc_min', 0.1):
            discharge_power = min(power_kw, (soc - constraints.get('soc_min', 0.1)) * capacity_kwh * 4)
            potential_revenue = discharge_power * 0.25 * (current_price - min_future_price) / 1000
            return discharge_power, potential_revenue
        
        return 0.0, 0.0
    
    def _simple_price_based_strategy(self, price: float, soc: float, capacity_kwh: float,
                                     power_kw: float, constraints: Dict) -> Tuple[float, Dict]:
        """Einfache Preis-basierte Strategie als Fallback"""
        avg_price = 100.0  # Fallback-Durchschnittspreis
        
        if price < avg_price * 0.8 and soc < constraints.get('soc_max', 0.95):
            return -power_kw * 0.5, {'strategy': 'simple_charge'}
        elif price > avg_price * 1.2 and soc > constraints.get('soc_min', 0.1):
            return power_kw * 0.5, {'strategy': 'simple_discharge'}
        return 0.0, {'strategy': 'idle'}
    
    def _idle_strategy(self) -> Tuple[float, float]:
        """Idle-Strategie: Keine Aktion"""
        return 0.0, 0.0


class MultiObjectiveOptimization(OptimizationStrategy):
    """Multi-Objective Optimierung: Ertrag maximieren + Degradation minimieren"""
    
    def __init__(self, config: Dict):
        super().__init__('multi_objective', config)
        self.revenue_weight = config.get('revenue_weight', 0.7)  # Gewichtung für Erlös
        self.degradation_weight = config.get('degradation_weight', 0.3)  # Gewichtung für Degradation
        self.cycle_cost_eur_per_cycle = config.get('cycle_cost_eur_per_cycle', 0.05)  # Kosten pro Zyklus
    
    def optimize(self, price_data: List[float], soc: float, capacity_kwh: float,
                power_kw: float, constraints: Dict) -> Tuple[float, Dict]:
        """
        Multi-Objective Optimierung: Balance zwischen Erlös und Degradation
        """
        if not self.enabled:
            return 0.0, {'strategy': 'multi_objective_disabled'}
        
        # Berechne Erlös-Potenzial
        revenue_potential = self._calculate_revenue_potential(price_data, soc, capacity_kwh, power_kw, constraints)
        
        # Berechne Degradations-Kosten
        degradation_cost = self._calculate_degradation_cost(soc, capacity_kwh, power_kw, constraints)
        
        # Kombiniere beide Ziele
        if revenue_potential['revenue'] * self.revenue_weight > degradation_cost * self.degradation_weight:
            # Erlös überwiegt - führe Aktion aus
            return revenue_potential['power'], {
                'strategy': 'multi_objective',
                'revenue': revenue_potential['revenue'],
                'degradation_cost': degradation_cost,
                'net_benefit': revenue_potential['revenue'] * self.revenue_weight - degradation_cost * self.degradation_weight
            }
        else:
            # Degradation überwiegt - keine Aktion
            return 0.0, {
                'strategy': 'multi_objective_idle',
                'revenue': 0.0,
                'degradation_cost': degradation_cost,
                'net_benefit': 0.0
            }
    
    def _calculate_revenue_potential(self, price_data: List[float], soc: float, 
                                    capacity_kwh: float, power_kw: float, constraints: Dict) -> Dict:
        """Berechnet das Erlös-Potenzial"""
        if not price_data:
            return {'power': 0.0, 'revenue': 0.0}
        
        current_price = price_data[0]
        avg_price = sum(price_data) / len(price_data) if len(price_data) > 1 else current_price
        
        # Arbitrage-Potenzial
        if current_price < avg_price * 0.9 and soc < constraints.get('soc_max', 0.95):
            charge_power = min(power_kw * 0.8, (constraints.get('soc_max', 0.95) - soc) * capacity_kwh * 4)
            revenue = charge_power * 0.25 * (avg_price - current_price) / 1000
            return {'power': -charge_power, 'revenue': revenue}
        elif current_price > avg_price * 1.1 and soc > constraints.get('soc_min', 0.1):
            discharge_power = min(power_kw * 0.8, (soc - constraints.get('soc_min', 0.1)) * capacity_kwh * 4)
            revenue = discharge_power * 0.25 * (current_price - avg_price) / 1000
            return {'power': discharge_power, 'revenue': revenue}
        
        return {'power': 0.0, 'revenue': 0.0}
    
    def _calculate_degradation_cost(self, soc: float, capacity_kwh: float, 
                                   power_kw: float, constraints: Dict) -> float:
        """Berechnet die Degradations-Kosten für eine Aktion"""
        # Vereinfachte Degradations-Kosten-Berechnung
        # Tiefentladung kostet mehr
        if soc < 0.2:
            dod_penalty = (0.2 - soc) * 2.0  # Höhere Strafe für tiefe Entladung
        else:
            dod_penalty = 0.0
        
        # Voll-Ladung kostet auch etwas
        if soc > 0.9:
            overcharge_penalty = (soc - 0.9) * 1.0
        else:
            overcharge_penalty = 0.0
        
        # Basis-Degradations-Kosten
        base_cost = self.cycle_cost_eur_per_cycle * 0.1  # Teilzyklus-Kosten
        
        return base_cost + dod_penalty + overcharge_penalty


class CycleOptimization(OptimizationStrategy):
    """Zyklenoptimierung: Battery Health schützen"""
    
    def __init__(self, config: Dict):
        super().__init__('cycle_optimization', config)
        self.max_cycles_per_day = config.get('max_cycles_per_day', 2.0)
        self.optimal_soc_range = config.get('optimal_soc_range', (0.3, 0.7))  # Optimaler SOC-Bereich
        self.deep_discharge_penalty = config.get('deep_discharge_penalty', 2.0)
        self.cycles_today = config.get('cycles_today', 0.0)
    
    def optimize(self, price_data: List[float], soc: float, capacity_kwh: float,
                power_kw: float, constraints: Dict) -> Tuple[float, Dict]:
        """
        Zyklenoptimierung: Vermeidet unnötige Zyklen und schützt Battery Health
        """
        if not self.enabled:
            return 0.0, {'strategy': 'cycle_optimization_disabled'}
        
        # Prüfe Zyklen-Limit
        if self.cycles_today >= self.max_cycles_per_day:
            return 0.0, {
                'strategy': 'cycle_optimization_limit_reached',
                'cycles_today': self.cycles_today,
                'max_cycles': self.max_cycles_per_day
            }
        
        # Optimaler SOC-Bereich
        soc_min_optimal, soc_max_optimal = self.optimal_soc_range
        
        # Wenn SOC außerhalb des optimalen Bereichs, versuche zu korrigieren
        if soc < soc_min_optimal:
            # SOC zu niedrig - lade auf optimalen Bereich
            charge_power = min(power_kw * 0.5, (soc_min_optimal - soc) * capacity_kwh * 4)
            return -charge_power, {
                'strategy': 'cycle_optimization_soc_correction',
                'target_soc': soc_min_optimal,
                'current_soc': soc
            }
        elif soc > soc_max_optimal:
            # SOC zu hoch - entlade auf optimalen Bereich
            discharge_power = min(power_kw * 0.5, (soc - soc_max_optimal) * capacity_kwh * 4)
            return discharge_power, {
                'strategy': 'cycle_optimization_soc_correction',
                'target_soc': soc_max_optimal,
                'current_soc': soc
            }
        
        # SOC im optimalen Bereich - nur bei sehr guten Arbitrage-Möglichkeiten handeln
        if price_data and len(price_data) > 0:
            current_price = price_data[0]
            avg_price = sum(price_data) / len(price_data) if len(price_data) > 1 else current_price
            
            # Nur handeln, wenn Preis-Differenz sehr groß ist
            price_spread = abs(current_price - avg_price) / avg_price if avg_price > 0 else 0
            
            if price_spread > 0.3:  # 30% Preis-Differenz erforderlich
                if current_price < avg_price * 0.7 and soc < soc_max_optimal:
                    return -power_kw * 0.3, {'strategy': 'cycle_optimization_high_value_arbitrage'}
                elif current_price > avg_price * 1.3 and soc > soc_min_optimal:
                    return power_kw * 0.3, {'strategy': 'cycle_optimization_high_value_arbitrage'}
        
        return 0.0, {'strategy': 'cycle_optimization_idle', 'reason': 'soc_optimal'}


class ClusterBasedDispatch(OptimizationStrategy):
    """Cluster-Based Dispatch: Gruppenbasierte Lastverteilung"""
    
    def __init__(self, config: Dict):
        super().__init__('cluster_dispatch', config)
        self.num_clusters = config.get('num_clusters', 5)
        self.cluster_threshold = config.get('cluster_threshold', 0.15)  # 15% Preis-Differenz für Cluster
    
    def optimize(self, price_data: List[float], soc: float, capacity_kwh: float,
                power_kw: float, constraints: Dict) -> Tuple[float, Dict]:
        """
        Cluster-Based Dispatch: Gruppiert Preise und optimiert pro Cluster
        """
        if not self.enabled or len(price_data) < 3:
            return 0.0, {'strategy': 'cluster_dispatch_disabled'}
        
        # Erstelle Preis-Cluster
        clusters = self._create_price_clusters(price_data)
        
        # Bestimme aktuelles Cluster
        current_price = price_data[0]
        current_cluster = self._get_cluster_for_price(current_price, clusters)
        
        # Strategie basierend auf Cluster
        if current_cluster == 'low':
            # Niedriges Preis-Cluster - lade
            if soc < constraints.get('soc_max', 0.95):
                charge_power = min(power_kw * 0.7, (constraints.get('soc_max', 0.95) - soc) * capacity_kwh * 4)
                return -charge_power, {
                    'strategy': 'cluster_dispatch',
                    'cluster': 'low',
                    'action': 'charge'
                }
        elif current_cluster == 'high':
            # Hohes Preis-Cluster - entlade
            if soc > constraints.get('soc_min', 0.1):
                discharge_power = min(power_kw * 0.7, (soc - constraints.get('soc_min', 0.1)) * capacity_kwh * 4)
                return discharge_power, {
                    'strategy': 'cluster_dispatch',
                    'cluster': 'high',
                    'action': 'discharge'
                }
        
        return 0.0, {'strategy': 'cluster_dispatch_idle', 'cluster': current_cluster}
    
    def _create_price_clusters(self, price_data: List[float]) -> Dict[str, float]:
        """Erstellt Preis-Cluster"""
        if not price_data:
            return {'low': 0.0, 'medium': 0.0, 'high': 0.0}
        
        sorted_prices = sorted(price_data)
        n = len(sorted_prices)
        
        low_threshold = sorted_prices[int(n * 0.33)]
        high_threshold = sorted_prices[int(n * 0.67)]
        
        return {
            'low': low_threshold,
            'medium': (low_threshold + high_threshold) / 2,
            'high': high_threshold
        }
    
    def _get_cluster_for_price(self, price: float, clusters: Dict[str, float]) -> str:
        """Bestimmt Cluster für einen Preis"""
        if price <= clusters['low']:
            return 'low'
        elif price >= clusters['high']:
            return 'high'
        else:
            return 'medium'


class OptimizationManager:
    """Manager für alle Optimierungsstrategien"""
    
    def __init__(self, strategies: List[OptimizationStrategy]):
        self.strategies = strategies
        self.active_strategy = None
    
    def optimize_dispatch(self, price_data: List[float], soc: float, capacity_kwh: float,
                         power_kw: float, constraints: Dict, strategy_preference: str = None) -> Tuple[float, Dict]:
        """
        Optimiert Dispatch mit der besten verfügbaren Strategie
        
        Args:
            price_data: Preis-Daten
            soc: State of Charge
            capacity_kwh: Kapazität
            power_kw: Leistung
            constraints: Constraints
            strategy_preference: Bevorzugte Strategie ('pso', 'multi_objective', etc.)
            
        Returns:
            Tuple: (optimized_power_kw, optimization_info)
        """
        if strategy_preference:
            # Verwende bevorzugte Strategie
            for strategy in self.strategies:
                if strategy.strategy_type == strategy_preference and strategy.enabled:
                    return strategy.optimize(price_data, soc, capacity_kwh, power_kw, constraints)
        
        # Finde beste Strategie
        best_power = 0.0
        best_info = {}
        best_score = float('-inf')
        
        for strategy in self.strategies:
            if not strategy.enabled:
                continue
            
            try:
                power, info = strategy.optimize(price_data, soc, capacity_kwh, power_kw, constraints)
                
                # Bewerte Strategie
                score = self._score_strategy(power, info, price_data, soc)
                
                if score > best_score:
                    best_score = score
                    best_power = power
                    best_info = info
                    best_info['strategy_used'] = strategy.strategy_type
            except Exception as e:
                print(f"⚠️ Fehler bei Strategie {strategy.strategy_type}: {e}")
                continue
        
        return best_power, best_info
    
    def _score_strategy(self, power: float, info: Dict, price_data: List[float], soc: float) -> float:
        """Bewertet eine Strategie"""
        if not price_data:
            return 0.0
        
        # Basis-Score: Erlös-Potenzial
        revenue_score = info.get('revenue', 0.0) or info.get('revenue_estimate', 0.0)
        
        # Degradations-Penalty
        degradation_penalty = info.get('degradation_cost', 0.0) * 10
        
        # SOC-Balance-Bonus
        soc_balance = 1.0 - abs(soc - 0.5) * 2  # Bonus für SOC nahe 50%
        
        return revenue_score - degradation_penalty + soc_balance * 0.1

