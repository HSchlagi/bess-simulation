#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Roadmap Stufe 1 Integration Helper
=================================
Hilfsfunktionen für die Integration von Netzrestriktionen, Degradation und Second-Life
"""

from typing import Dict, Optional, Tuple
from datetime import datetime
from app.network_restrictions import NetworkRestrictions, NetworkRestrictionsManager, create_default_restrictions
from app.degradation_model import DegradationModel, create_standard_degradation_model
from models import NetworkRestrictions as NetworkRestrictionsModel, BatteryDegradationAdvanced, SecondLifeConfig, Project


def load_network_restrictions(project_id: int, project_power_kw: float) -> NetworkRestrictionsManager:
    """
    Lädt Netzrestriktionen aus der Datenbank oder erstellt Standardwerte
    
    Args:
        project_id: Projekt-ID
        project_power_kw: Projektleistung in kW
        
    Returns:
        NetworkRestrictionsManager
    """
    restrictions_model = NetworkRestrictionsModel.query.filter_by(project_id=project_id).first()
    
    if restrictions_model:
        restrictions = NetworkRestrictions(
            max_discharge_kw=restrictions_model.max_discharge_kw or project_power_kw,
            max_charge_kw=restrictions_model.max_charge_kw or project_power_kw,
            ramp_rate_percent=restrictions_model.ramp_rate_percent or 10.0,
            export_limit_kw=restrictions_model.export_limit_kw or (project_power_kw * 0.8),
            network_level=restrictions_model.network_level or 'NE5',
            eeg_100h_rule_enabled=restrictions_model.eeg_100h_rule_enabled or False,
            eeg_100h_hours_per_year=restrictions_model.eeg_100h_hours_per_year or 100,
            eeg_100h_used_hours=restrictions_model.eeg_100h_used_hours or 0,
            hull_curve_enabled=restrictions_model.hull_curve_enabled or False,
            hull_curve_data=restrictions_model.hull_curve_data
        )
    else:
        # Standardwerte erstellen
        restrictions = create_default_restrictions(project_power_kw)
    
    return NetworkRestrictionsManager(restrictions)


def load_degradation_model(project_id: int, initial_capacity_kwh: float) -> DegradationModel:
    """
    Lädt Degradationsmodell aus der Datenbank oder erstellt Standardwerte
    
    Args:
        project_id: Projekt-ID
        initial_capacity_kwh: Anfangskapazität in kWh
        
    Returns:
        DegradationModel
    """
    degradation_model = BatteryDegradationAdvanced.query.filter_by(project_id=project_id).first()
    second_life_config = SecondLifeConfig.query.filter_by(project_id=project_id).first()
    
    is_second_life = second_life_config.is_second_life if second_life_config else False
    
    if degradation_model:
        model = DegradationModel(
            initial_capacity_kwh=degradation_model.initial_capacity_kwh or initial_capacity_kwh,
            current_capacity_kwh=degradation_model.current_capacity_kwh or initial_capacity_kwh,
            cycle_number=degradation_model.cycle_number or 0,
            dod=degradation_model.dod or 0.0,
            efficiency=degradation_model.efficiency or 0.85,
            temperature=degradation_model.temperature or 25.0,
            state_of_health=degradation_model.state_of_health or 100.0,
            degradation_rate_per_cycle=degradation_model.degradation_rate_per_cycle or 0.0001,
            calendar_aging_rate=degradation_model.calendar_aging_rate or 0.02,
            is_second_life=is_second_life,
            second_life_start_capacity=second_life_config.start_capacity_percent / 100.0 if second_life_config else 0.85
        )
    else:
        # Standardwerte erstellen
        model = create_standard_degradation_model(initial_capacity_kwh, is_second_life)
    
    return model


def apply_restrictions_to_power(restrictions_manager: NetworkRestrictionsManager,
                                planned_power_kw: float,
                                timestamp: Optional[datetime] = None,
                                time_interval_minutes: float = 15.0) -> Tuple[float, Dict]:
    """
    Wendet Netzrestriktionen auf geplante Leistung an
    
    Args:
        restrictions_manager: NetworkRestrictionsManager
        planned_power_kw: Geplante Leistung (kW, positiv = Entladung)
        timestamp: Zeitstempel für 100-h-Regel
        time_interval_minutes: Zeitintervall in Minuten
        
    Returns:
        Tuple: (tatsächliche_leistung_kw, restrictions_info)
    """
    return restrictions_manager.apply_restrictions(
        planned_power_kw,
        time_interval_minutes,
        timestamp
    )


def calculate_degradation_for_cycle(degradation_model: DegradationModel,
                                    dod: float,
                                    temperature: float = 25.0) -> Dict:
    """
    Berechnet Degradation für einen Zyklus
    
    Args:
        degradation_model: DegradationModel
        dod: Depth of Discharge (0-1)
        temperature: Betriebstemperatur (°C)
        
    Returns:
        Dictionary mit Degradationsinformationen
    """
    return degradation_model.add_cycle(dod, temperature)


def calculate_degradation_for_year(degradation_model: DegradationModel,
                                  cycles_per_year: float,
                                  avg_dod: float = 0.8,
                                  temperature: float = 25.0) -> Dict:
    """
    Berechnet Degradation für ein Jahr
    
    Args:
        degradation_model: DegradationModel
        cycles_per_year: Anzahl Zyklen pro Jahr
        avg_dod: Durchschnittliche DoD (0-1)
        temperature: Betriebstemperatur (°C)
        
    Returns:
        Dictionary mit Jahres-Degradationsinformationen
    """
    # Kalender-Alterung hinzufügen
    calendar_aging = degradation_model.add_calendar_aging(1.0)
    
    # Zyklen-basierte Degradation
    cycle_degradations = []
    for _ in range(int(cycles_per_year)):
        cycle_info = degradation_model.add_cycle(avg_dod, temperature)
        cycle_degradations.append(cycle_info)
    
    # Zusammenfassung
    total_capacity_loss = sum(c['capacity_loss_kwh'] for c in cycle_degradations)
    total_capacity_loss += calendar_aging.get('capacity_loss_kwh', 0)
    
    return {
        'year': datetime.now().year,
        'cycles': int(cycles_per_year),
        'total_capacity_loss_kwh': total_capacity_loss,
        'current_capacity_kwh': degradation_model.current_capacity_kwh,
        'state_of_health': degradation_model.state_of_health,
        'efficiency': degradation_model.efficiency,
        'calendar_aging': calendar_aging
    }


def get_second_life_cost_reduction(project_id: int) -> float:
    """
    Gibt Kostenvorteil für Second-Life-Batterien zurück
    
    Args:
        project_id: Projekt-ID
        
    Returns:
        Kostenvorteil in Prozent (0-100)
    """
    second_life_config = SecondLifeConfig.query.filter_by(project_id=project_id).first()
    
    if second_life_config and second_life_config.is_second_life:
        return second_life_config.cost_reduction_percent or 50.0
    
    return 0.0


def calculate_revenue_loss_from_restrictions(restrictions_history: list,
                                            price_eur_mwh: float) -> Dict:
    """
    Berechnet Erlösverlust durch Netzrestriktionen
    
    Args:
        restrictions_history: Liste von restrictions_info Dictionaries
        price_eur_mwh: Preis in EUR/MWh
        
    Returns:
        Dictionary mit Erlösverlust-Informationen
    """
    total_revenue_loss_kwh = sum(r.get('revenue_loss_kwh', 0) for r in restrictions_history)
    total_revenue_loss_eur = total_revenue_loss_kwh * (price_eur_mwh / 1000.0)  # kWh zu MWh
    
    restrictions_count = {}
    for r in restrictions_history:
        for restriction in r.get('restrictions_applied', []):
            restrictions_count[restriction] = restrictions_count.get(restriction, 0) + 1
    
    return {
        'total_revenue_loss_kwh': total_revenue_loss_kwh,
        'total_revenue_loss_eur': total_revenue_loss_eur,
        'total_power_loss_kw': sum(r.get('power_loss_kw', 0) for r in restrictions_history),
        'restrictions_count': restrictions_count,
        'periods_with_restrictions': sum(1 for r in restrictions_history 
                                        if r.get('restrictions_applied'))
    }

