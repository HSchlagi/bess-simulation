#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Netzrestriktionen-Modul für BESS-Simulation
Implementiert Ramp-Rate Limits, Exportlimits, 100-h-Regel, etc.
"""

from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class NetworkRestrictions:
    """Datenmodell für Netzrestriktionen"""
    max_discharge_kw: float = 0.0          # Max. Entladeleistung (kW)
    max_charge_kw: float = 0.0             # Max. Ladeleistung (kW)
    ramp_rate_percent: float = 10.0         # Max. % Leistungsänderung pro Minute
    export_limit_kw: float = 0.0           # Exportlimit am Netzanschlusspunkt (kW)
    network_level: str = "NE5"             # Netzebene (NE5/NE6/NE7)
    eeg_100h_rule_enabled: bool = False     # 100-h-Regel aktiviert (EEG/DE)
    eeg_100h_hours_per_year: int = 100     # Max. Einspeisestunden pro Jahr
    eeg_100h_used_hours: int = 0           # Bereits genutzte Stunden
    hull_curve_enabled: bool = False        # Hüllkurvenregelung aktiviert
    hull_curve_data: Optional[Dict] = None # Hüllkurven-Daten (JSON)
    
    def __post_init__(self):
        """Validiert die Eingabewerte"""
        if self.ramp_rate_percent <= 0 or self.ramp_rate_percent > 100:
            raise ValueError("Ramp-Rate muss zwischen 0 und 100% liegen")
        if self.max_discharge_kw < 0 or self.max_charge_kw < 0:
            raise ValueError("Leistungswerte müssen >= 0 sein")


class NetworkRestrictionsManager:
    """Manager für Netzrestriktionen"""
    
    def __init__(self, restrictions: NetworkRestrictions):
        self.restrictions = restrictions
        self.previous_power_kw = 0.0  # Vorherige Leistung für Ramp-Rate
        self.ramp_rate_kw_per_min = 0.0  # Berechnete Ramp-Rate in kW/min
        
    def calculate_ramp_rate_limit(self, current_power_kw: float, 
                                  time_interval_minutes: float = 15.0) -> float:
        """
        Berechnet die maximale Leistungsänderung basierend auf Ramp-Rate
        
        Args:
            current_power_kw: Aktuelle Leistung (kW)
            time_interval_minutes: Zeitintervall in Minuten (Standard: 15 Min)
            
        Returns:
            Maximale erlaubte Leistungsänderung (kW)
        """
        # Ramp-Rate in kW/min umrechnen
        # Annahme: Ramp-Rate bezieht sich auf die maximale Leistung
        max_power = max(abs(self.restrictions.max_charge_kw), 
                       abs(self.restrictions.max_discharge_kw))
        
        if max_power == 0:
            return 0.0
        
        # Ramp-Rate als % der Maximalleistung pro Minute
        ramp_rate_kw_per_min = max_power * (self.restrictions.ramp_rate_percent / 100.0)
        
        # Maximale Änderung für das Zeitintervall
        max_change_kw = ramp_rate_kw_per_min * time_interval_minutes
        
        return max_change_kw
    
    def apply_restrictions(self, planned_power_kw: float, 
                          time_interval_minutes: float = 15.0,
                          timestamp: Optional[datetime] = None) -> Tuple[float, Dict]:
        """
        Wendet alle Netzrestriktionen auf die geplante Leistung an
        
        Args:
            planned_power_kw: Geplante Leistung (kW, positiv = Entladung, negativ = Ladung)
            time_interval_minutes: Zeitintervall in Minuten
            timestamp: Zeitstempel für 100-h-Regel
            
        Returns:
            Tuple: (tatsächliche_leistung_kw, restrictions_info)
        """
        actual_power = planned_power_kw
        restrictions_applied = []
        revenue_loss_kwh = 0.0
        
        # 1. Max. Lade-/Entladeleistung
        if actual_power > 0:  # Entladung
            if actual_power > self.restrictions.max_discharge_kw:
                restrictions_applied.append("max_discharge")
                actual_power = min(actual_power, self.restrictions.max_discharge_kw)
        else:  # Ladung (negativ)
            if abs(actual_power) > self.restrictions.max_charge_kw:
                restrictions_applied.append("max_charge")
                actual_power = -min(abs(actual_power), self.restrictions.max_charge_kw)
        
        # 2. Ramp-Rate Limit
        max_change = self.calculate_ramp_rate_limit(actual_power, time_interval_minutes)
        power_change = actual_power - self.previous_power_kw
        
        if abs(power_change) > max_change:
            restrictions_applied.append("ramp_rate")
            if power_change > 0:
                actual_power = self.previous_power_kw + max_change
            else:
                actual_power = self.previous_power_kw - max_change
        
        # 3. Exportlimit (nur bei Entladung/Einspeisung)
        if actual_power > 0 and actual_power > self.restrictions.export_limit_kw:
            restrictions_applied.append("export_limit")
            actual_power = min(actual_power, self.restrictions.export_limit_kw)
        
        # 4. 100-h-Regel (EEG/DE) - nur bei Einspeisung
        if (actual_power > 0 and 
            self.restrictions.eeg_100h_rule_enabled and
            timestamp):
            # Prüfe ob noch Stunden verfügbar sind
            if self.restrictions.eeg_100h_used_hours >= self.restrictions.eeg_100h_hours_per_year:
                restrictions_applied.append("eeg_100h_rule")
                actual_power = 0.0  # Keine Einspeisung mehr erlaubt
        
        # 5. Hüllkurvenregelung (vereinfacht)
        if self.restrictions.hull_curve_enabled and self.restrictions.hull_curve_data:
            # Hier könnte eine komplexere Hüllkurven-Logik implementiert werden
            pass
        
        # Berechne Erlösverlust
        power_loss_kw = abs(planned_power_kw - actual_power)
        revenue_loss_kwh = power_loss_kw * (time_interval_minutes / 60.0)
        
        # Aktualisiere vorherige Leistung
        self.previous_power_kw = actual_power
        
        # Aktualisiere 100-h-Regel Stunden (wenn Einspeisung)
        if actual_power > 0 and timestamp:
            # Annahme: Wenn Leistung > 0, wird eine Stunde genutzt
            # In Realität müsste dies über das gesamte Jahr getrackt werden
            pass
        
        restrictions_info = {
            'planned_power_kw': planned_power_kw,
            'actual_power_kw': actual_power,
            'power_loss_kw': power_loss_kw,
            'revenue_loss_kwh': revenue_loss_kwh,
            'restrictions_applied': restrictions_applied,
            'timestamp': timestamp or datetime.now()
        }
        
        return actual_power, restrictions_info
    
    def reset(self):
        """Setzt den Manager zurück (z.B. für neue Simulation)"""
        self.previous_power_kw = 0.0
    
    def get_revenue_loss_summary(self, restrictions_history: list) -> Dict:
        """
        Berechnet Zusammenfassung der Erlösverluste
        
        Args:
            restrictions_history: Liste von restrictions_info Dictionaries
            
        Returns:
            Zusammenfassung mit Gesamtverlusten
        """
        total_revenue_loss_kwh = sum(r.get('revenue_loss_kwh', 0) for r in restrictions_history)
        total_power_loss_kw = sum(r.get('power_loss_kw', 0) for r in restrictions_history)
        
        restrictions_count = {}
        for r in restrictions_history:
            for restriction in r.get('restrictions_applied', []):
                restrictions_count[restriction] = restrictions_count.get(restriction, 0) + 1
        
        return {
            'total_revenue_loss_kwh': total_revenue_loss_kwh,
            'total_power_loss_kw': total_power_loss_kw,
            'restrictions_count': restrictions_count,
            'total_periods': len(restrictions_history),
            'periods_with_restrictions': sum(1 for r in restrictions_history 
                                            if r.get('restrictions_applied'))
        }


def create_default_restrictions(project_power_kw: float, 
                               network_level: str = "NE5") -> NetworkRestrictions:
    """
    Erstellt Standard-Netzrestriktionen basierend auf Projektparametern
    
    Args:
        project_power_kw: Projektleistung in kW
        network_level: Netzebene (NE5/NE6/NE7)
        
    Returns:
        NetworkRestrictions-Objekt mit Standardwerten
    """
    # Standardwerte basierend auf Netzebene
    if network_level == "NE5":
        # Niederspannung: Weniger restriktiv
        max_export = project_power_kw * 1.0  # 100% der Leistung
        ramp_rate = 20.0  # 20% pro Minute
    elif network_level == "NE6":
        # Mittelspannung: Mittlere Restriktionen
        max_export = project_power_kw * 0.8  # 80% der Leistung
        ramp_rate = 15.0  # 15% pro Minute
    elif network_level == "NE7":
        # Hochspannung: Strengere Restriktionen
        max_export = project_power_kw * 0.6  # 60% der Leistung
        ramp_rate = 10.0  # 10% pro Minute
    else:
        # Fallback
        max_export = project_power_kw * 0.8
        ramp_rate = 10.0
    
    return NetworkRestrictions(
        max_discharge_kw=project_power_kw,
        max_charge_kw=project_power_kw,
        ramp_rate_percent=ramp_rate,
        export_limit_kw=max_export,
        network_level=network_level,
        eeg_100h_rule_enabled=False,
        hull_curve_enabled=False
    )








