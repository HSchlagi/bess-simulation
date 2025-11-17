#!/usr/bin/env python3
"""
Debug-Skript für Gesamterlös-Berechnung

Prueft, wie der Gesamterlös in den Vergleichsmetriken berechnet wird.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_gesamterloes():
    """Debuggt die Gesamterlös-Berechnung"""
    
    try:
        from app import create_app
        from models import Project, InvestmentCost, UseCase
        from enhanced_economic_analysis import EnhancedEconomicAnalyzer
        
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
            
            # Use Cases aus der Datenbank laden
            db_use_cases = UseCase.query.filter_by(project_id=project.id).all()
            
            print("=" * 80)
            print("DEBUG: GESAMTERLOES BERECHNUNG")
            print("=" * 80)
            print()
            print(f"Projekt: {project.name} (ID: {project.id})")
            print(f"Use Cases gefunden: {len(db_use_cases)}")
            for uc in db_use_cases:
                print(f"  - {uc.name} (ID: {uc.id})")
            print()
            
            # Analyzer erstellen
            analyzer = EnhancedEconomicAnalyzer(project_id=project.id)
            
            # Analyse durchführen
            analysis_results = analyzer.generate_comprehensive_analysis(project_data, db_use_cases)
            
            print("=" * 80)
            print("USE CASES ERGEBNISSE")
            print("=" * 80)
            print()
            
            for use_case_name, data in analysis_results['use_cases'].items():
                balance = data['annual_balance']
                print(f"{use_case_name}:")
                print(f"  Gesamterlös (10 Jahre): {balance['total_revenue']:,.2f} EUR")
                print(f"  Gesamtkosten (10 Jahre): {balance['total_costs']:,.2f} EUR")
                print(f"  Netto-Cashflow (10 Jahre): {balance['net_cashflow']:,.2f} EUR")
                print(f"  ROI: {balance['cumulative_roi']:.1f}%")
                print()
            
            print("=" * 80)
            print("VERGLEICHSMETRIKEN")
            print("=" * 80)
            print()
            
            metrics = analysis_results['comparison_metrics']
            print(f"Beste ROI: {metrics['best_roi']:.1f}%")
            print(f"Bester Use Case: {metrics['best_use_case']}")
            print()
            print(f"Total Comparison:")
            print(f"  Gesamterlös: {metrics['total_comparison']['total_revenue']:,.2f} EUR")
            print(f"  Gesamtkosten: {metrics['total_comparison']['total_costs']:,.2f} EUR")
            print(f"  Investitionskosten: {metrics['total_comparison']['total_investment']:,.2f} EUR")
            print()
            
            # Pruefe, ob der Gesamterlös korrekt ist
            best_use_case_name = metrics['best_use_case']
            if best_use_case_name:
                best_use_case_data = analysis_results['use_cases'].get(best_use_case_name)
                if best_use_case_data:
                    expected_revenue = best_use_case_data['annual_balance']['total_revenue']
                    actual_revenue = metrics['total_comparison']['total_revenue']
                    
                    print("=" * 80)
                    print("VALIDIERUNG")
                    print("=" * 80)
                    print()
                    print(f"Erwarteter Gesamterlös (vom besten Use Case): {expected_revenue:,.2f} EUR")
                    print(f"Tatsaechlicher Gesamterlös (in Vergleichsmetriken): {actual_revenue:,.2f} EUR")
                    print()
                    
                    if abs(expected_revenue - actual_revenue) < 0.01:
                        print("OK: Gesamterlös ist korrekt!")
                    else:
                        print(f"FEHLER: Gesamterlös weicht ab!")
                        print(f"  Differenz: {abs(expected_revenue - actual_revenue):,.2f} EUR")
            
    except Exception as e:
        print(f"Fehler: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    debug_gesamterloes()

