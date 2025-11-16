"""
Roadmap Stufe 2.1 Integration Helper
Co-Location PV + BESS
"""

from app import db
from models import CoLocationConfig
from app.co_location import CoLocationManager, CoLocationConfig as CoLocationConfigClass
from typing import Dict, Any


def load_co_location_config(project_id: int, pv_power_kw: float, bess_power_kw: float) -> CoLocationConfigClass:
    """Lädt die Co-Location-Konfiguration für ein Projekt."""
    return CoLocationManager.load_for_project(project_id, pv_power_kw, bess_power_kw)


def calculate_co_location_benefits_for_simulation(
    co_location_config: CoLocationConfigClass,
    annual_pv_generation_mwh: float,
    annual_consumption_mwh: float,
    export_limit_kw: float,
    bess_charge_capacity_kw: float,
    bess_discharge_capacity_kw: float,
    spot_price_eur_mwh: float,
    grid_fee_eur_mwh: float = 0.05,  # 0.05 EUR/kWh = 50 EUR/MWh
    annual_wind_generation_mwh: float = 0.0  # ROADMAP STUFE 2.1: Co-Location PV+Wind+BESS
) -> Dict[str, Any]:
    """
    Berechnet Co-Location-Vorteile für die Simulation (erweitert für PV+Wind+BESS)
    
    Args:
        co_location_config: Co-Location-Konfiguration
        annual_pv_generation_mwh: Jährliche PV-Erzeugung in MWh
        annual_consumption_mwh: Jährlicher Verbrauch in MWh
        export_limit_kw: Exportlimit in kW
        bess_charge_capacity_kw: Verfügbare BESS-Ladekapazität in kW
        bess_discharge_capacity_kw: Verfügbare BESS-Entladekapazität in kW
        spot_price_eur_mwh: Spot-Preis in EUR/MWh
        grid_fee_eur_mwh: Netzentgelt in EUR/MWh
        annual_wind_generation_mwh: Jährliche Wind-Erzeugung in MWh (optional)
    
    Returns:
        Dict mit allen Co-Location-Kennzahlen
    """
    if not co_location_config.is_co_location:
        return {
            'is_co_location': False,
            'curtailment_losses_kw': 0.0,
            'avoided_curtailment_kw': 0.0,
            'pv_utilization_percent': 100.0,
            'self_consumption_rate_percent': 0.0,
            'peak_shaving_kw': 0.0,
            'revenue_increase_eur': 0.0,
            'cost_savings_eur': 0.0,
            'total_benefit_eur': 0.0
        }
    
    # Durchschnittliche PV-Erzeugung, Wind-Erzeugung und Verbrauch pro Stunde (vereinfacht)
    avg_pv_generation_kw = (annual_pv_generation_mwh * 1000) / 8760  # kW
    avg_wind_generation_kw = (annual_wind_generation_mwh * 1000) / 8760  # kW
    avg_consumption_kw = (annual_consumption_mwh * 1000) / 8760  # kW
    
    # Curtailment-Berechnung (erweitert für PV+Wind)
    curtailment_data = CoLocationManager.calculate_curtailment_losses(
        pv_generation_kw=avg_pv_generation_kw,
        export_limit_kw=export_limit_kw,
        bess_charge_capacity_kw=bess_charge_capacity_kw,
        consumption_kw=avg_consumption_kw,
        co_location_config=co_location_config,
        wind_generation_kw=avg_wind_generation_kw  # ROADMAP STUFE 2.1: Winddaten einbeziehen
    )
    
    # PV-geführtes Peak-Shaving (erweitert für PV+Wind)
    peak_shaving_data = CoLocationManager.calculate_pv_guided_peak_shaving(
        pv_generation_kw=avg_pv_generation_kw,
        consumption_kw=avg_consumption_kw,
        bess_discharge_capacity_kw=bess_discharge_capacity_kw,
        co_location_config=co_location_config,
        wind_generation_kw=avg_wind_generation_kw  # ROADMAP STUFE 2.1: Winddaten einbeziehen
    )
    
    # Wirtschaftliche Vorteile (erweitert für PV+Wind)
    benefits = CoLocationManager.calculate_co_location_benefits(
        annual_pv_generation_mwh=annual_pv_generation_mwh,
        annual_consumption_mwh=annual_consumption_mwh,
        curtailment_data=curtailment_data,
        peak_shaving_data=peak_shaving_data,
        spot_price_eur_mwh=spot_price_eur_mwh,
        grid_fee_eur_mwh=grid_fee_eur_mwh,
        co_location_config=co_location_config,
        annual_wind_generation_mwh=annual_wind_generation_mwh  # ROADMAP STUFE 2.1: Winddaten einbeziehen
    )
    
    return {
        'is_co_location': True,
        'curtailment_losses_kw': curtailment_data['curtailment_losses_kw'],
        'avoided_curtailment_kw': curtailment_data['avoided_curtailment_kw'],
        'pv_utilization_percent': curtailment_data['pv_utilization_percent'],
        'bess_curtailment_charge_kw': curtailment_data['bess_curtailment_charge_kw'],
        'peak_shaving_kw': peak_shaving_data['peak_shaving_kw'],
        'self_consumption_rate_percent': benefits['self_consumption_rate_percent'],
        'revenue_increase_eur': benefits['revenue_increase_eur'],
        'cost_savings_eur': benefits['cost_savings_eur'],
        'total_benefit_eur': benefits['total_benefit_eur'],
        'curtailment_loss_revenue_eur': benefits['curtailment_loss_revenue_eur'],
        'avoided_curtailment_revenue_eur': benefits['avoided_curtailment_revenue_eur'],
        'grid_fee_savings_eur': benefits['grid_fee_savings_eur']
    }




