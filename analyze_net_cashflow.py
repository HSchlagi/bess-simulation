#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyse-Skript für Netto-Cashflow-Berechnung im Use Case Vergleich
Zeigt detailliert, wie der Wert 248.169.640 € zustande kommt
"""

def analyze_net_cashflow_calculation():
    """
    Analysiert die Netto-Cashflow-Berechnung für Use Case Vergleich
    """
    
    print("=" * 80)
    print("NETTO-CASHFLOW ANALYSE - USE CASE VERGLEICH")
    print("=" * 80)
    print()
    
    print("BERECHNUNGSLOGIK:")
    print("-" * 80)
    print()
    
    print("1. SIMULATION ÜBER 10 JAHRE:")
    print("   - Die Simulation läuft über 10 Jahre (years=10)")
    print("   - Für jedes Jahr wird ein SimulationResult erstellt")
    print("   - Degradation: 2% pro Jahr (degradation_rate = 0.02)")
    print()
    
    print("2. MARKTERLÖSE PRO JAHR:")
    print("   - SRL-Erlöse (Sekundärregelleistung):")
    print("     Formel: bess_power_mw * availability_hours * price * participation_ratio")
    print("     - availability_hours = 8000 (nicht 8760)")
    print("     - srl_positive = 18.0 €/MW/h")
    print("     - srl_negative = 18.0 €/MW/h")
    print()
    
    print("   - SRE-Erlöse (Sekundärregelenergie):")
    print("     Formel: activation_energy_mwh * price * participation_ratio")
    print("     - activation_energy_mwh = 250 MWh/Jahr (fest)")
    print("     - sre_positive = 80.0 €/MWh")
    print("     - sre_negative = 80.0 €/MWh")
    print()
    
    print("   - Intraday-Trading:")
    print("     a) Spot-Arbitrage:")
    print("        Formel: bess_capacity_kwh * daily_cycles * 365 * price * efficiency")
    print("        - spot_arbitrage_price = 0.0074 €/kWh")
    print()
    print("     b) Intraday-Handel:")
    print("        Formel: bess_capacity_kwh * daily_cycles * 365 * price * efficiency")
    print("        - intraday_trading_price = 0.0111 €/kWh")
    print()
    print("     c) Balancing Energy:")
    print("        Formel: bess_power_mw * 1000 * 8760 * price / 1000 * efficiency")
    print("        - balancing_energy_price = 0.0231 €/kWh")
    print("        - AKTUELL DEAKTIVIERT (balancing_energy_revenue = 0)")
    print()
    
    print("   - Day-Ahead-Markt:")
    print("     Formel: bess_size_mwh * annual_cycles * price * participation_ratio")
    print()
    
    print("   - Ausgleichsenergie:")
    print("     Formel: bess_power_mw * 8760 * price * participation_ratio")
    print()
    
    print("3. KOSTEN PRO JAHR:")
    print("   - Betriebskosten: investment_costs * operating_cost_factor")
    print("   - Wartungskosten: investment_costs * maintenance_rate")
    print("   - Netzentgelte: energy_throughput * grid_tariff")
    print("   - Versicherung: investment_costs * insurance_rate")
    print("   - Degradation: investment_costs * degradation_rate")
    print()
    
    print("4. DEGRADATION:")
    print("   - Degradationsfaktor pro Jahr: (1 - 0.02) ** year_idx")
    print("   - Jahr 1: 1.0 (keine Degradation)")
    print("   - Jahr 2: 0.98")
    print("   - Jahr 3: 0.9604")
    print("   - ...")
    print("   - Jahr 10: 0.8337")
    print("   - Degradation wird auf Erlöse UND Betriebskosten angewendet")
    print()
    
    print("5. NETTO-CASHFLOW BERECHNUNG:")
    print("   - Pro Jahr: net_cashflow = total_revenue - total_costs")
    print("   - Über 10 Jahre: net_cashflow_10y = sum(net_cashflow für alle Jahre)")
    print()
    
    print("=" * 80)
    print("FORMEL-ZUSAMMENFASSUNG:")
    print("=" * 80)
    print()
    
    print("Für jedes Jahr (1-10):")
    print("  degradation_factor = (1 - 0.02) ** (year - 1)")
    print()
    print("  # Erlöse (mit Degradation)")
    print("  revenue_year = (")
    print("    srl_revenue * degradation_factor +")
    print("    sre_revenue * degradation_factor +")
    print("    intraday_revenue * degradation_factor +")
    print("    day_ahead_revenue * degradation_factor +")
    print("    balancing_revenue * degradation_factor")
    print("  )")
    print()
    print("  # Kosten (mit Degradation)")
    print("  costs_year = (")
    print("    operating_costs * degradation_factor +")
    print("    maintenance_costs * degradation_factor +")
    print("    grid_fees * degradation_factor +")
    print("    insurance_costs * degradation_factor +")
    print("    degradation_costs * degradation_factor")
    print("  )")
    print()
    print("  net_cashflow_year = revenue_year - costs_year")
    print()
    print("Gesamt (10 Jahre):")
    print("  net_cashflow_10y = sum(net_cashflow_year for year in 1..10)")
    print()
    
    print("=" * 80)
    print("BEISPIEL-BERECHNUNG (vereinfacht, ohne Degradation):")
    print("=" * 80)
    print()
    
    # Beispiel-Berechnung
    bess_power_mw = 2.0  # Beispiel: 2 MW
    bess_size_mwh = 8.0  # Beispiel: 8 MWh
    annual_cycles = 730  # Beispiel: 2 Zyklen/Tag * 365
    investment_costs = 6130000  # Beispiel: 6.13 Mio €
    
    print(f"Annahmen:")
    print(f"  - BESS-Leistung: {bess_power_mw} MW")
    print(f"  - BESS-Kapazität: {bess_size_mwh} MWh")
    print(f"  - Jahreszyklen: {annual_cycles}")
    print(f"  - Investitionskosten: {investment_costs:,.0f} €")
    print()
    
    # Erlöse (vereinfacht, ohne Degradation)
    availability_hours = 8000
    srl_price = 18.0  # €/MW/h
    srl_revenue = bess_power_mw * availability_hours * srl_price * 0.5  # 50% Teilnahme
    
    sre_activation = 250  # MWh/Jahr
    sre_price = 80.0  # €/MWh
    sre_revenue = sre_activation * sre_price * 0.5  # 50% Teilnahme
    
    bess_capacity_kwh = bess_size_mwh * 1000
    daily_cycles = annual_cycles / 365
    spot_arbitrage_price = 0.0074  # €/kWh
    spot_arbitrage_revenue = bess_capacity_kwh * daily_cycles * 365 * spot_arbitrage_price * 0.85
    
    intraday_trading_price = 0.0111  # €/kWh
    intraday_trading_revenue = bess_capacity_kwh * daily_cycles * 365 * intraday_trading_price * 0.85
    
    # Balancing Energy ist deaktiviert
    balancing_energy_revenue = 0
    
    intraday_total = (spot_arbitrage_revenue + intraday_trading_revenue + balancing_energy_revenue) * 0.5
    
    day_ahead_price = 50.0  # €/MWh (Standard)
    day_ahead_revenue = bess_size_mwh * annual_cycles * day_ahead_price * 0.3
    
    balancing_price = 45.0  # €/MWh (Standard)
    balancing_revenue = bess_power_mw * 8760 * balancing_price * 0.2 / 1000  # Umrechnung
    
    total_revenue_year = srl_revenue + sre_revenue + intraday_total + day_ahead_revenue + balancing_revenue
    
    print(f"Erlöse pro Jahr (ohne Degradation):")
    print(f"  - SRL: {srl_revenue:,.0f} €")
    print(f"  - SRE: {sre_revenue:,.0f} €")
    print(f"  - Intraday (Spot-Arbitrage): {spot_arbitrage_revenue:,.0f} €")
    print(f"  - Intraday (Trading): {intraday_trading_revenue:,.0f} €")
    print(f"  - Intraday (Balancing): {balancing_energy_revenue:,.0f} € (deaktiviert)")
    print(f"  - Intraday gesamt: {intraday_total:,.0f} €")
    print(f"  - Day-Ahead: {day_ahead_revenue:,.0f} €")
    print(f"  - Balancing: {balancing_revenue:,.0f} €")
    print(f"  - GESAMT: {total_revenue_year:,.0f} €")
    print()
    
    # Kosten (vereinfacht)
    operating_cost_factor = 0.02
    maintenance_rate = 0.015
    grid_tariff = 15.0  # €/MWh
    insurance_rate = 0.005
    degradation_rate = 0.02
    
    energy_throughput = bess_size_mwh * annual_cycles
    operating_costs = investment_costs * operating_cost_factor
    maintenance_costs = investment_costs * maintenance_rate
    grid_fees = energy_throughput * grid_tariff
    insurance_costs = investment_costs * insurance_rate
    degradation_costs = investment_costs * degradation_rate
    
    total_costs_year = operating_costs + maintenance_costs + grid_fees + insurance_costs + degradation_costs
    
    print(f"Kosten pro Jahr (ohne Degradation):")
    print(f"  - Betriebskosten: {operating_costs:,.0f} €")
    print(f"  - Wartungskosten: {maintenance_costs:,.0f} €")
    print(f"  - Netzentgelte: {grid_fees:,.0f} €")
    print(f"  - Versicherung: {insurance_costs:,.0f} €")
    print(f"  - Degradation: {degradation_costs:,.0f} €")
    print(f"  - GESAMT: {total_costs_year:,.0f} €")
    print()
    
    net_cashflow_year = total_revenue_year - total_costs_year
    print(f"Netto-Cashflow pro Jahr: {net_cashflow_year:,.0f} €")
    print()
    
    # Über 10 Jahre mit Degradation
    print("Über 10 Jahre (mit Degradation):")
    total_revenue_10y = 0
    total_costs_10y = 0
    
    for year in range(1, 11):
        degradation_factor = (1 - 0.02) ** (year - 1)
        revenue_year = total_revenue_year * degradation_factor
        costs_year = total_costs_year * degradation_factor
        total_revenue_10y += revenue_year
        total_costs_10y += costs_year
    
    net_cashflow_10y = total_revenue_10y - total_costs_10y
    
    print(f"  - Gesamterlös (10 Jahre): {total_revenue_10y:,.0f} €")
    print(f"  - Gesamtkosten (10 Jahre): {total_costs_10y:,.0f} €")
    print(f"  - Netto-Cashflow (10 Jahre): {net_cashflow_10y:,.0f} €")
    print()
    
    print("=" * 80)
    print("HINWEISE:")
    print("=" * 80)
    print()
    print("WARNUNG: Der tatsaechliche Wert haengt ab von:")
    print("   1. Projekt-spezifischen Parametern (BESS-Größe, Leistung, Zyklen)")
    print("   2. Marktpreisen (aus DB oder Standardwerten)")
    print("   3. Use Case Konfiguration (Marktteilnahme, Effizienz)")
    print("   4. Investitionskosten")
    print()
    print("WARNUNG: Balancing Energy ist derzeit DEAKTIVIERT in enhanced_economic_analysis.py")
    print("   (Zeile 582: balancing_energy_revenue = 0)")
    print()
    print("HINWEIS: Um die genaue Berechnung fuer ein Projekt zu sehen:")
    print("   - Öffne die Browser-Konsole (F12)")
    print("   - Prüfe die API-Antwort von /api/economic-analysis/<project_id>")
    print("   - Oder füge Debug-Ausgaben in enhanced_economic_analysis.py hinzu")
    print()

if __name__ == "__main__":
    analyze_net_cashflow_calculation()

