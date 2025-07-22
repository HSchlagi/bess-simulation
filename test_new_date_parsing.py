#!/usr/bin/env python3
"""
Test-Skript für das neue Datum-Parsing
"""

import re
from datetime import datetime

def test_new_date_parsing():
    """Testet das neue Datum-Parsing"""
    
    print("🔍 Teste neues Datum-Parsing...")
    print("=" * 50)
    
    # Test-Datumsformate aus der Excel-Datei
    test_timestamps = [
        "21.2.1900, 12:07:12",
        "30.3.1900, 03:50:24", 
        "9.4.1900, 10:33:36",
        "13.2.1900, 22:48:00",
        "21.2.1900, 23:52:48"
    ]
    
    print("1. Neues Datum-Parsing:")
    for timestamp in test_timestamps:
        print(f"   Original: '{timestamp}'")
        
        # Neue Parsing-Logik
        timestamp_clean = re.sub(r'[TZ]', ' ', timestamp).strip()
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
                print(f"   Format '{fmt}': {parsed_date}")
                break
            except ValueError:
                continue
        
        # Excel-Datum-Format versuchen
        if parsed_date is None:
            try:
                parts = timestamp_clean.split()
                if len(parts) >= 2:
                    date_part = parts[0]
                    time_part = parts[1] if len(parts) > 1 else "00:00:00"
                    
                    date_parts = date_part.split('.')
                    if len(date_parts) == 3:
                        day = int(date_parts[0])
                        month = int(date_parts[1])
                        year = int(date_parts[2])
                        
                        # Korrigiere Jahr wenn nötig
                        if year < 2000:
                            year = 2024
                        
                        time_parts = time_part.split(':')
                        hour = int(time_parts[0]) if len(time_parts) > 0 else 0
                        minute = int(time_parts[1]) if len(time_parts) > 1 else 0
                        second = int(time_parts[2]) if len(time_parts) > 2 else 0
                        
                        parsed_date = datetime(year, month, day, hour, minute, second)
                        print(f"   ✅ Excel-Datum korrigiert: {parsed_date}")
            except Exception as e:
                print(f"   ❌ Excel-Datum-Parsing fehlgeschlagen: {e}")
        
        if parsed_date is None:
            print(f"   ❌ Kein Format gefunden!")
        else:
            print(f"   Final: {parsed_date.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print()

if __name__ == "__main__":
    test_new_date_parsing() 