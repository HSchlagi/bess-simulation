#!/usr/bin/env python3
"""
Skript zum Prüfen der Datumstruktur in der Datenbank
"""

import sqlite3
import os
from datetime import datetime

def check_date_structure():
    """Prüft die Datumstruktur in der Datenbank"""
    
    db_path = 'instance/bess.db'
    
    if not os.path.exists(db_path):
        print("❌ Datenbank nicht gefunden!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Prüfe Datumstruktur in der Datenbank...")
        print("=" * 60)
        
        # 1. Load Values mit Datumsstruktur prüfen
        print("1. Load Values - Datumstruktur:")
        cursor.execute("""
            SELECT load_profile_id, timestamp, power_kw, created_at 
            FROM load_value 
            ORDER BY timestamp ASC 
            LIMIT 10
        """)
        
        load_values = cursor.fetchall()
        
        if not load_values:
            print("   ❌ Keine Load Values gefunden!")
        else:
            print(f"   ✅ {len(load_values)} Load Values gefunden:")
            for profile_id, timestamp, power_kw, created_at in load_values:
                print(f"   - Profil {profile_id}: {timestamp} -> {power_kw} kW")
                
                # Datum parsen und validieren
                try:
                    parsed_date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    print(f"     Parsed: {parsed_date.strftime('%Y-%m-%d %H:%M:%S')}")
                except Exception as e:
                    print(f"     ❌ Parse-Fehler: {e}")
        
        print()
        
        # 2. Datumsbereich prüfen
        print("2. Datumsbereich:")
        cursor.execute("""
            SELECT MIN(timestamp), MAX(timestamp), COUNT(*) 
            FROM load_value
        """)
        
        min_date, max_date, count = cursor.fetchone()
        
        if min_date and max_date:
            print(f"   Erste Daten: {min_date}")
            print(f"   Letzte Daten: {max_date}")
            print(f"   Gesamtanzahl: {count}")
            
            # Datum validieren
            try:
                min_parsed = datetime.fromisoformat(min_date.replace('Z', '+00:00'))
                max_parsed = datetime.fromisoformat(max_date.replace('Z', '+00:00'))
                print(f"   Parsed Min: {min_parsed.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   Parsed Max: {max_parsed.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Prüfen ob Datum realistisch ist
                if min_parsed.year < 2000 or max_parsed.year < 2000:
                    print("   ⚠️ WARNUNG: Datum vor 2000 - wahrscheinlich falsch!")
                elif min_parsed.year > 2030 or max_parsed.year > 2030:
                    print("   ⚠️ WARNUNG: Datum nach 2030 - wahrscheinlich falsch!")
                else:
                    print("   ✅ Datum sieht realistisch aus")
                    
            except Exception as e:
                print(f"   ❌ Parse-Fehler: {e}")
        else:
            print("   ❌ Keine Daten gefunden")
        
        print()
        
        # 3. Datumsformat-Analyse
        print("3. Datumsformat-Analyse:")
        cursor.execute("""
            SELECT DISTINCT timestamp 
            FROM load_value 
            ORDER BY timestamp ASC 
            LIMIT 5
        """)
        
        formats = cursor.fetchall()
        for (timestamp,) in formats:
            print(f"   Format: '{timestamp}'")
            print(f"   Länge: {len(timestamp)}")
            print(f"   Enthält 'T': {'T' in timestamp}")
            print(f"   Enthält 'Z': {'Z' in timestamp}")
            print(f"   Enthält '+': {'+' in timestamp}")
        
        print()
        
        # 4. Lastprofile mit Datumsinfo
        print("4. Lastprofile mit Datumsinfo:")
        cursor.execute("""
            SELECT lp.id, lp.name, 
                   MIN(lv.timestamp) as first_date, 
                   MAX(lv.timestamp) as last_date,
                   COUNT(lv.id) as data_points
            FROM load_profile lp
            LEFT JOIN load_value lv ON lp.id = lv.load_profile_id
            GROUP BY lp.id, lp.name
            ORDER BY lp.id
        """)
        
        profiles = cursor.fetchall()
        for profile_id, name, first_date, last_date, data_points in profiles:
            print(f"   Profil {profile_id}: {name}")
            print(f"     Datenpunkte: {data_points}")
            if first_date and last_date:
                print(f"     Zeitraum: {first_date} bis {last_date}")
            else:
                print(f"     Zeitraum: Keine Daten")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Fehler beim Prüfen der Datumstruktur: {e}")

if __name__ == "__main__":
    check_date_structure() 