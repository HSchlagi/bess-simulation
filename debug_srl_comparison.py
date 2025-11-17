#!/usr/bin/env python3
"""
Vergleicht die SRL-Berechnung zwischen 10-Jahres-Report und Use Case Vergleich
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def compare_srl():
    """Vergleicht die SRL-Berechnung"""
    
    try:
        from app import create_app
        from models import Project
        
        app = create_app()
        with app.app_context():
            # BORBET-Projekt laden
            project = Project.query.filter(Project.name.ilike('%BORBET%')).first()
            
            if not project:
                print("BORBET-Projekt nicht gefunden!")
                return
            
            bess_power_mw = (project.bess_power or 0) / 1000
            availability_hours = 8000
            srl_price = 18.0  # €/MW/h
            srl_participation_rate = 0.5
            degradation_rate = 0.02
            
            print("=" * 80)
            print("SRL-BERECHNUNGSVERGLEICH")
            print("=" * 80)
            print()
            print(f"BESS-Leistung: {bess_power_mw:.2f} MW")
            print(f"Verfügbarkeitsstunden: {availability_hours} h/Jahr")
            print(f"SRL-Preis: {srl_price} €/MW/h")
            print(f"SRL-Marktteilnahme: {srl_participation_rate * 100}%")
            print(f"Degradationsrate: {degradation_rate * 100}%")
            print()
            
            # Berechne SRL-Erlöse für jedes Jahr
            print("JÄHRLICHE SRL-ERLÖSE (ohne Degradation):")
            print("-" * 80)
            base_srl_revenue = bess_power_mw * availability_hours * srl_price * srl_participation_rate
            print(f"Jährlicher SRL-Erlös (ohne Degradation): {base_srl_revenue:,.2f} EUR")
            print()
            
            # Berechne SRL-Erlöse mit Degradation über 11 Jahre
            print("SRL-ERLÖSE MIT DEGRADATION ÜBER 11 JAHRE:")
            print("-" * 80)
            total_srl_revenue = 0
            for year_idx in range(11):
                degradation_factor = (1 - degradation_rate) ** year_idx
                year_srl_revenue = base_srl_revenue * degradation_factor
                total_srl_revenue += year_srl_revenue
                print(f"Jahr {year_idx + 1} (degradation_factor={degradation_factor:.6f}): {year_srl_revenue:,.2f} EUR")
            
            print()
            print(f"GESAMT SRL-ERLÖSE (11 Jahre): {total_srl_revenue:,.2f} EUR")
            print(f"GESAMT SRL-ERLÖSE (positiv + negativ): {total_srl_revenue * 2:,.2f} EUR")
            print()
            
            # Vergleich mit tatsächlichen Werten
            print("=" * 80)
            print("VERGLEICH MIT TATSÄCHLICHEN WERTEN")
            print("=" * 80)
            print()
            print(f"10-Jahres-Report SRL-Erlöse (positiv + negativ): 28.694.685,50 EUR")
            print(f"Berechnet (11 Jahre): {total_srl_revenue * 2:,.2f} EUR")
            print(f"Differenz: {abs(28694685.50 - total_srl_revenue * 2):,.2f} EUR")
            print()
            
            # Prüfe, ob es 10 oder 11 Jahre sind
            print("HINWEIS: Der 10-Jahres-Report könnte 10 Jahre (nicht 11) umfassen!")
            print("Berechne für 10 Jahre:")
            total_srl_revenue_10y = sum(
                base_srl_revenue * ((1 - degradation_rate) ** year_idx)
                for year_idx in range(10)
            )
            print(f"GESAMT SRL-ERLÖSE (10 Jahre, positiv + negativ): {total_srl_revenue_10y * 2:,.2f} EUR")
            print(f"Differenz zu 10-Jahres-Report: {abs(28694685.50 - total_srl_revenue_10y * 2):,.2f} EUR")
            
    except Exception as e:
        print(f"Fehler: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    compare_srl()

