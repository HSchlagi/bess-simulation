#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Erweiterte Wirtschaftlichkeitsanalyse für BESS-Simulation
mit 10-Jahres-Prognose, Batterie-Degradation und Intraday-Arbitrage
"""

import pandas as pd
import numpy as np
from datetime import datetime, date
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import json
import os

# Intraday-Arbitrage Integration
try:
    from src.intraday import (
        theoretical_revenue, spread_based_revenue, thresholds_based_revenue
    )
    INTRADAY_AVAILABLE = True
except ImportError:
    INTRADAY_AVAILABLE = False
    print("Warnung: Intraday-Arbitrage Modul nicht verfügbar")

# Österreichische Marktdaten Integration
try:
    from src.markets import ATMarketIntegrator, BESSSpec
    AT_MARKET_AVAILABLE = True
except ImportError:
    AT_MARKET_AVAILABLE = False
    print("Warnung: Österreichische Marktdaten-Modul nicht verfügbar")

@dataclass
class InvestmentData:
    """Investitionsdaten"""
    bess_cost_eur: float
    pv_cost_eur: float = 0.0
    hydro_cost_eur: float = 0.0
    installation_cost_eur: float = 0.0
    other_costs_eur: float = 0.0
    
    @property
    def total_investment_eur(self) -> float:
        return (self.bess_cost_eur + self.pv_cost_eur + self.hydro_cost_eur + 
                self.installation_cost_eur + self.other_costs_eur)

@dataclass
class OperatingData:
    """Betriebsdaten"""
    annual_energy_consumption_mwh: float
    annual_energy_generation_mwh: float
    annual_energy_stored_mwh: float
    annual_energy_discharged_mwh: float
    annual_cycles: int
    average_spot_price_eur_mwh: float

@dataclass
class FinancialData:
    """Finanzdaten"""
    electricity_cost_eur_mwh: float
    feed_in_tariff_eur_mwh: float
    grid_tariff_eur_mwh: float
    legal_charges_eur_mwh: float
    subsidy_eur_mwh: float = 0.0

class BatteryDegradationModel:
    """Modelliert Batterie-Degradation über 10 Jahre"""
    
    def __init__(self, initial_capacity_kwh: float, degradation_rate_per_year: float = 0.02):
        self.initial_capacity = initial_capacity_kwh
        self.degradation_rate = degradation_rate_per_year
        
    def calculate_capacity_factor(self, year: int, cycles_per_year: int) -> float:
        """
        Berechnet den Kapazitätsfaktor für ein bestimmtes Jahr
        
        Args:
            year: Jahr seit Inbetriebnahme (0 = erstes Jahr)
            cycles_per_year: Durchschnittliche Zyklen pro Jahr
            
        Returns:
            Kapazitätsfaktor (1.0 = 100% Kapazität)
        """
        # Zeitbasierte Degradation
        time_degradation = 1 - (self.degradation_rate * year)
        
        # Zyklusbasierte Degradation (zusätzlich zur Zeitdegradation)
        cycle_degradation_factor = 1 - (cycles_per_year * 0.0001)  # 0.01% pro Zyklus
        
        # Kombinierte Degradation
        capacity_factor = time_degradation * cycle_degradation_factor
        
        return max(0.7, capacity_factor)  # Mindestkapazität 70%
    
    def calculate_remaining_capacity(self, year: int, cycles_per_year: int) -> float:
        """Berechnet die verbleibende Kapazität in kWh"""
        capacity_factor = self.calculate_capacity_factor(year, cycles_per_year)
        return self.initial_capacity * capacity_factor

def intraday_revenue(cfg: Dict, E_kWh: float, P_kW: float, DoD: float, eta_rt: float) -> float:
    """
    Berechnet Intraday-Arbitrage-Erlöse gemäß Konfiguration
    
    Args:
        cfg: Konfigurations-Dictionary
        E_kWh: Batteriekapazität in kWh
        P_kW: Batterieleistung in kW
        DoD: Depth of Discharge (0-1)
        eta_rt: Roundtrip-Effizienz (0-1)
        
    Returns:
        float: Intraday-Erlöse in EUR für den Preis-Serien-Zeitraum (oder pro Jahr für theoretical)
    """
    if not INTRADAY_AVAILABLE:
        return 0.0
        
    intr = cfg.get("intraday", {})
    prices_csv = intr.get("prices_csv")
    mode = intr.get("mode", "threshold")

    prices = None
    if prices_csv:
        try:
            prices_df = pd.read_csv(f"data/{prices_csv}")
            prices = _ensure_price_kwh(prices_df)
        except Exception as e:
            print(f"Warnung: Konnte Intraday-Preisdaten nicht laden: {e}")
            return 0.0

    if mode == "theoretical":
        return theoretical_revenue(E_kWh, DoD, eta_rt,
                                   intr.get("delta_p_eur_per_kWh", 0.06),
                                   intr.get("cycles_per_day", 1.0),
                                   days=365)
    elif mode == "spread":
        if prices is None: 
            return 0.0
        rev, _ = spread_based_revenue(prices, E_kWh=E_kWh, DoD=DoD, P_kW=P_kW,
                                      eta_rt=eta_rt, cycles_cap_per_day=intr.get("cycles_per_day_cap", 1.0))
        return rev
    elif mode == "threshold":
        if prices is None: 
            return 0.0
        rev, _ = thresholds_based_revenue(prices, E_kWh, DoD, P_kW, eta_rt,
            intr.get("buy_threshold_eur_per_MWh", 45)/1000.0,
            intr.get("sell_threshold_eur_per_MWh", 85)/1000.0,
            intr.get("cycles_per_day_cap", 1.0))
        return rev
    else:
        return 0.0

def calculate_austrian_market_revenue(cfg: Dict, E_kWh: float, P_kW: float) -> Dict[str, float]:
    """
    Berechnet Erlöse aus österreichischen Energiemärkten
    
    Args:
        cfg: Konfigurations-Dictionary
        E_kWh: Batteriekapazität in kWh
        P_kW: Batterieleistung in kW
        
    Returns:
        Dict[str, float]: Erlöse aus verschiedenen Märkten
    """
    if not AT_MARKET_AVAILABLE:
        return {}
        
    market_config = cfg.get("austrian_markets", {})
    spec = BESSSpec(power_mw=P_kW/1000.0, energy_mwh=E_kWh/1000.0)
    
    revenues = {}
    
    # APG Regelenergie
    apg_config = market_config.get("apg", {})
    if apg_config.get("enabled", False):
        try:
            integrator = ATMarketIntegrator()
            
            # Kapazitätsmärkte
            cap_path = apg_config.get("capacity_csv")
            if cap_path and os.path.exists(cap_path):
                cap_series = integrator.load_apg_capacity(cap_path, apg_config.get("product_filter"))
                revenues["apg_capacity_revenue"] = revenue_from_capacity(spec, cap_series)
            
            # Aktivierungsmärkte
            act_path = apg_config.get("activation_csv")
            if act_path and os.path.exists(act_path):
                act_series = integrator.load_apg_activation(act_path, apg_config.get("product_filter"))
                revenues["apg_activation_revenue"] = revenue_from_activation(spec, act_series)
                
        except Exception as e:
            print(f"Warnung: APG Marktdaten konnten nicht verarbeitet werden: {e}")
    
    # EPEX Intraday Auktionen
    epex_config = market_config.get("epex", {})
    if epex_config.get("enabled", False):
        try:
            integrator = ATMarketIntegrator()
            ida_paths = epex_config.get("ida_csv_paths", [])
            
            if ida_paths:
                ida_df = integrator.load_ida_csvs(ida_paths)
                ida_series = integrator.ida_quarter_series(ida_df)
                revenues["epex_ida_revenue"] = revenue_from_ida(spec, ida_series)
                
        except Exception as e:
            print(f"Warnung: EPEX Marktdaten konnten nicht verarbeitet werden: {e}")
    
    return revenues

class RegulatoryChangeModel:
    """Modelliert gesetzliche Änderungen über Zeit"""
    
    def __init__(self):
        self.changes = {
            'electricity_tax': {
                2024: 1.0,   # EUR/MWh
                2025: 15.0   # EUR/MWh
            },
            'subsidy_pv': {
                2024: 0.0,   # EUR/MWh
                2025: 0.0    # EUR/MWh
            }
        }
    
    def get_electricity_tax(self, year: int) -> float:
        """Gibt die Stromabgabe für ein bestimmtes Jahr zurück"""
        if year in self.changes['electricity_tax']:
            return self.changes['electricity_tax'][year]
        else:
            # Extrapolation für zukünftige Jahre
            return self.changes['electricity_tax'][2025]
    
    def get_pv_subsidy(self, year: int) -> float:
        """Gibt die PV-Förderung für ein bestimmtes Jahr zurück"""
        if year in self.changes['subsidy_pv']:
            return self.changes['subsidy_pv'][year]
        else:
            return 0.0

class EconomicAnalysisEnhanced:
    """Erweiterte Wirtschaftlichkeitsanalyse"""
    
    def __init__(self, investment: InvestmentData, operating: OperatingData, 
                 financial: FinancialData):
        self.investment = investment
        self.operating = operating
        self.financial = financial
        self.degradation_model = BatteryDegradationModel(investment.bess_cost_eur / 1000)  # Annahme: 1000 EUR/kWh
        self.regulatory_model = RegulatoryChangeModel()
        
    def calculate_annual_revenues(self, year: int, capacity_factor: float, config: Dict = None) -> Dict[str, float]:
        """
        Berechnet jährliche Erlöse inklusive Intraday-Arbitrage und österreichischer Märkte
        
        Args:
            year: Jahr seit Inbetriebnahme
            capacity_factor: Kapazitätsfaktor (Degradation)
            config: Konfigurations-Dictionary für erweiterte Features
        """
        # Basis-Energiemengen mit Degradation
        energy_stored = self.operating.annual_energy_stored_mwh * capacity_factor
        energy_discharged = self.operating.annual_energy_discharged_mwh * capacity_factor
        
        # Basis-Arbitrage-Erlöse
        arbitrage_revenue = energy_discharged * self.operating.average_spot_price_eur_mwh * 0.85  # Wirkungsgrad
        
        # SRL-Erlöse (Annahme: 5% der Zeit aktiviert)
        srl_hours = 8760 * 0.05
        srl_power_mw = (self.investment.bess_cost_eur / 1000) / 1000  # Annahme: 1 MW
        srl_positive_revenue = srl_power_mw * srl_hours * 45.0 * 0.95  # SRL+ Preis
        srl_negative_revenue = srl_power_mw * srl_hours * 35.0 * 0.95  # SRL- Preis
        
        # PV-Förderung
        pv_subsidy = self.operating.annual_energy_generation_mwh * self.regulatory_model.get_pv_subsidy(year)
        
        # Basis-Erlöse
        revenues = {
            'arbitrage': arbitrage_revenue,
            'srl_positive': srl_positive_revenue,
            'srl_negative': srl_negative_revenue,
            'pv_subsidy': pv_subsidy,
            'feed_in_tariff': self.operating.annual_energy_generation_mwh * self.financial.feed_in_tariff_eur_mwh
        }
        
        # Erweiterte Erlöse (Intraday-Arbitrage)
        if config and INTRADAY_AVAILABLE:
            try:
                # BESS-Parameter schätzen
                E_kWh = self.investment.bess_cost_eur / 1000  # Annahme: 1000 EUR/kWh
                P_kW = E_kWh * 0.25  # Annahme: 4h Speicher
                DoD = 0.9  # Depth of Discharge
                eta_rt = 0.85  # Roundtrip-Effizienz
                
                intraday_rev = intraday_revenue(config, E_kWh, P_kW, DoD, eta_rt)
                revenues['intraday_arbitrage'] = intraday_rev
                
            except Exception as e:
                print(f"Warnung: Intraday-Arbitrage-Berechnung fehlgeschlagen: {e}")
                revenues['intraday_arbitrage'] = 0.0
        
        # Österreichische Markt-Erlöse
        if config and AT_MARKET_AVAILABLE:
            try:
                E_kWh = self.investment.bess_cost_eur / 1000
                P_kW = E_kWh * 0.25
                
                austrian_revenues = calculate_austrian_market_revenue(config, E_kWh, P_kW)
                revenues.update(austrian_revenues)
                
            except Exception as e:
                print(f"Warnung: Österreichische Markt-Berechnung fehlgeschlagen: {e}")
        
        revenues['total'] = sum(revenues.values())
        return revenues
    
    def calculate_annual_costs(self, year: int) -> Dict[str, float]:
        """Berechnet jährliche Kosten"""
        # Strombezugskosten
        net_consumption = self.operating.annual_energy_consumption_mwh - self.operating.annual_energy_generation_mwh
        electricity_cost = net_consumption * self.financial.electricity_cost_eur_mwh
        
        # Netzentgelte
        grid_cost = net_consumption * self.financial.grid_tariff_eur_mwh
        
        # Gesetzliche Abgaben
        electricity_tax = net_consumption * self.regulatory_model.get_electricity_tax(year)
        legal_charges = net_consumption * self.financial.legal_charges_eur_mwh
        
        # Betriebskosten (Annahme: 2% der Investition)
        operating_cost = self.investment.total_investment_eur * 0.02
        
        costs = {
            'electricity': electricity_cost,
            'grid_tariff': grid_cost,
            'electricity_tax': electricity_tax,
            'legal_charges': legal_charges,
            'operating_cost': operating_cost
        }
        
        costs['total'] = sum(costs.values())
        return costs
    
    def calculate_annual_cashflow(self, year: int) -> Dict[str, float]:
        """Berechnet jährlichen Cashflow"""
        # Kapazitätsfaktor für dieses Jahr
        capacity_factor = self.degradation_model.calculate_capacity_factor(year, self.operating.annual_cycles)
        
        # Erlöse und Kosten
        revenues = self.calculate_annual_revenues(year, capacity_factor)
        costs = self.calculate_annual_costs(year)
        
        # Cashflow
        cashflow = {
            'revenues': revenues['total'],
            'costs': costs['total'],
            'net_cashflow': revenues['total'] - costs['total'],
            'capacity_factor': capacity_factor
        }
        
        return cashflow
    
    def calculate_10_year_analysis(self) -> Dict[str, List[float]]:
        """Berechnet 10-Jahres-Analyse"""
        years = list(range(10))
        cashflows = []
        cumulative_cashflow = 0
        
        for year in years:
            cashflow = self.calculate_annual_cashflow(year)
            cumulative_cashflow += cashflow['net_cashflow']
            
            cashflows.append({
                'year': year + 2024,  # Startjahr 2024
                'revenues': cashflow['revenues'],
                'costs': cashflow['costs'],
                'net_cashflow': cashflow['net_cashflow'],
                'cumulative_cashflow': cumulative_cashflow,
                'capacity_factor': cashflow['capacity_factor'],
                'remaining_capacity_kwh': self.degradation_model.calculate_remaining_capacity(year, self.operating.annual_cycles)
            })
        
        return cashflows
    
    def calculate_roi_metrics(self, cashflows: List[Dict]) -> Dict[str, float]:
        """Berechnet ROI-Metriken"""
        total_investment = self.investment.total_investment_eur
        total_revenues = sum(cf['revenues'] for cf in cashflows)
        total_costs = sum(cf['costs'] for cf in cashflows)
        total_net_cashflow = sum(cf['net_cashflow'] for cf in cashflows)
        
        # ROI
        roi_percent = (total_net_cashflow / total_investment) * 100
        
        # Payback Period
        cumulative = 0
        payback_year = None
        for cf in cashflows:
            cumulative += cf['net_cashflow']
            if cumulative >= total_investment and payback_year is None:
                payback_year = cf['year']
        
        # NPV (Net Present Value) mit 5% Diskontierung
        npv = 0
        for cf in cashflows:
            discount_factor = 1 / ((1 + 0.05) ** (cf['year'] - 2024))
            npv += cf['net_cashflow'] * discount_factor
        
        # IRR (Internal Rate of Return) - vereinfachte Berechnung
        irr_percent = (total_net_cashflow / total_investment) ** (1/10) - 1
        
        return {
            'total_investment_eur': total_investment,
            'total_revenues_eur': total_revenues,
            'total_costs_eur': total_costs,
            'total_net_cashflow_eur': total_net_cashflow,
            'roi_percent': roi_percent,
            'payback_year': payback_year,
            'npv_eur': npv,
            'irr_percent': irr_percent * 100
        }

def create_sample_analysis() -> EconomicAnalysisEnhanced:
    """Erstellt eine Beispiel-Analyse für Hinterstoder"""
    
    # Investitionsdaten
    investment = InvestmentData(
        bess_cost_eur=500000.0,      # 500.000 EUR für BESS
        pv_cost_eur=1950000.0,       # 1,95 MWp * 1000 EUR/kWp
        hydro_cost_eur=650000.0,     # 650 kW * 1000 EUR/kW
        installation_cost_eur=200000.0,
        other_costs_eur=100000.0
    )
    
    # Betriebsdaten
    operating = OperatingData(
        annual_energy_consumption_mwh=4380.0,  # 500 kW * 8760 h
        annual_energy_generation_mwh=2190.0,   # PV + Hydro
        annual_energy_stored_mwh=1000.0,       # 1 MWh BESS
        annual_energy_discharged_mwh=850.0,    # Mit Wirkungsgrad
        annual_cycles=300,                     # 300 Zyklen pro Jahr
        average_spot_price_eur_mwh=60.0        # Durchschnittlicher Spotpreis
    )
    
    # Finanzdaten
    financial = FinancialData(
        electricity_cost_eur_mwh=120.0,        # 12 Ct/kWh
        feed_in_tariff_eur_mwh=80.0,           # 8 Ct/kWh
        grid_tariff_eur_mwh=25.0,              # Netzentgelt
        legal_charges_eur_mwh=9.65             # Stromabgabe + Netzverlust + Clearing
    )
    
    return EconomicAnalysisEnhanced(investment, operating, financial)

def main():
    """Test-Funktion"""
    print("=== BESS-Simulation: Erweiterte Wirtschaftlichkeitsanalyse ===")
    
    # Beispiel-Analyse erstellen
    analysis = create_sample_analysis()
    
    print(f"Investition: {analysis.investment.total_investment_eur:,.0f} EUR")
    print(f"Jährlicher Verbrauch: {analysis.operating.annual_energy_consumption_mwh:,.0f} MWh")
    print(f"Jährliche Erzeugung: {analysis.operating.annual_energy_generation_mwh:,.0f} MWh")
    
    # 10-Jahres-Analyse
    cashflows = analysis.calculate_10_year_analysis()
    
    print(f"\n10-Jahres-Analyse:")
    print(f"{'Jahr':<6} {'Erlöse':<12} {'Kosten':<12} {'Cashflow':<12} {'Kapazität':<10}")
    print("-" * 60)
    
    for cf in cashflows:
        print(f"{cf['year']:<6} {cf['revenues']:>10,.0f} {cf['costs']:>10,.0f} "
              f"{cf['net_cashflow']:>10,.0f} {cf['capacity_factor']:>8.1%}")
    
    # ROI-Metriken
    metrics = analysis.calculate_roi_metrics(cashflows)
    
    print(f"\nWirtschaftlichkeitsmetriken:")
    print(f"Gesamtinvestition: {metrics['total_investment_eur']:,.0f} EUR")
    print(f"Gesamterlöse: {metrics['total_revenues_eur']:,.0f} EUR")
    print(f"Gesamtkosten: {metrics['total_costs_eur']:,.0f} EUR")
    print(f"Gesamt-Cashflow: {metrics['total_net_cashflow_eur']:,.0f} EUR")
    print(f"ROI: {metrics['roi_percent']:.1f}%")
    print(f"Amortisationszeit: {metrics['payback_year']} Jahre")
    print(f"NPV (5%): {metrics['npv_eur']:,.0f} EUR")
    print(f"IRR: {metrics['irr_percent']:.1f}%")
    
    # Export für Chart.js
    chart_data = {
        'labels': [cf['year'] for cf in cashflows],
        'datasets': [
            {
                'label': 'Erlöse',
                'data': [cf['revenues'] for cf in cashflows],
                'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                'borderColor': 'rgba(75, 192, 192, 1)',
                'borderWidth': 2
            },
            {
                'label': 'Kosten',
                'data': [cf['costs'] for cf in cashflows],
                'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                'borderColor': 'rgba(255, 99, 132, 1)',
                'borderWidth': 2
            },
            {
                'label': 'Net Cashflow',
                'data': [cf['net_cashflow'] for cf in cashflows],
                'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                'borderColor': 'rgba(54, 162, 235, 1)',
                'borderWidth': 2
            }
        ]
    }
    
    # JSON-Datei für Frontend speichern
    with open('chart_data_enhanced.json', 'w', encoding='utf-8') as f:
        json.dump(chart_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nChart-Daten gespeichert in: chart_data_enhanced.json")
    print("\n✓ Analyse erfolgreich abgeschlossen!")

if __name__ == "__main__":
    main() 