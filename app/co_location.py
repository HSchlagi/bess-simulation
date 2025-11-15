"""
Co-Location PV + BESS Modul (Roadmap Stufe 2.1)
Berechnet Curtailment-Vermeidung und PV-geführtes Peak-Shaving
"""

from datetime import datetime
from typing import Dict, Any, Optional
from app import db
from models import CoLocationConfig as CoLocationConfigModel  # Alias to avoid name clash


class CoLocationConfig:
    """Konfiguration für Co-Location PV + BESS"""
    
    def __init__(self, project_id: int, is_co_location: bool, shared_grid_connection_kw: float,
                 pv_power_kw: float, bess_power_kw: float, curtailment_reduction_percent: float,
                 pv_guided_peak_shaving: bool, self_consumption_boost_percent: float):
        self.project_id = project_id
        self.is_co_location = is_co_location
        self.shared_grid_connection_kw = shared_grid_connection_kw  # Gemeinsamer Netzanschluss
        self.pv_power_kw = pv_power_kw
        self.bess_power_kw = bess_power_kw
        self.curtailment_reduction_percent = curtailment_reduction_percent  # % Reduktion durch BESS
        self.pv_guided_peak_shaving = pv_guided_peak_shaving
        self.self_consumption_boost_percent = self_consumption_boost_percent  # % Erhöhung Eigenverbrauch


class CoLocationManager:
    """Manager für Co-Location-Berechnungen"""
    
    @staticmethod
    def load_for_project(project_id: int, pv_power_kw: float, bess_power_kw: float) -> CoLocationConfig:
        """Lädt die Co-Location-Konfiguration für ein Projekt"""
        co_location_db = CoLocationConfigModel.query.filter_by(project_id=project_id).first()
        
        if co_location_db and co_location_db.is_co_location:
            return CoLocationConfig(
                project_id=co_location_db.project_id,
                is_co_location=co_location_db.is_co_location,
                shared_grid_connection_kw=co_location_db.shared_grid_connection_kw,
                pv_power_kw=pv_power_kw,
                bess_power_kw=bess_power_kw,
                curtailment_reduction_percent=co_location_db.curtailment_reduction_percent,
                pv_guided_peak_shaving=co_location_db.pv_guided_peak_shaving,
                self_consumption_boost_percent=co_location_db.self_consumption_boost_percent
            )
        
        # Default: Keine Co-Location
        return CoLocationConfig(
            project_id=project_id,
            is_co_location=False,
            shared_grid_connection_kw=0.0,
            pv_power_kw=pv_power_kw,
            bess_power_kw=bess_power_kw,
            curtailment_reduction_percent=0.0,
            pv_guided_peak_shaving=False,
            self_consumption_boost_percent=0.0
        )
    
    @staticmethod
    def calculate_curtailment_losses(pv_generation_kw: float, export_limit_kw: float, 
                                     bess_charge_capacity_kw: float, consumption_kw: float,
                                     co_location_config: CoLocationConfig) -> Dict[str, float]:
        """
        Berechnet Curtailment-Verluste (PV-Abschaltung)
        
        Args:
            pv_generation_kw: PV-Erzeugung in kW
            export_limit_kw: Exportlimit am Netzanschlusspunkt in kW
            bess_charge_capacity_kw: Verfügbare BESS-Ladekapazität in kW
            consumption_kw: Verbrauch in kW
            co_location_config: Co-Location-Konfiguration
        
        Returns:
            Dict mit curtailment_losses_kw, avoided_curtailment_kw, pv_utilization_percent
        """
        if not co_location_config.is_co_location:
            # Keine Co-Location: Keine Curtailment-Vermeidung
            return {
                'curtailment_losses_kw': 0.0,
                'avoided_curtailment_kw': 0.0,
                'pv_utilization_percent': 100.0,
                'bess_curtailment_charge_kw': 0.0
            }
        
        # Netto-PV-Erzeugung (nach Verbrauch)
        net_pv_generation_kw = max(0.0, pv_generation_kw - consumption_kw)
        
        # Verfügbare Exportkapazität (sicherstellen, dass es nicht None oder negativ ist)
        available_export_kw = max(0.0, export_limit_kw) if export_limit_kw else 0.0
        
        # BESS kann PV-Überschuss aufnehmen
        bess_curtailment_charge_kw = min(
            bess_charge_capacity_kw,
            net_pv_generation_kw - available_export_kw
        )
        bess_curtailment_charge_kw = max(0.0, bess_curtailment_charge_kw)
        
        # Verbleibender PV-Überschuss nach BESS-Ladung
        remaining_pv_excess_kw = max(0.0, net_pv_generation_kw - available_export_kw - bess_curtailment_charge_kw)
        
        # Curtailment-Verluste (PV muss abgeschaltet werden)
        curtailment_losses_kw = remaining_pv_excess_kw
        
        # Vermiedene Curtailment durch BESS
        avoided_curtailment_kw = bess_curtailment_charge_kw * (co_location_config.curtailment_reduction_percent / 100.0)
        
        # PV-Ausnutzung (%)
        if pv_generation_kw > 0:
            utilized_pv_kw = pv_generation_kw - curtailment_losses_kw
            pv_utilization_percent = (utilized_pv_kw / pv_generation_kw) * 100.0
        else:
            pv_utilization_percent = 100.0
        
        return {
            'curtailment_losses_kw': curtailment_losses_kw,
            'avoided_curtailment_kw': avoided_curtailment_kw,
            'pv_utilization_percent': pv_utilization_percent,
            'bess_curtailment_charge_kw': bess_curtailment_charge_kw,
            'net_pv_generation_kw': net_pv_generation_kw,
            'exported_pv_kw': min(net_pv_generation_kw, available_export_kw)
        }
    
    @staticmethod
    def calculate_pv_guided_peak_shaving(pv_generation_kw: float, consumption_kw: float,
                                         bess_discharge_capacity_kw: float,
                                         co_location_config: CoLocationConfig) -> Dict[str, float]:
        """
        Berechnet PV-geführtes Peak-Shaving
        
        Args:
            pv_generation_kw: PV-Erzeugung in kW
            consumption_kw: Verbrauch in kW
            bess_discharge_capacity_kw: Verfügbare BESS-Entladekapazität in kW
            co_location_config: Co-Location-Konfiguration
        
        Returns:
            Dict mit peak_shaving_kw, self_consumption_kw, grid_import_kw
        """
        if not co_location_config.is_co_location or not co_location_config.pv_guided_peak_shaving:
            return {
                'peak_shaving_kw': 0.0,
                'self_consumption_kw': min(pv_generation_kw, consumption_kw),
                'grid_import_kw': max(0.0, consumption_kw - pv_generation_kw),
                'grid_export_kw': max(0.0, pv_generation_kw - consumption_kw)
            }
        
        # Eigenverbrauch (PV direkt für Verbrauch)
        direct_self_consumption_kw = min(pv_generation_kw, consumption_kw)
        
        # PV-Überschuss
        pv_excess_kw = max(0.0, pv_generation_kw - consumption_kw)
        
        # Verbleibender Verbrauch nach PV
        remaining_consumption_kw = max(0.0, consumption_kw - pv_generation_kw)
        
        # BESS kann PV-Überschuss speichern und später für Peak-Shaving nutzen
        # Vereinfacht: BESS entlädt bei Verbrauchsspitzen
        peak_shaving_kw = min(
            bess_discharge_capacity_kw,
            remaining_consumption_kw
        )
        peak_shaving_kw = max(0.0, peak_shaving_kw)
        
        # Gesamter Eigenverbrauch (direkt + über BESS)
        total_self_consumption_kw = direct_self_consumption_kw + peak_shaving_kw
        
        # Netto-Grid-Import
        grid_import_kw = max(0.0, remaining_consumption_kw - peak_shaving_kw)
        
        # Netto-Grid-Export (PV-Überschuss nach BESS-Ladung)
        grid_export_kw = max(0.0, pv_excess_kw - peak_shaving_kw)
        
        # Eigenverbrauchs-Boost durch Co-Location
        self_consumption_boost_kw = total_self_consumption_kw * (co_location_config.self_consumption_boost_percent / 100.0)
        
        return {
            'peak_shaving_kw': peak_shaving_kw,
            'self_consumption_kw': total_self_consumption_kw + self_consumption_boost_kw,
            'grid_import_kw': grid_import_kw,
            'grid_export_kw': grid_export_kw,
            'direct_self_consumption_kw': direct_self_consumption_kw,
            'bess_self_consumption_kw': peak_shaving_kw,
            'self_consumption_boost_kw': self_consumption_boost_kw
        }
    
    @staticmethod
    def calculate_co_location_benefits(annual_pv_generation_mwh: float, annual_consumption_mwh: float,
                                      curtailment_data: Dict[str, float], peak_shaving_data: Dict[str, float],
                                      spot_price_eur_mwh: float, grid_fee_eur_mwh: float,
                                      co_location_config: CoLocationConfig) -> Dict[str, float]:
        """
        Berechnet die wirtschaftlichen Vorteile der Co-Location
        
        Returns:
            Dict mit revenue_increase, cost_savings, total_benefit
        """
        if not co_location_config.is_co_location:
            return {
                'revenue_increase_eur': 0.0,
                'cost_savings_eur': 0.0,
                'total_benefit_eur': 0.0,
                'curtailment_loss_revenue_eur': 0.0,
                'avoided_curtailment_revenue_eur': 0.0,
                'grid_fee_savings_eur': 0.0
            }
        
        # Vermiedene Curtailment-Verluste (können verkauft werden)
        avoided_curtailment_mwh = (curtailment_data['avoided_curtailment_kw'] * 8760) / 1000.0  # Jahreswert
        avoided_curtailment_revenue_eur = avoided_curtailment_mwh * spot_price_eur_mwh
        
        # Verlorene Curtailment-Verluste (können nicht verkauft werden)
        curtailment_loss_mwh = (curtailment_data['curtailment_losses_kw'] * 8760) / 1000.0
        curtailment_loss_revenue_eur = curtailment_loss_mwh * spot_price_eur_mwh
        
        # Grid-Fee-Ersparnis durch erhöhten Eigenverbrauch
        self_consumption_increase_mwh = (peak_shaving_data['self_consumption_boost_kw'] * 8760) / 1000.0
        grid_fee_savings_eur = self_consumption_increase_mwh * grid_fee_eur_mwh
        
        # Gesamter Erlöszuwachs
        revenue_increase_eur = avoided_curtailment_revenue_eur
        
        # Gesamte Kosteneinsparung
        cost_savings_eur = grid_fee_savings_eur
        
        # Gesamter Nutzen
        total_benefit_eur = revenue_increase_eur + cost_savings_eur
        
        return {
            'revenue_increase_eur': revenue_increase_eur,
            'cost_savings_eur': cost_savings_eur,
            'total_benefit_eur': total_benefit_eur,
            'curtailment_loss_revenue_eur': curtailment_loss_revenue_eur,
            'avoided_curtailment_revenue_eur': avoided_curtailment_revenue_eur,
            'grid_fee_savings_eur': grid_fee_savings_eur,
            'pv_utilization_percent': curtailment_data['pv_utilization_percent'],
            'self_consumption_rate_percent': (peak_shaving_data['self_consumption_kw'] / max(annual_consumption_mwh * 1000 / 8760, 1.0)) * 100.0
        }

