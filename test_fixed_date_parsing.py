#!/usr/bin/env python3
"""
Test-Skript für das korrigierte Datum-Parsing
"""

import re
from datetime import datetime

def test_fixed_date_parsing():
    """Testet das korrigierte Datum-Parsing"""
    
    print("🔍 Teste korrigiertes Datum-Parsing...")
    print("=" * 50)
    
    # Test-Datumsformate aus der Excel-Datei
    test_timestamps = [
        "21.2.1900, 12:07:12",
        "30.3.1900, 03:50:24", 
        "9.4.1900, 10:33:36",
        "13.2.1900, 22:48:00",
        "21.2.1900, 23:52:48"
    ]
    
    print("1. Korrigiertes Parsing:")
    for timestamp in test_timestamps:
        print(f"   Original: '{timestamp}'")
        
        # Neue Parsing-Logik (wie in der API)
        timestamp_clean = timestamp.replace('T', ' ').replace('Z', '').strip()
        timestamp_clean = timestamp_clean.replace(',', ' ')
        
        print(f"   Bereinigt: '{timestamp_clean}'")
        
        # Versuche verschiedene Formate
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
                break
            except ValueError:
                continue
        
        # Excel-Datum-Korrektur NACH dem Standard-Parsing
        if parsed_date and parsed_date.year < 2000:
            print(f"   ✅ Excel-Datum korrigiert: {timestamp} -> {parsed_date.year} -> 2024")
            # Korrigiere das Jahr zu 2024
            parsed_date = datetime(2024, parsed_date.month, parsed_date.day, 
                                parsed_date.hour, parsed_date.minute, parsed_date.second)
        
        if parsed_date is None:
            print(f"   ❌ Kein Format gefunden!")
        else:
            print(f"   Final: {parsed_date.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print()

if __name__ == "__main__":
    test_fixed_date_parsing() 