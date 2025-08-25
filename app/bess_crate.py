#!/usr/bin/env python3
"""
C-Rate Integration für BESS-Simulation
======================================

Backend-Modul für C-Rate Berechnungen und Derating-Faktoren
"""

import json
from dataclasses import dataclass
from typing import Optional, Tuple, Dict, List
from models import BatteryConfig, Project
from app import db

@dataclass
class CRConfig:
    """C-Rate Konfiguration"""
    E_nom_kWh: float
    C_chg_rate: float
    C_dis_rate: float
    derating_enable: bool = True
    soc_derate_charge: Optional[List[Tuple[float, float, float]]] = None
    soc_derate_discharge: Optional[List[Tuple[float, float, float]]] = None
    temp_derate_charge: Optional[List[Tuple[float, float, float]]] = None
    temp_derate_discharge: Optional[List[Tuple[float, float, float]]] = None

def _piecewise_factor(x: Optional[float], table: Optional[List[Tuple[float, float, float]]], default: float = 1.0) -> float:
    """Berechnet Derating-Faktor basierend auf stückweise definierter Tabelle"""
    if x is None or not table:
        return default
    for lo, hi, fac in table:
        if lo <= x < hi:
            return float(fac)
    return default

def derate_factors(SoC: Optional[float], temp_C: Optional[float], cfg: CRConfig) -> Tuple[float, float]:
    """Berechnet Derating-Faktoren für Laden und Entladen"""
    if not cfg.derating_enable:
        return 1.0, 1.0
    
    f_soc_chg = _piecewise_factor(SoC, cfg.soc_derate_charge, 1.0)
    f_soc_dis = _piecewise_factor(SoC, cfg.soc_derate_discharge, 1.0)
    f_t_chg = _piecewise_factor(temp_C, cfg.temp_derate_charge, 1.0)
    f_t_dis = _piecewise_factor(temp_C, cfg.temp_derate_discharge, 1.0)
    
    return f_soc_chg * f_t_chg, f_soc_dis * f_t_dis

def compute_power_bounds(E_nom_kWh: float,
                        C_chg_rate: float,
                        C_dis_rate: float,
                        SoC: Optional[float] = None,
                        temp_C: Optional[float] = None,
                        cfg: Optional[CRConfig] = None) -> Dict[str, float]:
    """Berechnet maximale Lade- und Entladeleistung basierend auf C-Rate und Derating"""
    if cfg is None:
        cfg = CRConfig(E_nom_kWh, C_chg_rate, C_dis_rate, derating_enable=False)
    
    f_chg, f_dis = derate_factors(SoC, temp_C, cfg)
    P_chg_max = max(0.0, cfg.C_chg_rate * cfg.E_nom_kWh * f_chg)
    P_dis_max = max(0.0, cfg.C_dis_rate * cfg.E_nom_kWh * f_dis)
    
    return {"P_chg_max_kW": P_chg_max, "P_dis_max_kW": P_dis_max}

def apply_bounds(P_req_kW: float, bounds: Dict[str, float], direction: str) -> float:
    """Wendet Leistungsgrenzen auf angeforderte Leistung an"""
    direction = direction.lower()
    if direction == "charge":
        return max(0.0, min(P_req_kW, bounds["P_chg_max_kW"]))
    elif direction == "discharge":
        P_req = abs(P_req_kW)
        return max(0.0, min(P_req, bounds["P_dis_max_kW"]))
    else:
        raise ValueError("direction must be 'charge' or 'discharge'")

def get_battery_config(project_id: int) -> Optional[CRConfig]:
    """Lädt C-Rate Konfiguration aus der Datenbank"""
    try:
        battery_config = BatteryConfig.query.filter_by(project_id=project_id).first()
        if not battery_config:
            return None
        
        # JSON-Felder parsen
        soc_charge = json.loads(battery_config.soc_derate_charge) if battery_config.soc_derate_charge else None
        soc_discharge = json.loads(battery_config.soc_derate_discharge) if battery_config.soc_derate_discharge else None
        temp_charge = json.loads(battery_config.temp_derate_charge) if battery_config.temp_derate_charge else None
        temp_discharge = json.loads(battery_config.temp_derate_discharge) if battery_config.temp_derate_discharge else None
        
        return CRConfig(
            E_nom_kWh=battery_config.E_nom_kWh,
            C_chg_rate=battery_config.C_chg_rate,
            C_dis_rate=battery_config.C_dis_rate,
            derating_enable=battery_config.derating_enable,
            soc_derate_charge=soc_charge,
            soc_derate_discharge=soc_discharge,
            temp_derate_charge=temp_charge,
            temp_derate_discharge=temp_discharge
        )
    except Exception as e:
        print(f"Fehler beim Laden der Battery-Config: {e}")
        return None

def save_battery_config(project_id: int, config_data: Dict) -> bool:
    """Speichert C-Rate Konfiguration in der Datenbank"""
    try:
        # Bestehende Konfiguration löschen oder aktualisieren
        existing_config = BatteryConfig.query.filter_by(project_id=project_id).first()
        
        if existing_config:
            # Update bestehende Konfiguration
            existing_config.E_nom_kWh = config_data['E_nom_kWh']
            existing_config.C_chg_rate = config_data['C_chg_rate']
            existing_config.C_dis_rate = config_data['C_dis_rate']
            existing_config.derating_enable = config_data.get('derating_enable', True)
            existing_config.soc_derate_charge = json.dumps(config_data.get('soc_derate_charge', []))
            existing_config.soc_derate_discharge = json.dumps(config_data.get('soc_derate_discharge', []))
            existing_config.temp_derate_charge = json.dumps(config_data.get('temp_derate_charge', []))
            existing_config.temp_derate_discharge = json.dumps(config_data.get('temp_derate_discharge', []))
        else:
            # Neue Konfiguration erstellen
            new_config = BatteryConfig(
                project_id=project_id,
                E_nom_kWh=config_data['E_nom_kWh'],
                C_chg_rate=config_data['C_chg_rate'],
                C_dis_rate=config_data['C_dis_rate'],
                derating_enable=config_data.get('derating_enable', True),
                soc_derate_charge=json.dumps(config_data.get('soc_derate_charge', [])),
                soc_derate_discharge=json.dumps(config_data.get('soc_derate_discharge', [])),
                temp_derate_charge=json.dumps(config_data.get('temp_derate_charge', [])),
                temp_derate_discharge=json.dumps(config_data.get('temp_derate_discharge', []))
            )
            db.session.add(new_config)
        
        db.session.commit()
        return True
        
    except Exception as e:
        print(f"Fehler beim Speichern der Battery-Config: {e}")
        db.session.rollback()
        return False

def validate_config(config_data: Dict) -> Tuple[bool, str]:
    """Validiert C-Rate Konfigurationsdaten"""
    try:
        # Pflichtfelder prüfen
        required_fields = ['E_nom_kWh', 'C_chg_rate', 'C_dis_rate']
        for field in required_fields:
            if field not in config_data:
                return False, f"Pflichtfeld fehlt: {field}"
        
        # Wertebereiche prüfen
        if config_data['E_nom_kWh'] <= 0:
            return False, "Nennenergie muss > 0 sein"
        
        if not (0 < config_data['C_chg_rate'] <= 2):
            return False, "C-Rate Laden muss zwischen 0 und 2 liegen"
        
        if not (0 < config_data['C_dis_rate'] <= 2):
            return False, "C-Rate Entladen muss zwischen 0 und 2 liegen"
        
        # SoC-Derating Tabellen validieren
        for table_name in ['soc_derate_charge', 'soc_derate_discharge']:
            if table_name in config_data and config_data[table_name]:
                table = config_data[table_name]
                for i, (soc_min, soc_max, factor) in enumerate(table):
                    if not (0 <= soc_min < soc_max <= 1):
                        return False, f"SoC-Intervall {i} in {table_name} ungültig"
                    if not (0 < factor <= 1.5):
                        return False, f"Derating-Faktor {i} in {table_name} ungültig"
        
        # Temperatur-Derating Tabellen validieren
        for table_name in ['temp_derate_charge', 'temp_derate_discharge']:
            if table_name in config_data and config_data[table_name]:
                table = config_data[table_name]
                for i, (temp_min, temp_max, factor) in enumerate(table):
                    if not (-50 <= temp_min < temp_max <= 100):
                        return False, f"Temperatur-Intervall {i} in {table_name} ungültig"
                    if not (0 < factor <= 1.5):
                        return False, f"Derating-Faktor {i} in {table_name} ungültig"
        
        return True, "Konfiguration ist gültig"
        
    except Exception as e:
        return False, f"Validierungsfehler: {str(e)}"

def test_config(config_data: Dict, test_soc: float = 0.5, test_temp: float = 25.0) -> Dict:
    """Testet C-Rate Konfiguration mit Beispielwerten"""
    try:
        # CRConfig erstellen
        cfg = CRConfig(
            E_nom_kWh=config_data['E_nom_kWh'],
            C_chg_rate=config_data['C_chg_rate'],
            C_dis_rate=config_data['C_dis_rate'],
            derating_enable=config_data.get('derating_enable', True),
            soc_derate_charge=config_data.get('soc_derate_charge', []),
            soc_derate_discharge=config_data.get('soc_derate_discharge', []),
            temp_derate_charge=config_data.get('temp_derate_charge', []),
            temp_derate_discharge=config_data.get('temp_derate_discharge', [])
        )
        
        # Leistungsgrenzen berechnen
        bounds = compute_power_bounds(
            cfg.E_nom_kWh, cfg.C_chg_rate, cfg.C_dis_rate,
            SoC=test_soc, temp_C=test_temp, cfg=cfg
        )
        
        # Derating-Faktoren berechnen
        f_chg, f_dis = derate_factors(test_soc, test_temp, cfg)
        
        return {
            'test_conditions': {
                'SoC': test_soc,
                'temperature_C': test_temp
            },
            'power_bounds': bounds,
            'derating_factors': {
                'charge_factor': f_chg,
                'discharge_factor': f_dis
            },
            'nominal_power': {
                'P_chg_nominal_kW': cfg.C_chg_rate * cfg.E_nom_kWh,
                'P_dis_nominal_kW': cfg.C_dis_rate * cfg.E_nom_kWh
            }
        }
        
    except Exception as e:
        return {
            'error': f"Testfehler: {str(e)}"
        }
