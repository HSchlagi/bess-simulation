#!/usr/bin/env python3
"""
Detaillierte Analyse des Excel-Datum-Problems
"""

import re
from datetime import datetime

def debug_excel_date_issue():
    """Analysiert das Excel-Datum-Problem detailliert"""
    
    print("🔍 Detaillierte Excel-Datum-Analyse...")
    print("=" * 60)
    
    # Test-Datumsformate aus der Excel-Datei
    test_timestamps = [
        "21.2.1900, 12:07:12",
        "30.3.1900, 03:50:24", 
        "9.4.1900, 10:33:36"
    ]
    
    print("1. Schritt-für-Schritt-Analyse:")
    for i, timestamp in enumerate(test_timestamps, 1):
        print(f"\n   Datum {i}: '{timestamp}'")
        
        # Schritt 1: Bereinigung
        timestamp_clean = re.sub(r'[TZ]', ' ', timestamp).strip()
        timestamp_clean = timestamp_clean.replace(',', ' ')
        print(f"   Schritt 1 - Bereinigt: '{timestamp_clean}'")
        
        # Schritt 2: Standard-Formate versuchen
        parsed_date = None
        formats_to_try = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%d.%m.%Y %H:%M:%S',
            '%d.%m.%Y %H:%M',
            '%d.%m.%y %H:%M:%S',
            '%d.%m.%y %H:%M'
        ]
        
        for fmt in formats_to_try:
            try:
                parsed_date = datetime.strptime(timestamp_clean, fmt)
                print(f"   Schritt 2 - Format '{fmt}' gefunden: {parsed_date}")
                break
            except ValueError:
                continue
        
        # Schritt 3: Excel-Korrektur nur wenn Standard-Format 1900 ergab
        if parsed_date and parsed_date.year < 2000:
            print(f"   Schritt 3 - 1900-Jahr erkannt, korrigiere zu 2024...")
            
            # Manuelle Korrektur
            corrected_date = datetime(2024, parsed_date.month, parsed_date.day, 
                                    parsed_date.hour, parsed_date.minute, parsed_date.second)
            print(f"   Schritt 3 - Korrigiert: {corrected_date}")
            parsed_date = corrected_date
        
        # Schritt 4: Finales Ergebnis
        if parsed_date:
            print(f"   Schritt 4 - Final: {parsed_date.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"   Schritt 4 - ❌ Kein gültiges Datum gefunden!")
    
    print("\n2. Problem-Identifikation:")
    print("   Das Problem ist, dass das Standard-Format '%d.%m.%Y %H:%M:%S'")
    print("   erfolgreich parst, aber dann die Excel-Korrektur nicht ausgeführt wird.")
    print("   Die Korrektur wird nur ausgeführt, wenn KEIN Standard-Format gefunden wird.")
    
    print("\n3. Lösung:")
    print("   Wir müssen die Excel-Korrektur NACH dem Standard-Parsing ausführen,")
    print("   wenn das Jahr < 2000 ist.")

if __name__ == "__main__":
    debug_excel_date_issue() 