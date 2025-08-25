from dataclasses import dataclass
from typing import Optional
from .crate import CRConfig, compute_power_bounds, apply_bounds

@dataclass
class Battery:
    E_nom_kWh: float
    eta_chg: float
    eta_dis: float
    SoC_min: float
    SoC_max: float
    SoC: float
    cfg: CRConfig

    def request_power(self, P_req_kW: float, dt_h: float, direction: str,
                      temp_C: Optional[float] = None) -> float:
        # 1) C-Rate-bedingte Leistungsgrenzen (mit optionalem Derating)
        bounds = compute_power_bounds(self.E_nom_kWh,
                                      self.cfg.C_chg_rate,
                                      self.cfg.C_dis_rate,
                                      SoC=self.SoC, temp_C=temp_C, cfg=self.cfg)

        # 2) Limit gemäß Richtung anwenden
        P_set = apply_bounds(P_req_kW, bounds, direction)

        # 3) SoC-Grenzen vorziehen (präventiv)
        if direction == "charge":
            # maximal zulässige Energie bis SoC_max
            E_room_kWh = max(0.0, (self.SoC_max - self.SoC) * self.E_nom_kWh)
            P_soc_cap = (E_room_kWh / dt_h) / self.eta_chg if dt_h > 0 else 0.0
            P_set = min(P_set, P_soc_cap)
            # SoC-Update
            self.SoC = min(self.SoC_max, self.SoC + (P_set * self.eta_chg * dt_h) / self.E_nom_kWh)
        else:
            # maximal entnehmbare Energie bis SoC_min
            E_avail_kWh = max(0.0, (self.SoC - self.SoC_min) * self.E_nom_kWh)
            P_soc_cap = (E_avail_kWh / dt_h) * self.eta_dis if dt_h > 0 else 0.0
            P_set = min(P_set, P_soc_cap)
            # SoC-Update
            self.SoC = max(self.SoC_min, self.SoC - (P_set / self.eta_dis * dt_h) / self.E_nom_kWh)

        return P_set  # kW (immer positiv), Direction gibt Bedeutung
