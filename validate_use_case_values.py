#!/usr/bin/env python3
"""
Validierungsskript für Use Case Vergleich Werte

Dieses Skript prüft die Konsistenz und Realitätsnähe der berechneten Werte
im Use Case Vergleich.
"""

import sys
import os

# Füge das Projektverzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def validate_net_cashflow(net_cashflow, total_revenue, total_costs, investment):
    """
    Validiert den Netto-Cashflow
    
    Args:
        net_cashflow: Berechneter Netto-Cashflow
        total_revenue: Gesamterlöse über 10 Jahre
        total_costs: Gesamtkosten über 10 Jahre
        investment: Investitionskosten
    
    Returns:
        dict: Validierungsergebnis
    """
    issues = []
    warnings = []
    
    # Erwarteter Netto-Cashflow
    expected_net_cashflow = total_revenue - total_costs - investment
    
    # Prüfe 1: Netto-Cashflow sollte gleich erwartetem Wert sein
    if abs(net_cashflow - expected_net_cashflow) > 0.01:
        issues.append(
            f"❌ FEHLER: Netto-Cashflow ({net_cashflow:,.2f} €) stimmt nicht mit erwartetem Wert ({expected_net_cashflow:,.2f} €) überein!"
        )
        issues.append(
            f"   Berechnung: {total_revenue:,.2f} € (Erlöse) - {total_costs:,.2f} € (Kosten) - {investment:,.2f} € (Investition) = {expected_net_cashflow:,.2f} €"
        )
    
    # Prüfe 2: Netto-Cashflow sollte realistisch sein
    # Netto-Cashflow sollte nicht größer sein als 2x Investition (für positive Werte)
    if net_cashflow > 0 and net_cashflow > investment * 2:
        warnings.append(
            f"⚠️ WARNUNG: Netto-Cashflow ({net_cashflow:,.2f} €) ist sehr hoch (> 2x Investition: {investment * 2:,.2f} €)"
        )
    
    # Prüfe 3: Netto-Cashflow sollte nicht kleiner sein als -2x Investition (für negative Werte)
    if net_cashflow < 0 and abs(net_cashflow) > investment * 2:
        warnings.append(
            f"⚠️ WARNUNG: Netto-Cashflow ({net_cashflow:,.2f} €) ist sehr negativ (< -2x Investition: {-investment * 2:,.2f} €)"
        )
    
    return {
        'valid': len(issues) == 0,
        'issues': issues,
        'warnings': warnings,
        'expected_net_cashflow': expected_net_cashflow,
        'actual_net_cashflow': net_cashflow
    }

def validate_total_revenue(total_revenue, investment, bess_size_mwh, bess_power_mw):
    """
    Validiert den Gesamterlös
    
    Args:
        total_revenue: Gesamterlös über 10 Jahre
        investment: Investitionskosten
        bess_size_mwh: BESS-Kapazität in MWh
        bess_power_mw: BESS-Leistung in MW
    
    Returns:
        dict: Validierungsergebnis
    """
    issues = []
    warnings = []
    
    # Erwartete jährliche Erlöse (ohne Degradation)
    # Basierend auf Standard-Marktpreisen
    expected_annual_revenue = (
        288 +  # SRL
        20000 +  # SRE
        46138 +  # Intraday
        87600 +  # Day-Ahead
        80942  # Balancing
    )  # ~234.968 €/Jahr
    
    # Mit Degradation über 10 Jahre: ~2.100.000 €
    degradation_factor_sum = sum((0.98 ** i) for i in range(10))  # Summe der Degradationsfaktoren
    expected_total_revenue = expected_annual_revenue * degradation_factor_sum
    
    # Prüfe 1: Gesamterlös sollte im erwarteten Bereich sein
    if total_revenue < expected_total_revenue * 0.5:
        warnings.append(
            f"⚠️ WARNUNG: Gesamterlös ({total_revenue:,.2f} €) ist niedriger als erwartet (~{expected_total_revenue:,.2f} €)"
        )
    elif total_revenue > expected_total_revenue * 2:
        warnings.append(
            f"⚠️ WARNUNG: Gesamterlös ({total_revenue:,.2f} €) ist höher als erwartet (~{expected_total_revenue:,.2f} €)"
        )
    
    # Prüfe 2: Gesamterlös sollte nicht größer sein als 10x Investition
    if total_revenue > investment * 10:
        issues.append(
            f"❌ FEHLER: Gesamterlös ({total_revenue:,.2f} €) ist unrealistisch hoch (> 10x Investition: {investment * 10:,.2f} €)"
        )
    
    # Prüfe 3: Gesamterlös pro MWh sollte realistisch sein
    revenue_per_mwh = total_revenue / (bess_size_mwh * 10) if bess_size_mwh > 0 else 0
    if revenue_per_mwh > 50000:  # > 50.000 €/MWh über 10 Jahre
        warnings.append(
            f"⚠️ WARNUNG: Gesamterlös pro MWh ({revenue_per_mwh:,.2f} €/MWh) ist sehr hoch"
        )
    
    return {
        'valid': len(issues) == 0,
        'issues': issues,
        'warnings': warnings,
        'expected_total_revenue': expected_total_revenue,
        'actual_total_revenue': total_revenue,
        'revenue_per_mwh': revenue_per_mwh
    }

def validate_roi(roi, net_cashflow, investment):
    """
    Validiert den ROI
    
    Args:
        roi: Berechneter ROI in %
        net_cashflow: Netto-Cashflow über 10 Jahre
        investment: Investitionskosten
    
    Returns:
        dict: Validierungsergebnis
    """
    issues = []
    warnings = []
    
    # Erwarteter ROI
    expected_roi = (net_cashflow / investment * 100) if investment > 0 else 0
    
    # Prüfe 1: ROI sollte gleich erwartetem Wert sein
    if abs(roi - expected_roi) > 0.1:
        issues.append(
            f"❌ FEHLER: ROI ({roi:.2f}%) stimmt nicht mit erwartetem Wert ({expected_roi:.2f}%) überein!"
        )
        issues.append(
            f"   Berechnung: ({net_cashflow:,.2f} € / {investment:,.2f} €) * 100 = {expected_roi:.2f}%"
        )
    
    # Prüfe 2: ROI sollte realistisch sein
    if roi < -100:
        warnings.append(
            f"⚠️ WARNUNG: ROI ({roi:.2f}%) ist sehr negativ (< -100%)"
        )
    elif roi > 500:
        warnings.append(
            f"⚠️ WARNUNG: ROI ({roi:.2f}%) ist sehr hoch (> 500%)"
        )
    
    return {
        'valid': len(issues) == 0,
        'issues': issues,
        'warnings': warnings,
        'expected_roi': expected_roi,
        'actual_roi': roi
    }

def validate_use_case_comparison(analysis_results, project_params):
    """
    Validiert die Use Case Vergleich Werte
    
    Args:
        analysis_results: Ergebnisse der Use Case Analyse
        project_params: Projektparameter (BESS-Größe, Investition, etc.)
    
    Returns:
        dict: Validierungsergebnis
    """
    print("=" * 80)
    print("VALIDIERUNG: USE CASE VERGLEICH WERTE")
    print("=" * 80)
    print()
    
    all_issues = []
    all_warnings = []
    
    # Projektparameter
    investment = project_params.get('investment', 0)
    bess_size_mwh = project_params.get('bess_size_mwh', 0)
    bess_power_mw = project_params.get('bess_power_mw', 0)
    
    print(f"Projektparameter:")
    print(f"  Investitionskosten: {investment:,.2f} €")
    print(f"  BESS-Kapazität: {bess_size_mwh:.2f} MWh")
    print(f"  BESS-Leistung: {bess_power_mw:.2f} MW")
    print()
    
    # Validiere jeden Use Case
    for uc_name, uc_data in analysis_results.get('use_cases', {}).items():
        print(f"{'=' * 80}")
        print(f"USE CASE: {uc_name}")
        print(f"{'=' * 80}")
        print()
        
        annual_balance = uc_data.get('annual_balance', {})
        
        net_cashflow = annual_balance.get('net_cashflow', 0)
        total_revenue = annual_balance.get('total_revenue', 0)
        total_costs = annual_balance.get('total_costs', 0)
        roi = annual_balance.get('cumulative_roi', 0)
        
        print(f"Berechnete Werte:")
        print(f"  Gesamterlös (10 Jahre): {total_revenue:,.2f} €")
        print(f"  Gesamtkosten (10 Jahre): {total_costs:,.2f} €")
        print(f"  Investitionskosten: {investment:,.2f} €")
        print(f"  Netto-Cashflow (10 Jahre): {net_cashflow:,.2f} €")
        print(f"  ROI: {roi:.2f}%")
        print()
        
        # Validiere Netto-Cashflow
        print("Validierung Netto-Cashflow:")
        net_cashflow_result = validate_net_cashflow(
            net_cashflow, total_revenue, total_costs, investment
        )
        
        if net_cashflow_result['issues']:
            for issue in net_cashflow_result['issues']:
                print(f"  {issue}")
                all_issues.append(f"{uc_name}: {issue}")
        
        if net_cashflow_result['warnings']:
            for warning in net_cashflow_result['warnings']:
                print(f"  {warning}")
                all_warnings.append(f"{uc_name}: {warning}")
        
        if net_cashflow_result['valid'] and not net_cashflow_result['warnings']:
            print(f"  ✅ Netto-Cashflow ist konsistent")
        
        print()
        
        # Validiere Gesamterlös
        print("Validierung Gesamterlös:")
        revenue_result = validate_total_revenue(
            total_revenue, investment, bess_size_mwh, bess_power_mw
        )
        
        if revenue_result['issues']:
            for issue in revenue_result['issues']:
                print(f"  {issue}")
                all_issues.append(f"{uc_name}: {issue}")
        
        if revenue_result['warnings']:
            for warning in revenue_result['warnings']:
                print(f"  {warning}")
                all_warnings.append(f"{uc_name}: {warning}")
        
        if revenue_result['valid'] and not revenue_result['warnings']:
            print(f"  ✅ Gesamterlös ist im erwarteten Bereich")
        
        print()
        
        # Validiere ROI
        print("Validierung ROI:")
        roi_result = validate_roi(roi, net_cashflow, investment)
        
        if roi_result['issues']:
            for issue in roi_result['issues']:
                print(f"  {issue}")
                all_issues.append(f"{uc_name}: {issue}")
        
        if roi_result['warnings']:
            for warning in roi_result['warnings']:
                print(f"  {warning}")
                all_warnings.append(f"{uc_name}: {warning}")
        
        if roi_result['valid'] and not roi_result['warnings']:
            print(f"  ✅ ROI ist konsistent")
        
        print()
    
    # Validiere Gesamterlös (Summe aller Use Cases)
    comparison_metrics = analysis_results.get('comparison_metrics', {})
    total_comparison = comparison_metrics.get('total_comparison', {})
    total_revenue_all = total_comparison.get('total_revenue', 0)
    
    print(f"{'=' * 80}")
    print(f"VALIDIERUNG: GESAMTERLÖS (ALLE USE CASES)")
    print(f"{'=' * 80}")
    print()
    
    print(f"Berechneter Gesamterlös (Summe aller Use Cases): {total_revenue_all:,.2f} €")
    print()
    
    print("⚠️ WICHTIGER HINWEIS:")
    print("  Der 'Gesamterlös' wird aktuell als Summe aller Use Cases berechnet.")
    print("  Dies ist FALSCH, da Use Cases alternative Szenarien sind und nicht")
    print("  gleichzeitig betrieben werden können!")
    print()
    print("  Empfehlung: Zeige nur den Gesamterlös des besten Use Cases an.")
    print()
    
    # Zusammenfassung
    print(f"{'=' * 80}")
    print(f"ZUSAMMENFASSUNG")
    print(f"{'=' * 80}")
    print()
    
    if all_issues:
        print(f"❌ GEFUNDENE FEHLER: {len(all_issues)}")
        for issue in all_issues:
            print(f"  - {issue}")
        print()
    else:
        print(f"✅ Keine kritischen Fehler gefunden")
        print()
    
    if all_warnings:
        print(f"⚠️ WARNUNGEN: {len(all_warnings)}")
        for warning in all_warnings:
            print(f"  - {warning}")
        print()
    else:
        print(f"✅ Keine Warnungen")
        print()
    
    return {
        'valid': len(all_issues) == 0,
        'issues': all_issues,
        'warnings': all_warnings
    }

if __name__ == '__main__':
    print("Dieses Skript sollte mit den tatsächlichen Analyse-Ergebnissen aufgerufen werden.")
    print("Beispiel:")
    print("  from enhanced_economic_analysis import EnhancedEconomicAnalyzer")
    print("  analyzer = EnhancedEconomicAnalyzer(project_id=1)")
    print("  results = analyzer.compare_use_cases(...)")
    print("  validate_use_case_comparison(results, {...})")

