from dataclasses import dataclass
from typing import Optional, Tuple, Dict, List

@dataclass
class CRConfig:
    E_nom_kWh: float
    C_chg_rate: float
    C_dis_rate: float
    derating_enable: bool = True
    soc_derate_charge: Optional[List[Tuple[float,float,float]]] = None
    soc_derate_discharge: Optional[List[Tuple[float,float,float]]] = None
    temp_derate_charge: Optional[List[Tuple[float,float,float]]] = None
    temp_derate_discharge: Optional[List[Tuple[float,float,float]]] = None

def _piecewise_factor(x: Optional[float], table: Optional[List[Tuple[float,float,float]]], default: float=1.0) -> float:
    if x is None or not table:
        return default
    for lo, hi, fac in table:
        if lo <= x < hi:
            return float(fac)
    return default

def derate_factors(SoC: Optional[float], temp_C: Optional[float], cfg: CRConfig) -> Tuple[float, float]:
    if not cfg.derating_enable:
        return 1.0, 1.0
    f_soc_chg = _piecewise_factor(SoC, cfg.soc_derate_charge, 1.0)
    f_soc_dis = _piecewise_factor(SoC, cfg.soc_derate_discharge, 1.0)
    f_t_chg   = _piecewise_factor(temp_C, cfg.temp_derate_charge, 1.0)
    f_t_dis   = _piecewise_factor(temp_C, cfg.temp_derate_discharge, 1.0)
    return f_soc_chg * f_t_chg, f_soc_dis * f_t_dis

def compute_power_bounds(E_nom_kWh: float,
                         C_chg_rate: float,
                         C_dis_rate: float,
                         SoC: Optional[float]=None,
                         temp_C: Optional[float]=None,
                         cfg: Optional[CRConfig]=None) -> Dict[str, float]:
    if cfg is None:
        cfg = CRConfig(E_nom_kWh, C_chg_rate, C_dis_rate, derating_enable=False)
    f_chg, f_dis = derate_factors(SoC, temp_C, cfg)
    P_chg_max = max(0.0, cfg.C_chg_rate * cfg.E_nom_kWh * f_chg)
    P_dis_max = max(0.0, cfg.C_dis_rate * cfg.E_nom_kWh * f_dis)
    return {"P_chg_max_kW": P_chg_max, "P_dis_max_kW": P_dis_max}

def apply_bounds(P_req_kW: float, bounds: Dict[str, float], direction: str) -> float:
    direction = direction.lower()
    if direction == "charge":
        return max(0.0, min(P_req_kW, bounds["P_chg_max_kW"]))
    elif direction == "discharge":
        P_req = abs(P_req_kW)
        return max(0.0, min(P_req, bounds["P_dis_max_kW"]))
    else:
        raise ValueError("direction must be 'charge' or 'discharge'")
