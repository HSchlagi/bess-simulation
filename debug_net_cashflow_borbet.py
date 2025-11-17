#!/usr/bin/env python3
"""
Debug-Skript für Netto-Cashflow Berechnung (BORBET)

Prüft, warum der Netto-Cashflow (234.601.104 €) so viel höher ist als die
Gesamterlöse aus der 10-Jahres-Analyse (30.279.838,90 €).
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_use_case_calculation():
    """Debuggt die Use Case Berechnung für BORBET"""
    
    try:
        from app import create_app
        from models import Project, InvestmentCost
        from enhanced_economic_analysis import EnhancedEconomicAnalyzer, BESSUseCase
        
        app = create_app()
        with app.app_context():
            # BORBET-Projekt laden
            project = Project.query.filter(Project.name.ilike('%BORBET%')).first()
            
            if not project:
                print("BORBET-Projekt nicht gefunden!")
                return
            
            # Investitionskosten
            investment_costs = InvestmentCost.query.filter_by(project_id=project.id).all()
            total_investment = sum(cost.cost_eur for cost in investment_costs)
            
            # Projektparameter
            bess_size_mwh = (project.bess_size or 0) / 1000
            bess_power_mw = (project.bess_power or 0) / 1000
            daily_cycles = getattr(project, 'daily_cycles', 1.2)
            annual_cycles = daily_cycles * 365
            
            print("=" * 80)
            print("DEBUG: USE CASE BERECHNUNG (BORBET)")
            print("=" * 80)
            print()
            print(f"Projekt: {project.name}")
            print(f"BESS-Kapazitaet: {bess_size_mwh:.2f} MWh")
            print(f"BESS-Leistung: {bess_power_mw:.2f} MW")
            print(f"Investitionskosten: {total_investment:,.2f} EUR")
            print(f"Tägliche Zyklen: {daily_cycles:.2f}")
            print(f"Jahreszyklen: {annual_cycles:.0f}")
            print()
            
            # Analyzer erstellen
            analyzer = EnhancedEconomicAnalyzer(project_id=project.id)
            
            # Use Case erstellen (UC1 - Nur Verbrauch)
            use_case = BESSUseCase(
                name="UC1 - Nur Verbrauch",
                description="Test Use Case",
                bess_size_mwh=bess_size_mwh,
                bess_power_mw=bess_power_mw,
                annual_cycles=annual_cycles,
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
            
            print("=" * 80)
            print("JAEHRLICHE ERLOESE (OHNE DEGRADATION)")
            print("=" * 80)
            print()
            
            # Markterlöse berechnen
            market_revenue = analyzer.calculate_market_revenue(use_case)
            
            print(f"SRL-Erloese:")
            print(f"  SRL+ (positiv): {market_revenue.srl_positive:,.2f} EUR/Jahr")
            print(f"  SRL- (negativ): {market_revenue.srl_negative:,.2f} EUR/Jahr")
            print(f"  SRL Gesamt: {market_revenue.srl_positive + market_revenue.srl_negative:,.2f} EUR/Jahr")
            print()
            
            print(f"SRE-Erloese:")
            print(f"  SRE+ (positiv): {market_revenue.sre_positive:,.2f} EUR/Jahr")
            print(f"  SRE- (negativ): {market_revenue.sre_negative:,.2f} EUR/Jahr")
            print(f"  SRE Gesamt: {market_revenue.sre_positive + market_revenue.sre_negative:,.2f} EUR/Jahr")
            print()
            
            print(f"Intraday-Erloese:")
            print(f"  Intraday Trading: {market_revenue.intraday_trading:,.2f} EUR/Jahr")
            print()
            
            print(f"Day-Ahead-Erloese:")
            print(f"  Day-Ahead: {market_revenue.day_ahead:,.2f} EUR/Jahr")
            print()
            
            print(f"Balancing-Erloese:")
            print(f"  Balancing Energy: {market_revenue.balancing_energy:,.2f} EUR/Jahr")
            print()
            
            total_revenue_year = market_revenue.total_revenue()
            print(f"GESAMTERLOES PRO JAHR: {total_revenue_year:,.2f} EUR/Jahr")
            print()
            
            print("=" * 80)
            print("JAEHRLICHE KOSTEN (OHNE DEGRADATION)")
            print("=" * 80)
            print()
            
            # Kostenstruktur berechnen
            cost_structure = analyzer.calculate_cost_structure(use_case, total_investment)
            
            print(f"Betriebskosten: {cost_structure.operating_costs:,.2f} EUR/Jahr")
            print(f"Wartungskosten: {cost_structure.maintenance_costs:,.2f} EUR/Jahr")
            print(f"Netzentgelte: {cost_structure.grid_fees:,.2f} EUR/Jahr")
            print(f"Versicherung: {cost_structure.insurance_costs:,.2f} EUR/Jahr")
            print(f"Degradation: {cost_structure.degradation_costs:,.2f} EUR/Jahr")
            print()
            
            total_costs_year = cost_structure.annual_operating_costs()
            print(f"GESAMTKOSTEN PRO JAHR: {total_costs_year:,.2f} EUR/Jahr")
            print()
            
            print("=" * 80)
            print("NETTO-CASHFLOW PRO JAHR (OHNE DEGRADATION)")
            print("=" * 80)
            print()
            
            net_cashflow_year = total_revenue_year - total_costs_year
            print(f"Netto-Cashflow (ohne Investition): {net_cashflow_year:,.2f} EUR/Jahr")
            print(f"Netto-Cashflow (mit Investition): {net_cashflow_year - total_investment:,.2f} EUR/Jahr")
            print()
            
            print("=" * 80)
            print("UEBER 10 JAHRE (MIT DEGRADATION)")
            print("=" * 80)
            print()
            
            # Simulation über 10 Jahre
            results = analyzer.run_simulation(use_case, total_investment, years=10)
            
            # Summen berechnen
            total_revenue_10y = sum(r.market_revenue.total_revenue() for r in results)
            total_costs_10y = sum(r.cost_structure.annual_operating_costs() for r in results)
            
            print(f"Gesamterloese (10 Jahre): {total_revenue_10y:,.2f} EUR")
            print(f"Gesamtkosten (10 Jahre): {total_costs_10y:,.2f} EUR")
            print(f"Investitionskosten: {total_investment:,.2f} EUR")
            print()
            
            net_cashflow_10y = total_revenue_10y - total_costs_10y - total_investment
            print(f"Netto-Cashflow (10 Jahre, MIT Investition): {net_cashflow_10y:,.2f} EUR")
            print()
            
            # Vergleich mit angezeigten Werten
            print("=" * 80)
            print("VERGLEICH MIT ANGEZEIGTEN WERTEN")
            print("=" * 80)
            print()
            
            print(f"Angezeigter Netto-Cashflow: 234.601.104 EUR")
            print(f"Berechneter Netto-Cashflow: {net_cashflow_10y:,.2f} EUR")
            print(f"Differenz: {234601104 - net_cashflow_10y:,.2f} EUR")
            print()
            
            # Prüfe, ob Investitionskosten abgezogen werden
            net_cashflow_without_investment = total_revenue_10y - total_costs_10y
            print(f"Netto-Cashflow OHNE Investition: {net_cashflow_without_investment:,.2f} EUR")
            print()
            
            if abs(net_cashflow_without_investment - 234601104) < abs(net_cashflow_10y - 234601104):
                print("WARNUNG: Investitionskosten werden NICHT abgezogen!")
                print(f"  Der angezeigte Wert ({234601104:,.0f} EUR) entspricht eher")
                print(f"  dem Netto-Cashflow OHNE Investition ({net_cashflow_without_investment:,.0f} EUR)")
            else:
                print("OK: Investitionskosten werden korrekt abgezogen.")
            
            print()
            
            # Prüfe jährliche Werte
            print("=" * 80)
            print("JAEHRLICHE WERTE (MIT DEGRADATION)")
            print("=" * 80)
            print()
            
            for i, result in enumerate(results[:5], 1):  # Nur erste 5 Jahre
                revenue = result.market_revenue.total_revenue()
                costs = result.cost_structure.annual_operating_costs()
                net = revenue - costs
                print(f"Jahr {i}:")
                print(f"  Erlöse: {revenue:,.2f} EUR")
                print(f"  Kosten: {costs:,.2f} EUR")
                print(f"  Netto (ohne Investition): {net:,.2f} EUR")
                print()
            
            # Prüfe, ob Werte mehrfach summiert werden
            print("=" * 80)
            print("PRUEFUNG: MEHRFACHE SUMMIERUNG?")
            print("=" * 80)
            print()
            
            # Erwarteter Gesamterlös (10 Jahre)
            expected_total_revenue = total_revenue_year * sum((0.98 ** i) for i in range(10))
            print(f"Erwarteter Gesamterlös (10 Jahre): {expected_total_revenue:,.2f} EUR")
            print(f"Tatsächlicher Gesamterlös (10 Jahre): {total_revenue_10y:,.2f} EUR")
            print()
            
            if abs(total_revenue_10y - expected_total_revenue) > expected_total_revenue * 0.1:
                print("WARNUNG: Gesamterlös weicht stark ab!")
                print(f"  Differenz: {abs(total_revenue_10y - expected_total_revenue):,.2f} EUR")
            else:
                print("OK: Gesamterlös ist im erwarteten Bereich.")
            
            print()
            
    except Exception as e:
        print(f"Fehler: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    debug_use_case_calculation()

