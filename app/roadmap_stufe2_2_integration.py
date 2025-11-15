"""
Roadmap Stufe 2.2 Integration Helper
Optimierte Regelstrategien
"""

from app import db
from models import OptimizationStrategyConfig, OptimizationHistory
from app.optimization_strategies import (
    OptimizationManager,
    ParticleSwarmOptimization,
    MultiObjectiveOptimization,
    CycleOptimization,
    ClusterBasedDispatch
)
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
import json


def load_optimization_config(project_id: int) -> OptimizationStrategyConfig:
    """Lädt die Optimierungs-Konfiguration für ein Projekt"""
    config = OptimizationStrategyConfig.query.filter_by(project_id=project_id).first()
    
    if not config:
        # Erstelle Standard-Konfiguration
        config = OptimizationStrategyConfig(
            project_id=project_id,
            optimization_enabled=True,  # Standard: aktiviert
            preferred_strategy='multi_objective',
            pso_enabled=True,
            multi_objective_enabled=True,
            cycle_optimization_enabled=True,
            cluster_dispatch_enabled=True
        )
        db.session.add(config)
        db.session.commit()
    
    return config


def create_optimization_manager(project_id: int) -> OptimizationManager:
    """Erstellt einen OptimizationManager mit den Projekt-spezifischen Strategien"""
    config = load_optimization_config(project_id)
    
    strategies = []
    
    # PSO
    if config.pso_enabled:
        strategies.append(ParticleSwarmOptimization({
            'enabled': config.pso_enabled,
            'swarm_size': config.pso_swarm_size,
            'max_iterations': config.pso_max_iterations,
            'inertia_weight': config.pso_inertia_weight,
            'cognitive_weight': config.pso_cognitive_weight,
            'social_weight': config.pso_social_weight
        }))
    
    # Multi-Objective
    if config.multi_objective_enabled:
        strategies.append(MultiObjectiveOptimization({
            'enabled': config.multi_objective_enabled,
            'revenue_weight': config.revenue_weight,
            'degradation_weight': config.degradation_weight,
            'cycle_cost_eur_per_cycle': config.cycle_cost_eur_per_cycle
        }))
    
    # Cycle Optimization
    if config.cycle_optimization_enabled:
        # Lade aktuelle Zyklen für heute
        cycles_today = get_cycles_today(project_id)
        
        strategies.append(CycleOptimization({
            'enabled': config.cycle_optimization_enabled,
            'max_cycles_per_day': config.max_cycles_per_day,
            'optimal_soc_range': (config.optimal_soc_min, config.optimal_soc_max),
            'deep_discharge_penalty': config.deep_discharge_penalty,
            'cycles_today': cycles_today
        }))
    
    # Cluster-Based Dispatch
    if config.cluster_dispatch_enabled:
        strategies.append(ClusterBasedDispatch({
            'enabled': config.cluster_dispatch_enabled,
            'num_clusters': config.num_clusters,
            'cluster_threshold': config.cluster_threshold
        }))
    
    return OptimizationManager(strategies)


def optimize_dispatch_for_period(
    project_id: int,
    price_data: List[float],
    soc: float,
    capacity_kwh: float,
    power_kw: float,
    constraints: Dict,
    timestamp: datetime,
    simulation_id: Optional[int] = None
) -> Tuple[float, Dict]:
    """
    Optimiert Dispatch für eine Periode
    
    Args:
        project_id: Projekt-ID
        price_data: Preis-Daten für den Zeitraum
        soc: Aktueller State of Charge (0-1)
        capacity_kwh: Batterie-Kapazität in kWh
        power_kw: Batterie-Leistung in kW
        constraints: Constraints (SOC_min, SOC_max, ramp_rate, etc.)
        timestamp: Zeitstempel
        simulation_id: Optional: Simulation-ID
        
    Returns:
        Tuple: (optimized_power_kw, optimization_info)
    """
    config = load_optimization_config(project_id)
    
    # Prüfe ob Optimierung aktiviert ist
    if not config.optimization_enabled:
        # Fallback: Einfache Preis-basierte Strategie
        return simple_price_based_dispatch(price_data[0] if price_data else 100.0, soc, capacity_kwh, power_kw, constraints), {
            'strategy': 'simple',
            'optimization_enabled': False
        }
    
    # Erstelle OptimizationManager
    manager = create_optimization_manager(project_id)
    
    # Optimiere Dispatch
    optimized_power, optimization_info = manager.optimize_dispatch(
        price_data=price_data,
        soc=soc,
        capacity_kwh=capacity_kwh,
        power_kw=power_kw,
        constraints=constraints,
        strategy_preference=config.preferred_strategy if config.preferred_strategy else None
    )
    
    # Berechne SOC nach Optimierung
    time_interval_hours = 0.25  # 15 Minuten
    if optimized_power < 0:  # Laden
        energy_change_kwh = abs(optimized_power) * time_interval_hours * 0.85  # 85% Effizienz
        soc_after = min(1.0, soc + (energy_change_kwh / capacity_kwh))
    elif optimized_power > 0:  # Entladen
        energy_change_kwh = optimized_power * time_interval_hours * 0.85
        soc_after = max(0.0, soc - (energy_change_kwh / capacity_kwh))
    else:
        soc_after = soc
    
    # Speichere Optimierungs-Historie
    try:
        history = OptimizationHistory(
            project_id=project_id,
            simulation_id=simulation_id,
            timestamp=timestamp,
            strategy_used=optimization_info.get('strategy_used', optimization_info.get('strategy', 'unknown')),
            price_eur_mwh=price_data[0] if price_data else 100.0,
            soc_before=soc,
            capacity_kwh=capacity_kwh,
            power_kw=power_kw,
            optimized_power_kw=optimized_power,
            soc_after=soc_after,
            revenue_estimate_eur=optimization_info.get('revenue', optimization_info.get('revenue_estimate', 0.0)),
            degradation_cost_eur=optimization_info.get('degradation_cost', 0.0),
            net_benefit_eur=optimization_info.get('net_benefit', 0.0),
            cycles_today=get_cycles_today(project_id),
            constraints_applied=json.dumps(constraints),
            optimization_info=json.dumps(optimization_info)
        )
        db.session.add(history)
        db.session.commit()
    except Exception as e:
        print(f"⚠️ Fehler beim Speichern der Optimierungs-Historie: {e}")
        db.session.rollback()
    
    return optimized_power, optimization_info


def simple_price_based_dispatch(price: float, soc: float, capacity_kwh: float,
                                power_kw: float, constraints: Dict) -> float:
    """Einfache Preis-basierte Dispatch-Strategie (Fallback)"""
    avg_price = 100.0  # Fallback-Durchschnittspreis
    
    if price < avg_price * 0.8 and soc < constraints.get('soc_max', 0.95):
        return -power_kw * 0.5  # Lade bei niedrigen Preisen
    elif price > avg_price * 1.2 and soc > constraints.get('soc_min', 0.1):
        return power_kw * 0.5  # Entlade bei hohen Preisen
    
    return 0.0  # Idle


def get_cycles_today(project_id: int) -> float:
    """Gibt die Anzahl der Zyklen für heute zurück"""
    today = datetime.now().date()
    
    try:
        # Zähle Zyklen aus der Optimierungs-Historie
        cycles = OptimizationHistory.query.filter(
            OptimizationHistory.project_id == project_id,
            db.func.date(OptimizationHistory.timestamp) == today
        ).count()
        
        # Vereinfacht: Jede Lade-/Entlade-Aktion zählt als Teilzyklus
        return cycles * 0.1  # 10 Aktionen = 1 Zyklus
    except Exception as e:
        print(f"⚠️ Fehler beim Abrufen der Zyklen: {e}")
        return 0.0


def get_optimization_statistics(project_id: int, days: int = 30) -> Dict[str, Any]:
    """
    Gibt Optimierungs-Statistiken zurück
    
    Args:
        project_id: Projekt-ID
        days: Anzahl der Tage für Statistik
        
    Returns:
        Dict mit Statistiken
    """
    from datetime import timedelta
    
    start_date = datetime.now() - timedelta(days=days)
    
    try:
        history = OptimizationHistory.query.filter(
            OptimizationHistory.project_id == project_id,
            OptimizationHistory.timestamp >= start_date
        ).all()
        
        if not history:
            return {
                'total_decisions': 0,
                'strategies_used': {},
                'avg_revenue_estimate': 0.0,
                'avg_degradation_cost': 0.0,
                'avg_net_benefit': 0.0,
                'total_cycles': 0.0
            }
        
        strategies_used = {}
        total_revenue = 0.0
        total_degradation_cost = 0.0
        total_net_benefit = 0.0
        total_cycles = 0.0
        
        for h in history:
            # Strategien zählen
            strategy = h.strategy_used or 'unknown'
            strategies_used[strategy] = strategies_used.get(strategy, 0) + 1
            
            # Summen
            total_revenue += h.revenue_estimate_eur or 0.0
            total_degradation_cost += h.degradation_cost_eur or 0.0
            total_net_benefit += h.net_benefit_eur or 0.0
            total_cycles += h.cycles_today or 0.0
        
        count = len(history)
        
        return {
            'total_decisions': count,
            'strategies_used': strategies_used,
            'avg_revenue_estimate': total_revenue / count if count > 0 else 0.0,
            'avg_degradation_cost': total_degradation_cost / count if count > 0 else 0.0,
            'avg_net_benefit': total_net_benefit / count if count > 0 else 0.0,
            'total_cycles': total_cycles,
            'avg_cycles_per_day': total_cycles / days if days > 0 else 0.0
        }
    except Exception as e:
        print(f"⚠️ Fehler beim Abrufen der Optimierungs-Statistiken: {e}")
        return {
            'total_decisions': 0,
            'strategies_used': {},
            'avg_revenue_estimate': 0.0,
            'avg_degradation_cost': 0.0,
            'avg_net_benefit': 0.0,
            'total_cycles': 0.0
        }

