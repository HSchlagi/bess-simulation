#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batterie-Degradation-Modell für BESS-Simulation
Implementiert Cycle Count, DoD-Abhängige Alterung, Temperaturfaktor, SoH Tracking
"""

from typing import Dict, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import math


@dataclass
class DegradationModel:
    """Datenmodell für Batterie-Degradation"""
    initial_capacity_kwh: float = 1000.0      # Anfangskapazität (kWh)
    current_capacity_kwh: float = 1000.0     # Aktuelle Kapazität (kWh)
    cycle_number: int = 0                     # Anzahl der Zyklen
    dod: float = 0.0                          # Depth of Discharge (0-1)
    efficiency: float = 0.85                  # Aktuelle Effizienz (0-1)
    temperature: float = 25.0                  # Betriebstemperatur (°C)
    temperature_factor: float = 1.0           # Temperaturfaktor für Degradation
    state_of_health: float = 100.0             # State of Health (0-100%)
    degradation_rate_per_cycle: float = 0.0001 # Degradationsrate pro Zyklus
    dod_factor: float = 1.0                   # DoD-Faktor für Degradation
    calendar_aging_rate: float = 0.02          # Kalender-Alterung pro Jahr (2%)
    is_second_life: bool = False               # Second-Life-Batterie
    second_life_start_capacity: float = 0.85    # Startkapazität für Second-Life (85%)
    
    def __post_init__(self):
        """Initialisiert das Modell"""
        if self.is_second_life:
            # Second-Life startet mit reduzierter Kapazität
            self.current_capacity_kwh = self.initial_capacity_kwh * self.second_life_start_capacity
            self.state_of_health = self.second_life_start_capacity * 100.0
        else:
            self.current_capacity_kwh = self.initial_capacity_kwh
            self.state_of_health = 100.0
    
    def calculate_dod_factor(self, dod: float) -> float:
        """
        Berechnet DoD-Faktor für Degradation
        
        Tiefere Entladung = höhere Degradation
        Formel: dod_factor = 1 + (dod - 0.5) * 2
        """
        # Normalisiert DoD auf 0-1
        dod_normalized = max(0.0, min(1.0, dod))
        
        # DoD-Faktor: Tiefe Entladung (>0.8) führt zu höherer Degradation
        if dod_normalized < 0.5:
            dod_factor = 0.5 + dod_normalized  # 0.5 - 1.0
        else:
            dod_factor = 0.5 + (dod_normalized - 0.5) * 2.0  # 1.0 - 2.0
        
        return dod_factor
    
    def calculate_temperature_factor(self, temperature: float) -> float:
        """
        Berechnet Temperaturfaktor für Degradation
        
        Optimal: 20-30°C
        Zu heiß (>40°C) oder zu kalt (<0°C) erhöht Degradation
        """
        if 20.0 <= temperature <= 30.0:
            # Optimaler Bereich
            return 1.0
        elif temperature < 0.0:
            # Zu kalt: Erhöhte Degradation
            return 1.0 + (abs(temperature) / 20.0) * 0.5
        elif temperature > 40.0:
            # Zu heiß: Erhöhte Degradation
            return 1.0 + ((temperature - 40.0) / 20.0) * 0.5
        else:
            # Leichte Abweichung
            return 1.0 + abs(temperature - 25.0) / 100.0
    
    def calculate_cycle_degradation(self, dod: float, temperature: float) -> float:
        """
        Berechnet Kapazitätsverlust durch einen Zyklus
        
        Args:
            dod: Depth of Discharge (0-1)
            temperature: Betriebstemperatur (°C)
            
        Returns:
            Kapazitätsverlust in kWh
        """
        # DoD-Faktor
        self.dod_factor = self.calculate_dod_factor(dod)
        
        # Temperaturfaktor
        self.temperature_factor = self.calculate_temperature_factor(temperature)
        
        # Basis-Degradation pro Zyklus
        base_degradation = self.degradation_rate_per_cycle * self.initial_capacity_kwh
        
        # Angepasste Degradation
        cycle_degradation = base_degradation * self.dod_factor * self.temperature_factor
        
        # Second-Life hat höhere Degradation
        if self.is_second_life:
            cycle_degradation *= 1.5  # 50% höhere Degradation
        
        return cycle_degradation
    
    def add_cycle(self, dod: float, temperature: float = 25.0) -> Dict:
        """
        Fügt einen Zyklus hinzu und berechnet Degradation
        
        Args:
            dod: Depth of Discharge (0-1)
            temperature: Betriebstemperatur (°C)
            
        Returns:
            Dictionary mit Degradationsinformationen
        """
        self.cycle_number += 1
        self.dod = dod
        self.temperature = temperature
        
        # Berechne Degradation
        capacity_loss = self.calculate_cycle_degradation(dod, temperature)
        
        # Aktualisiere Kapazität
        self.current_capacity_kwh = max(0.0, self.current_capacity_kwh - capacity_loss)
        
        # Aktualisiere State of Health
        self.state_of_health = (self.current_capacity_kwh / self.initial_capacity_kwh) * 100.0
        
        # Aktualisiere Effizienz (leicht abnehmend mit Degradation)
        efficiency_loss = (100.0 - self.state_of_health) / 1000.0  # Max. 10% Effizienzverlust
        self.efficiency = max(0.7, 0.85 - efficiency_loss)
        
        return {
            'cycle_number': self.cycle_number,
            'capacity_loss_kwh': capacity_loss,
            'current_capacity_kwh': self.current_capacity_kwh,
            'state_of_health': self.state_of_health,
            'efficiency': self.efficiency,
            'dod_factor': self.dod_factor,
            'temperature_factor': self.temperature_factor
        }
    
    def add_calendar_aging(self, years: float) -> Dict:
        """
        Fügt Kalender-Alterung hinzu (unabhängig von Zyklen)
        
        Args:
            years: Anzahl der Jahre
            
        Returns:
            Dictionary mit Alterungsinformationen
        """
        # Kalender-Alterung (exponentiell)
        calendar_loss_factor = 1.0 - (1.0 - self.calendar_aging_rate) ** years
        
        # Kapazitätsverlust durch Kalender-Alterung
        capacity_loss = self.initial_capacity_kwh * calendar_loss_factor
        
        # Aktualisiere Kapazität (nur wenn noch nicht durch Zyklen reduziert)
        if self.current_capacity_kwh > self.initial_capacity_kwh * (1.0 - calendar_loss_factor):
            self.current_capacity_kwh = self.initial_capacity_kwh * (1.0 - calendar_loss_factor)
        
        # Aktualisiere State of Health
        self.state_of_health = (self.current_capacity_kwh / self.initial_capacity_kwh) * 100.0
        
        return {
            'years': years,
            'capacity_loss_kwh': capacity_loss,
            'current_capacity_kwh': self.current_capacity_kwh,
            'state_of_health': self.state_of_health
        }
    
    def get_lifetime_estimate(self, target_soh: float = 80.0) -> Dict:
        """
        Schätzt die verbleibende Lebensdauer bis zum Ziel-SoH
        
        Args:
            target_soh: Ziel State of Health (Standard: 80%)
            
        Returns:
            Dictionary mit Lebensdauer-Schätzung
        """
        if self.state_of_health <= target_soh:
            return {
                'remaining_cycles': 0,
                'remaining_years': 0.0,
                'status': 'end_of_life_reached'
            }
        
        # Verbleibende Kapazität bis Ziel
        remaining_capacity_loss = (self.state_of_health - target_soh) / 100.0 * self.initial_capacity_kwh
        
        # Schätzung basierend auf durchschnittlicher Degradation
        avg_degradation_per_cycle = self.degradation_rate_per_cycle * self.initial_capacity_kwh * 1.5
        remaining_cycles = int(remaining_capacity_loss / avg_degradation_per_cycle) if avg_degradation_per_cycle > 0 else 0
        
        # Schätzung in Jahren (basierend auf durchschnittlichen Zyklen pro Jahr)
        avg_cycles_per_year = 365 * 2.0  # Annahme: 2 Zyklen pro Tag
        remaining_years = remaining_cycles / avg_cycles_per_year if avg_cycles_per_year > 0 else 0.0
        
        return {
            'remaining_cycles': remaining_cycles,
            'remaining_years': remaining_years,
            'current_soh': self.state_of_health,
            'target_soh': target_soh,
            'status': 'operational'
        }
    
    def get_degradation_summary(self) -> Dict:
        """Gibt eine Zusammenfassung der Degradation zurück"""
        return {
            'initial_capacity_kwh': self.initial_capacity_kwh,
            'current_capacity_kwh': self.current_capacity_kwh,
            'capacity_loss_kwh': self.initial_capacity_kwh - self.current_capacity_kwh,
            'capacity_loss_percent': ((self.initial_capacity_kwh - self.current_capacity_kwh) / self.initial_capacity_kwh) * 100.0,
            'state_of_health': self.state_of_health,
            'cycle_number': self.cycle_number,
            'efficiency': self.efficiency,
            'is_second_life': self.is_second_life,
            'lifetime_estimate': self.get_lifetime_estimate()
        }


def create_standard_degradation_model(initial_capacity_kwh: float,
                                     is_second_life: bool = False) -> DegradationModel:
    """
    Erstellt ein Standard-Degradationsmodell
    
    Args:
        initial_capacity_kwh: Anfangskapazität in kWh
        is_second_life: Ob es sich um eine Second-Life-Batterie handelt
        
    Returns:
        DegradationModel-Objekt
    """
    return DegradationModel(
        initial_capacity_kwh=initial_capacity_kwh,
        is_second_life=is_second_life,
        degradation_rate_per_cycle=0.0001,  # 0.01% pro Zyklus
        calendar_aging_rate=0.02  # 2% pro Jahr
    )







