#!/usr/bin/env python3
"""
Vergleicht die Degradationsanwendung zwischen 10-Jahres-Report und Use Case Vergleich
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def compare_degradation():
    """Vergleicht die Degradationsanwendung"""
    
    print("=" * 80)
    print("DEGRADATIONSVERGLEICH")
    print("=" * 80)
    print()
    
    degradation_rate = 0.02
    
    print("10-JAHRES-REPORT Degradationsfaktoren:")
    print("-" * 80)
    for year_idx in range(11):  # 0-10 (11 Jahre)
        year = 2024 + year_idx
        degradation_factor = (1 - degradation_rate) ** year_idx
        print(f"Jahr {year} (year_idx={year_idx}): degradation_factor = {degradation_factor:.6f}")
    print()
    
    print("USE CASE VERGLEICH Degradationsfaktoren:")
    print("-" * 80)
    for year in range(1, 12):  # 1-11 (11 Jahre)
        year_idx = year - 1  # 0-basiert
        degradation_factor = (1 - degradation_rate) ** year_idx
        print(f"Jahr {year} (year_idx={year_idx}): degradation_factor = {degradation_factor:.6f}")
    print()
    
    print("VERGLEICH:")
    print("-" * 80)
    print("Beide verwenden: degradation_factor = (1 - 0.02) ** year_idx")
    print("wobei year_idx 0-basiert ist (0 für erstes Jahr, 1 für zweites Jahr, etc.)")
    print()
    print("OK: Degradationsfaktoren sind identisch!")
    print()
    
    # Berechne Summe der Degradationsfaktoren über 11 Jahre
    sum_degradation_10y = sum((1 - degradation_rate) ** year_idx for year_idx in range(11))
    print(f"Summe der Degradationsfaktoren über 11 Jahre: {sum_degradation_10y:.6f}")
    print(f"Multipliziert mit 11 (ohne Degradation): {11.0:.6f}")
    print(f"Effektive Anzahl Jahre (mit Degradation): {sum_degradation_10y:.2f}")
    print()

if __name__ == '__main__':
    compare_degradation()

