#!/usr/bin/env python3
"""
Validierungsskript für BORBET-Projekt Werte

Dieses Skript lädt die tatsächlichen BORBET-Projektparameter aus der Datenbank
und validiert die Use Case Vergleich Werte mit den korrekten Parametern.
"""

import sys
import os

# Füge das Projektverzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def load_borbet_project():
    """Lädt BORBET-Projektparameter aus der Datenbank"""
    try:
        from app import create_app
        from models import Project, InvestmentCost
        
        app = create_app()
        with app.app_context():
            # Suche BORBET-Projekt
            project = Project.query.filter(
                Project.name.ilike('%BORBET%')
            ).first()
            
            if not project:
                print("❌ BORBET-Projekt nicht gefunden!")
                return None
            
            # Investitionskosten laden
            investment_costs = InvestmentCost.query.filter_by(project_id=project.id).all()
            total_investment = sum(cost.cost_eur for cost in investment_costs)
            
            # Projektparameter
            project_params = {
                'id': project.id,
                'name': project.name,
                'bess_size_kwh': project.bess_size or 0,
                'bess_power_kw': project.bess_power or 0,
                'bess_size_mwh': (project.bess_size or 0) / 1000,
                'bess_power_mw': (project.bess_power or 0) / 1000,
                'total_investment': total_investment,
                'pv_power': project.pv_power or 0,
                'daily_cycles': getattr(project, 'daily_cycles', 1.2)
            }
            
            print("=" * 80)
            print("BORBET PROJEKTPARAMETER")
            print("=" * 80)
            print()
            print(f"Projekt ID: {project_params['id']}")
            print(f"Projekt Name: {project_params['name']}")
            print(f"BESS-Kapazität: {project_params['bess_size_kwh']:,.0f} kWh ({project_params['bess_size_mwh']:.2f} MWh)")
            print(f"BESS-Leistung: {project_params['bess_power_kw']:,.0f} kW ({project_params['bess_power_mw']:.2f} MW)")
            print(f"Investitionskosten: {project_params['total_investment']:,.2f} €")
            print(f"PV-Leistung: {project_params['pv_power']:,.0f} kW")
            print(f"Tägliche Zyklen: {project_params['daily_cycles']:.2f}")
            print()
            
            # Investitionskosten-Details
            if investment_costs:
                print("Investitionskosten-Details:")
                for cost in investment_costs:
                    print(f"  {cost.component_type}: {cost.cost_eur:,.2f} €")
                print()
            
            return project_params
            
    except Exception as e:
        print(f"❌ Fehler beim Laden der Projektparameter: {e}")
        import traceback
        traceback.print_exc()
        return None

def validate_with_actual_params(project_params):
    """Validiert die Use Case Werte mit den tatsächlichen Projektparametern"""
    
    if not project_params:
        print("❌ Keine Projektparameter verfügbar!")
        return
    
    print("=" * 80)
    print("VALIDIERUNG MIT TATSÄCHLICHEN PARAMETERN")
    print("=" * 80)
    print()
    
    # Projektparameter
    bess_size_mwh = project_params['bess_size_mwh']
    bess_power_mw = project_params['bess_power_mw']
    investment = project_params['total_investment']
    daily_cycles = project_params['daily_cycles']
    annual_cycles = daily_cycles * 365
    
    print(f"Berechnungsgrundlagen:")
    print(f"  BESS-Kapazität: {bess_size_mwh:.2f} MWh")
    print(f"  BESS-Leistung: {bess_power_mw:.2f} MW")
    print(f"  Investitionskosten: {investment:,.2f} €")
    print(f"  Tägliche Zyklen: {daily_cycles:.2f}")
    print(f"  Jahreszyklen: {annual_cycles:.0f}")
    print()
    
    # Erwartete jährliche Erlöse (ohne Degradation)
    # Basierend auf Standard-Marktpreisen
    print("Erwartete jährliche Erlöse (ohne Degradation):")
    print("-" * 80)
    
    # SRL-Erlöse
    availability_hours = 8000
    srl_price = 0.018  # €/MW/h
    srl_positive = bess_power_mw * availability_hours * srl_price * 0.5
    srl_negative = bess_power_mw * availability_hours * srl_price * 0.5
    srl_total = srl_positive + srl_negative
    print(f"  SRL (positiv + negativ): {srl_total:,.2f} €/Jahr")
    
    # SRE-Erlöse
    activation_energy_mwh = 250
    sre_price = 80.0  # €/MWh
    sre_positive = activation_energy_mwh * sre_price * 0.5
    sre_negative = activation_energy_mwh * sre_price * 0.5
    sre_total = sre_positive + sre_negative
    print(f"  SRE (positiv + negativ): {sre_total:,.2f} €/Jahr")
    
    # Intraday-Erlöse
    bess_capacity_kwh = bess_size_mwh * 1000
    efficiency = 0.85
    
    # Spot-Arbitrage
    spot_arbitrage_price = 0.0074  # €/kWh
    spot_arbitrage_revenue = bess_capacity_kwh * daily_cycles * 365 * spot_arbitrage_price * efficiency
    
    # Intraday-Trading
    intraday_trading_price = 0.0111  # €/kWh
    intraday_trading_revenue = bess_capacity_kwh * daily_cycles * 365 * intraday_trading_price * efficiency
    
    # Balancing Energy
    bess_power_kw = bess_power_mw * 1000
    balancing_energy_price = 0.0231  # €/kWh
    balancing_energy_revenue = bess_power_kw * 8760 * balancing_energy_price / 1000 * efficiency
    
    intraday_total = (spot_arbitrage_revenue + intraday_trading_revenue + balancing_energy_revenue) * 0.5
    print(f"  Intraday (Spot + Trading + Balancing): {intraday_total:,.2f} €/Jahr")
    
    # Day-Ahead
    day_ahead_price = 50.0  # €/MWh
    day_ahead_revenue = bess_size_mwh * annual_cycles * day_ahead_price * 0.3
    print(f"  Day-Ahead: {day_ahead_revenue:,.2f} €/Jahr")
    
    # Balancing
    balancing_price = 23.1  # €/MWh
    balancing_revenue = bess_power_mw * 8760 * balancing_price * 0.2
    print(f"  Balancing: {balancing_revenue:,.2f} €/Jahr")
    
    # Gesamterlös pro Jahr
    total_revenue_year = srl_total + sre_total + intraday_total + day_ahead_revenue + balancing_revenue
    print(f"  GESAMT: {total_revenue_year:,.2f} €/Jahr")
    print()
    
    # Erwartete jährliche Kosten (ohne Degradation)
    print("Erwartete jährliche Kosten (ohne Degradation):")
    print("-" * 80)
    
    # Betriebskosten
    operating_costs = (bess_size_mwh * 1000 + bess_power_mw * 100) * 0.02
    print(f"  Betriebskosten: {operating_costs:,.2f} €/Jahr")
    
    # Wartungskosten
    maintenance_costs = investment * 0.015
    print(f"  Wartungskosten: {maintenance_costs:,.2f} €/Jahr")
    
    # Netzentgelte
    energy_throughput = bess_size_mwh * annual_cycles
    grid_fees = energy_throughput * 15.0
    print(f"  Netzentgelte: {grid_fees:,.2f} €/Jahr")
    
    # Versicherung
    insurance_costs = investment * 0.005
    print(f"  Versicherung: {insurance_costs:,.2f} €/Jahr")
    
    # Degradation
    degradation_costs = investment * 0.02
    print(f"  Degradation: {degradation_costs:,.2f} €/Jahr")
    
    # Gesamtkosten pro Jahr
    total_costs_year = operating_costs + maintenance_costs + grid_fees + insurance_costs + degradation_costs
    print(f"  GESAMT: {total_costs_year:,.2f} €/Jahr")
    print()
    
    # Netto-Cashflow pro Jahr (ohne Degradation)
    net_cashflow_year = total_revenue_year - total_costs_year
    print(f"Netto-Cashflow pro Jahr (ohne Degradation): {net_cashflow_year:,.2f} €/Jahr")
    print()
    
    # Über 10 Jahre (mit Degradation)
    print("Über 10 Jahre (mit Degradation):")
    print("-" * 80)
    
    degradation_rate = 0.02
    degradation_factors = [(1 - degradation_rate) ** i for i in range(10)]
    
    total_revenue_10y = sum(total_revenue_year * df for df in degradation_factors)
    total_costs_10y = sum(total_costs_year * df for df in degradation_factors)
    
    print(f"  Gesamterlöse (10 Jahre): {total_revenue_10y:,.2f} €")
    print(f"  Gesamtkosten (10 Jahre): {total_costs_10y:,.2f} €")
    print(f"  Investitionskosten: {investment:,.2f} €")
    print()
    
    # Netto-Cashflow über 10 Jahre
    net_cashflow_10y = total_revenue_10y - total_costs_10y - investment
    print(f"Netto-Cashflow über 10 Jahre: {net_cashflow_10y:,.2f} €")
    print()
    
    # ROI
    roi = (net_cashflow_10y / investment * 100) if investment > 0 else 0
    print(f"ROI: {roi:.2f}%")
    print()
    
    # Vergleich mit angezeigten Werten
    print("=" * 80)
    print("VERGLEICH MIT ANGEZEIGTEN WERTEN")
    print("=" * 80)
    print()
    
    print("Angezeigte Werte (aus Screenshot):")
    print(f"  UC1 Netto-Cashflow: 11.364.535 €")
    print(f"  UC2 Netto-Cashflow: -4.769.798 €")
    print(f"  UC3 Netto-Cashflow: -4.800.905 €")
    print(f"  Gesamterlös: 22.263.463 €")
    print()
    
    print("Berechnete Werte (mit tatsächlichen Parametern):")
    print(f"  Netto-Cashflow (10 Jahre): {net_cashflow_10y:,.2f} €")
    print(f"  Gesamterlös (10 Jahre): {total_revenue_10y:,.2f} €")
    print()
    
    # Abweichungen
    print("Abweichungen:")
    print("-" * 80)
    
    if abs(net_cashflow_10y - 11364535) < abs(net_cashflow_10y - (-7000000)):
        print(f"  OK: Netto-Cashflow ist naeher an UC1 (11.364.535 EUR) als an erwartetem Wert")
    else:
        print(f"  WARNUNG: Netto-Cashflow weicht stark ab:")
        print(f"     Erwartet: {net_cashflow_10y:,.2f} €")
        print(f"     Angezeigt: 11.364.535 €")
        print(f"     Differenz: {11364535 - net_cashflow_10y:,.2f} €")
    
    print()
    
    # Prüfe, ob Investitionskosten abgezogen werden
    net_cashflow_without_investment = total_revenue_10y - total_costs_10y
    print(f"Netto-Cashflow OHNE Investitionskosten: {net_cashflow_without_investment:,.2f} €")
    print(f"Netto-Cashflow MIT Investitionskosten: {net_cashflow_10y:,.2f} €")
    print()
    
    if abs(net_cashflow_without_investment - 11364535) < abs(net_cashflow_10y - 11364535):
        print("WARNUNG: Es scheint, dass die Investitionskosten NICHT abgezogen werden!")
        print("   Der angezeigte Wert entspricht eher dem Netto-Cashflow OHNE Investition.")
    else:
        print("OK: Investitionskosten werden korrekt abgezogen.")
    
    print()

if __name__ == '__main__':
    print("Lade BORBET-Projektparameter aus der Datenbank...")
    print()
    
    project_params = load_borbet_project()
    
    if project_params:
        validate_with_actual_params(project_params)
    else:
        print("❌ Konnte Projektparameter nicht laden!")

