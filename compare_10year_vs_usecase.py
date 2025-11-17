#!/usr/bin/env python3
"""
Vergleicht die Berechnungen zwischen 10-Jahres-Report und Use Case Vergleich
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def compare_calculations():
    """Vergleicht die Berechnungen"""
    
    try:
        from app import create_app
        from models import Project, InvestmentCost
        from app.routes import calculate_10_year_revenue_potential, get_market_prices
        
        app = create_app()
        with app.app_context():
            # BORBET-Projekt laden
            project = Project.query.filter(Project.name.ilike('%BORBET%')).first()
            
            if not project:
                print("BORBET-Projekt nicht gefunden!")
                return
            
            print("=" * 80)
            print("VERGLEICH: 10-JAHRES-REPORT vs. USE CASE VERGLEICH")
            print("=" * 80)
            print()
            print(f"Projekt: {project.name}")
            print(f"BESS-Kapazitaet: {project.bess_size / 1000:.2f} MWh")
            print(f"BESS-Leistung: {project.bess_power / 1000:.2f} MW")
            print()
            
            # 10-Jahres-Report berechnen
            print("=" * 80)
            print("10-JAHRES-REPORT")
            print("=" * 80)
            print()
            
            report_data = calculate_10_year_revenue_potential(project, use_case='hybrid')
            
            if report_data:
                sum_10y = report_data.get('sum_10y', {})
                total_revenue_10y = sum_10y.get('total_revenue', 0)
                
                print(f"Summe Erlöse (10 Jahre): {total_revenue_10y:,.2f} EUR")
                print()
                
                # Detaillierte Aufschlüsselung
                print("Detaillierte Aufschlüsselung (10 Jahre):")
                print(f"  SRL-Erlöse: {sum_10y.get('srl_negative', 0):,.2f} EUR")
                print(f"  SRL+Erlöse: {sum_10y.get('srl_positive', 0):,.2f} EUR")
                print(f"  SRE-Erlöse: {sum_10y.get('sre_negative', 0):,.2f} EUR")
                print(f"  SRE+Erlöse: {sum_10y.get('sre_positive', 0):,.2f} EUR")
                print(f"  Intraday-Erlöse: {sum_10y.get('intraday_storage_strategy', 0):,.2f} EUR")
                print()
            
            # Use Case Vergleich berechnen
            print("=" * 80)
            print("USE CASE VERGLEICH (BORBET UC1 Batterie)")
            print("=" * 80)
            print()
            
            from models import UseCase
            from enhanced_economic_analysis import EnhancedEconomicAnalyzer
            
            # UC1 Use Case laden
            uc1 = UseCase.query.filter_by(project_id=project.id, name='BORBET UC1 Batterie').first()
            
            if uc1:
                # Investitionskosten
                investment_costs = InvestmentCost.query.filter_by(project_id=project.id).all()
                total_investment = sum(cost.cost_eur for cost in investment_costs)
                
                # Projektdaten
                project_data = {
                    'bess_size': project.bess_size or 1000,
                    'bess_power': project.bess_power or 500,
                    'total_investment': total_investment,
                    'location': project.location or 'Unbekannt',
                    'pv_power': project.pv_power or 0,
                    'hydro_power': project.hydro_power or 0,
                    'wind_power': project.wind_power or 0,
                    'hp_power': project.hp_power or 0
                }
                
                # Analyzer
                analyzer = EnhancedEconomicAnalyzer(project_id=project.id)
                
                # Use Case aus Datenbank erstellen
                bess_size_mwh = (project.bess_size or 0) / 1000
                bess_power_mw = (project.bess_power or 0) / 1000
                use_case = analyzer.create_use_case_from_database(uc1, bess_size_mwh, bess_power_mw)
                
                # Simulation durchführen
                # WICHTIG: 11 Jahre, da der 10-Jahres-Report 11 Jahre berechnet (Bezugsjahr + 10 Projektionsjahre)
                results = analyzer.run_simulation(use_case, total_investment, years=11)
                
                # Summen berechnen
                total_revenue_10y = sum(r.market_revenue.total_revenue() for r in results)
                
                print(f"Gesamterlöse (11 Jahre): {total_revenue_10y:,.2f} EUR")
                print()
                
                # Detaillierte Aufschlüsselung
                print("Detaillierte Aufschlüsselung (10 Jahre):")
                srl_positive_total = sum(r.market_revenue.srl_positive for r in results)
                srl_negative_total = sum(r.market_revenue.srl_negative for r in results)
                sre_positive_total = sum(r.market_revenue.sre_positive for r in results)
                sre_negative_total = sum(r.market_revenue.sre_negative for r in results)
                intraday_total = sum(r.market_revenue.intraday_trading for r in results)
                day_ahead_total = sum(r.market_revenue.day_ahead for r in results)
                balancing_total = sum(r.market_revenue.balancing_energy for r in results)
                
                print(f"  SRL-Erlöse: {srl_negative_total:,.2f} EUR")
                print(f"  SRL+Erlöse: {srl_positive_total:,.2f} EUR")
                print(f"  SRE-Erlöse: {sre_negative_total:,.2f} EUR")
                print(f"  SRE+Erlöse: {sre_positive_total:,.2f} EUR")
                print(f"  Intraday-Erlöse: {intraday_total:,.2f} EUR")
                print(f"  Day-Ahead-Erlöse: {day_ahead_total:,.2f} EUR")
                print(f"  Balancing-Erlöse: {balancing_total:,.2f} EUR")
                print()
            
            # Vergleich
            print("=" * 80)
            print("VERGLEICH")
            print("=" * 80)
            print()
            
            if report_data and uc1:
                report_revenue = sum_10y.get('total_revenue', 0)
                usecase_revenue = total_revenue_10y
                
                print(f"10-Jahres-Report Gesamterlös: {report_revenue:,.2f} EUR")
                print(f"Use Case Vergleich Gesamterlös: {usecase_revenue:,.2f} EUR")
                print(f"Differenz: {abs(report_revenue - usecase_revenue):,.2f} EUR")
                print(f"Prozentuale Abweichung: {abs(report_revenue - usecase_revenue) / report_revenue * 100:.1f}%")
                print()
                
                if abs(report_revenue - usecase_revenue) > report_revenue * 0.1:
                    print("WARNUNG: Große Abweichung zwischen den beiden Berechnungen!")
                    print("Moegliche Ursachen:")
                    print("  1. Unterschiedliche Marktpreise")
                    print("  2. Unterschiedliche Formeln")
                    print("  3. Unterschiedliche Degradation")
                    print("  4. Unterschiedliche Marktteilnahme-Raten")
            
    except Exception as e:
        print(f"Fehler: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    compare_calculations()

