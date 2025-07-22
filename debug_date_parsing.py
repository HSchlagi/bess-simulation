#!/usr/bin/env python3
"""
Debug-Skript für das Datum-Parsing-Problem
"""

import re
from datetime import datetime

def debug_date_parsing():
    """Debuggt das Datum-Parsing-Problem"""
    
    print("🔍 Debug: Datum-Parsing-Problem analysieren...")
    print("=" * 60)
    
    # Test-Datumsformate aus der Excel-Datei
    test_timestamps = [
        "21.2.1900, 12:07:12",
        "30.3.1900, 03:50:24", 
        "9.4.1900, 10:33:36",
        "13.2.1900, 22:48:00",
        "21.2.1900, 23:52:48"
    ]
    
    print("1. Test-Datumsformate:")
    for timestamp in test_timestamps:
        print(f"   Original: '{timestamp}'")
        
        # Aktuelle Parsing-Logik
        timestamp_clean = re.sub(r'[TZ]', ' ', timestamp).strip()
        print(f"   Bereinigt: '{timestamp_clean}'")
        
        # Versuche verschiedene Formate
        parsed_date = None
        for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%d.%m.%Y %H:%M:%S', '%d.%m.%Y %H:%M']:
            try:
                parsed_date = datetime.strptime(timestamp_clean, fmt)
                print(f"   Format '{fmt}': {parsed_date}")
                break
            except ValueError:
                continue
        
        if parsed_date is None:
            print(f"   ❌ Kein Format gefunden!")
        
        print()
    
    print("2. Problem-Analyse:")
    print("   Das Problem ist, dass Excel-Daten oft als 'Tage seit 1900-01-01' gespeichert werden.")
    print("   Excel interpretiert 21.2.1900 als Tag 21, Februar 1900, aber das ist falsch.")
    print("   Wir müssen das Excel-Datum-Format korrekt parsen.")
    
    print("\n3. Lösung:")
    print("   - Excel-Datum-Format erkennen")
    print("   - Korrekte Jahr-Berechnung implementieren")
    print("   - Datum-Validierung verbessern")

if __name__ == "__main__":
    debug_date_parsing() 