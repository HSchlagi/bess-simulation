import math
from bess.crate import CRConfig, compute_power_bounds, apply_bounds

def test_bounds_nominal():
    cfg = CRConfig(E_nom_kWh=8000, C_chg_rate=0.5, C_dis_rate=1.0, derating_enable=False)
    b = compute_power_bounds(8000, 0.5, 1.0, cfg=cfg)
    assert math.isclose(b["P_chg_max_kW"], 4000)
    assert math.isclose(b["P_dis_max_kW"], 8000)

def test_soc_derate_charge_high_soc():
    cfg = CRConfig(
        E_nom_kWh=8000, C_chg_rate=0.5, C_dis_rate=1.0, derating_enable=True,
        soc_derate_charge=[(0.0,0.8,1.0),(0.8,1.0,0.5)]
    )
    b = compute_power_bounds(8000, 0.5, 1.0, SoC=0.9, cfg=cfg)
    assert math.isclose(b["P_chg_max_kW"], 2000)

def test_apply_bounds():
    cfg = CRConfig(E_nom_kWh=8000, C_chg_rate=0.5, C_dis_rate=1.0, derating_enable=False)
    b = compute_power_bounds(8000, 0.5, 1.0, cfg=cfg)
    assert apply_bounds(5000, b, "charge") == 4000
    assert apply_bounds(9000, b, "discharge") == 8000
