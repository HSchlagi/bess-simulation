#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug-Skript zur Analyse des Netto-Cashflows im Use Case Vergleich
Zeigt Schritt für Schritt, wie die Werte zustande kommen
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from enhanced_economic_analysis import EnhancedEconomicAnalyzer, BESSUseCase

def debug_net_cashflow():
    """Analysiert die Netto-Cashflow-Berechnung Schritt für Schritt"""
    
    print("=" * 80)
    print("DEBUG: NETTO-CASHFLOW BERECHNUNG")
    print("=" * 80)
    print()
    
    # Beispiel-Projekt (Hinterstoder: 8 MWh / 2 MW)
    bess_size_mwh = 8.0  # 8 MWh
    bess_power_mw = 2.0  # 2 MW
    investment_costs = 6130000  # 6.13 Mio € (Beispiel)
    
    print(f"PROJEKT-PARAMETER:")
    print(f"  - BESS-Kapazität: {bess_size_mwh} MWh")
    print(f"  - BESS-Leistung: {bess_power_mw} MW")
    print(f"  - Investitionskosten: {investment_costs:,.0f} €")
    print()
    
    # Use Case erstellen (UC1 - Nur Verbrauch)
    use_case = BESSUseCase(
        name="UC1 - Nur Verbrauch",
        description="Test Use Case",
        bess_size_mwh=bess_size_mwh,
        bess_power_mw=bess_power_mw,
        annual_cycles=730,  # 2 Zyklen/Tag * 365
        efficiency=0.85,
        market_participation={
            'srl_positive': 0.5,
            'srl_negative': 0.5,
            'sre_positive': 0.5,
            'sre_negative': 0.5,
            'intraday_trading': 0.5,
            'day_ahead': 0.3,
            'balancing_energy': 0.2
        },
        cost_factors={}
    )
    
    # Analyzer erstellen
    analyzer = EnhancedEconomicAnalyzer()
    
    print("MARKTPREISE:")
    print(f"  - SRL+: {analyzer.market_prices.get('srl_positive', 0):.2f} €/MW/h")
    print(f"  - SRL-: {analyzer.market_prices.get('srl_negative', 0):.2f} €/MW/h")
    print(f"  - SRE+: {analyzer.market_prices.get('sre_positive', 0):.2f} €/MWh")
    print(f"  - SRE-: {analyzer.market_prices.get('sre_negative', 0):.2f} €/MWh")
    print()
    
    # Jährliche Markterlöse berechnen (ohne Degradation)
    print("=" * 80)
    print("SCHRITT 1: JÄHRLICHE MARKTERLÖSE (ohne Degradation)")
    print("=" * 80)
    print()
    
    market_revenue = analyzer.calculate_market_revenue(use_case)
    
    print(f"SRL-Erlöse:")
    print(f"  - SRL+: {market_revenue.srl_positive:,.2f} €")
    print(f"  - SRL-: {market_revenue.srl_negative:,.2f} €")
    print(f"  - SRL gesamt: {market_revenue.srl_positive + market_revenue.srl_negative:,.2f} €")
    print()
    
    print(f"SRE-Erlöse:")
    print(f"  - SRE+: {market_revenue.sre_positive:,.2f} €")
    print(f"  - SRE-: {market_revenue.sre_negative:,.2f} €")
    print(f"  - SRE gesamt: {market_revenue.sre_positive + market_revenue.sre_negative:,.2f} €")
    print()
    
    print(f"Intraday-Erlöse:")
    print(f"  - Intraday Trading: {market_revenue.intraday_trading:,.2f} €")
    print()
    
    print(f"Day-Ahead-Erlöse:")
    print(f"  - Day-Ahead: {market_revenue.day_ahead:,.2f} €")
    print()
    
    print(f"Balancing-Erlöse:")
    print(f"  - Balancing Energy: {market_revenue.balancing_energy:,.2f} €")
    print()
    
    total_revenue_year = market_revenue.total_revenue()
    print(f"GESAMTERLÖS PRO JAHR: {total_revenue_year:,.2f} €")
    print()
    
    # Jährliche Kosten berechnen (ohne Degradation)
    print("=" * 80)
    print("SCHRITT 2: JÄHRLICHE KOSTEN (ohne Degradation)")
    print("=" * 80)
    print()
    
    cost_structure = analyzer.calculate_cost_structure(use_case, investment_costs)
    
    print(f"Betriebskosten: {cost_structure.operating_costs:,.2f} €")
    print(f"Wartungskosten: {cost_structure.maintenance_costs:,.2f} €")
    print(f"Netzentgelte: {cost_structure.grid_fees:,.2f} €")
    print(f"Versicherung: {cost_structure.insurance_costs:,.2f} €")
    print(f"Degradation: {cost_structure.degradation_costs:,.2f} €")
    print()
    
    total_costs_year = cost_structure.annual_operating_costs()
    print(f"GESAMTKOSTEN PRO JAHR: {total_costs_year:,.2f} €")
    print()
    
    net_cashflow_year = total_revenue_year - total_costs_year
    print(f"NETTO-CASHFLOW PRO JAHR: {net_cashflow_year:,.2f} €")
    print()
    
    # Simulation über 10 Jahre
    print("=" * 80)
    print("SCHRITT 3: SIMULATION ÜBER 10 JAHRE (mit Degradation)")
    print("=" * 80)
    print()
    
    results = analyzer.run_simulation(use_case, investment_costs, years=10)
    
    print("Jährliche Werte:")
    total_revenue_10y = 0
    total_costs_10y = 0
    
    for i, result in enumerate(results, 1):
        year_revenue = result.market_revenue.total_revenue()
        year_costs = result.cost_structure.annual_operating_costs()
        year_net = year_revenue - year_costs
        
        total_revenue_10y += year_revenue
        total_costs_10y += year_costs
        
        degradation_factor = (1 - 0.02) ** (i - 1)
        print(f"Jahr {i} (Degradation: {degradation_factor:.4f}):")
        print(f"  - Erlöse: {year_revenue:,.2f} €")
        print(f"  - Kosten: {year_costs:,.2f} €")
        print(f"  - Netto: {year_net:,.2f} €")
        print()
    
    print("=" * 80)
    print("ZUSAMMENFASSUNG ÜBER 10 JAHRE:")
    print("=" * 80)
    print()
    print(f"Gesamterlös (10 Jahre): {total_revenue_10y:,.2f} €")
    print(f"Gesamtkosten (10 Jahre): {total_costs_10y:,.2f} €")
    print(f"Netto-Cashflow (10 Jahre): {total_revenue_10y - total_costs_10y:,.2f} €")
    print()
    
    # Vergleich mit calculate_annual_balance
    from enhanced_economic_analysis import KPICalculator
    balance = KPICalculator.calculate_annual_balance(results)
    
    print("=" * 80)
    print("VERGLEICH MIT calculate_annual_balance():")
    print("=" * 80)
    print()
    print(f"total_revenue: {balance['total_revenue']:,.2f} €")
    print(f"total_costs: {balance['total_costs']:,.2f} €")
    print(f"net_cashflow: {balance['net_cashflow']:,.2f} €")
    print(f"cumulative_roi: {balance['cumulative_roi']:.2f} %")
    print()
    
    # Prüfe auf Einheitenprobleme
    print("=" * 80)
    print("EINHEITEN-PRÜFUNG:")
    print("=" * 80)
    print()
    print(f"BESS-Power in MW: {bess_power_mw} MW")
    print(f"BESS-Power in kW: {bess_power_mw * 1000} kW")
    print(f"BESS-Size in MWh: {bess_size_mwh} MWh")
    print(f"BESS-Size in kWh: {bess_size_mwh * 1000} kWh")
    print()
    
    # Prüfe SRL-Berechnung
    print("SRL-Berechnung (Beispiel Jahr 1):")
    availability_hours = 8000
    srl_price = analyzer.market_prices.get('srl_positive', 18.0)
    srl_participation = use_case.market_participation.get('srl_positive', 0.5)
    
    srl_calc = bess_power_mw * availability_hours * srl_price * srl_participation
    print(f"  Formel: {bess_power_mw} MW * {availability_hours} h * {srl_price} €/MW/h * {srl_participation}")
    print(f"  Ergebnis: {srl_calc:,.2f} €")
    print()
    
    # Prüfe Intraday-Berechnung
    print("Intraday-Berechnung (Beispiel Jahr 1):")
    try:
        from app.routes import get_market_prices
        db_prices = get_market_prices(None)
        
        bess_capacity_kwh = bess_size_mwh * 1000
        daily_cycles = use_case.annual_cycles / 365
        spot_arbitrage_price = db_prices.get('spot_arbitrage_price', 0.0074)
        
        spot_calc = bess_capacity_kwh * daily_cycles * 365 * spot_arbitrage_price * use_case.efficiency
        print(f"  Spot-Arbitrage:")
        print(f"    Formel: {bess_capacity_kwh} kWh * {daily_cycles:.2f} Zyklen/Tag * 365 Tage * {spot_arbitrage_price} €/kWh * {use_case.efficiency}")
        print(f"    Ergebnis: {spot_calc:,.2f} €")
        print()
        
        balancing_energy_price = db_prices.get('balancing_energy_price', 0.0231)
        bess_power_kw = bess_power_mw * 1000
        balancing_calc = bess_power_kw * 8760 * balancing_energy_price / 1000 * use_case.efficiency
        print(f"  Balancing Energy:")
        print(f"    Formel: {bess_power_kw} kW * 8760 h * {balancing_energy_price} €/kWh / 1000 * {use_case.efficiency}")
        print(f"    Ergebnis: {balancing_calc:,.2f} €")
        print()
    except Exception as e:
        print(f"  Fehler bei Intraday-Berechnung: {e}")
        print()

if __name__ == "__main__":
    debug_net_cashflow()

