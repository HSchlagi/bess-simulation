#!/usr/bin/env python3
"""
Prüfe Solar-Daten für Hinterstoder 2020
"""

import sqlite3
import pandas as pd

def check_hinterstoder_data():
    """Prüfe Solar-Daten für Hinterstoder 2020"""
    
    db_path = "instance/bess.db"
    
    try:
        conn = sqlite3.connect(db_path)
        
        # Prüfe Daten für Hinterstoder 2020
        query = """
        SELECT COUNT(*) as count, 
               MIN(datetime) as min_date, 
               MAX(datetime) as max_date,
               AVG(global_irradiance) as avg_irradiance,
               MAX(global_irradiance) as max_irradiance
        FROM solar_data 
        WHERE location_key = 'hinterstoder' AND year = 2020
        """
        
        df = pd.read_sql_query(query, conn)
        
        if not df.empty and df.iloc[0]['count'] > 0:
            print("✅ Solar-Daten für Hinterstoder 2020 gefunden:")
            print(f"   Anzahl Datensätze: {df.iloc[0]['count']}")
            print(f"   Zeitraum: {df.iloc[0]['min_date']} bis {df.iloc[0]['max_date']}")
            print(f"   Ø Globalstrahlung: {df.iloc[0]['avg_irradiance']:.1f} W/m²")
            print(f"   Max Globalstrahlung: {df.iloc[0]['max_irradiance']:.1f} W/m²")
            
            # Zeige erste 5 Datensätze
            print("\n📋 Erste 5 Datensätze:")
            sample_query = """
            SELECT datetime, global_irradiance, temperature_2m, wind_speed_10m
            FROM solar_data 
            WHERE location_key = 'hinterstoder' AND year = 2020
            ORDER BY datetime
            LIMIT 5
            """
            sample_df = pd.read_sql_query(sample_query, conn)
            print(sample_df)
            
        else:
            print("❌ Keine Solar-Daten für Hinterstoder 2020 gefunden")
            
            # Prüfe welche Daten vorhanden sind
            print("\n🔍 Verfügbare Solar-Daten:")
            cursor = conn.cursor()
            cursor.execute("SELECT location_key, year, COUNT(*) FROM solar_data GROUP BY location_key, year")
            available = cursor.fetchall()
            for loc, year, count in available:
                print(f"   - {loc} ({year}): {count} Datensätze")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Fehler: {e}")

if __name__ == "__main__":
    check_hinterstoder_data() 