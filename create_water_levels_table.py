#!/usr/bin/env python3
"""
ERSTELLT DIE WATER_LEVELS TABELLE UND FÜLLT SIE MIT DEMO-DATEN!
"""

import sqlite3
import json
from datetime import datetime, timedelta
import random

def create_water_levels_table():
    """Erstellt die water_levels Tabelle"""
    
    print("🌊 ERSTELLE WATER_LEVELS TABELLE!")
    print("=" * 60)
    
    try:
        # Verbindung zur Datenbank
        conn = sqlite3.connect('instance/bess.db')
        cursor = conn.cursor()
        
        # Prüfe ob water_levels Tabelle existiert
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='water_levels'
        """)
        
        if not cursor.fetchone():
            print("📋 Erstelle water_levels Tabelle...")
            cursor.execute("""
                CREATE TABLE water_levels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    water_level_cm REAL NOT NULL,
                    river_name TEXT NOT NULL,
                    station_name TEXT NOT NULL,
                    source TEXT DEFAULT 'EHYD',
                    created_at TEXT NOT NULL
                )
            """)
            print("✅ water_levels Tabelle erstellt")
        else:
            print("✅ water_levels Tabelle bereits vorhanden")
        
        # Prüfe ob bereits Daten vorhanden sind
        cursor.execute("SELECT COUNT(*) FROM water_levels")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("📊 Erstelle Demo-Wasserstanddaten für Steyr...")
            
            # Erstelle Demo-Daten für Steyr
            start_date = datetime(2024, 1, 1)
            end_date = datetime(2025, 12, 31)
            current_date = start_date
            
            stations = ['Hinterstoder', 'Steyrbrücke', 'Steyrdorf']
            base_levels = [120, 110, 115]  # cm
            
            data_count = 0
            while current_date <= end_date:
                for hour in range(24):
                    for station_idx, station in enumerate(stations):
                        # Realistische Pegelstand-Variation
                        base_level = base_levels[station_idx]
                        
                        # Tagesverlauf (höher am Tag, niedriger in der Nacht)
                        daily_variation = 10 * (1 + 0.5 * (hour - 12) / 12)
                        
                        # Wöchentliche Variation
                        weekly_variation = 5 * (current_date.weekday() - 3) / 3
                        
                        # Zufällige Variation
                        random_variation = random.uniform(-5, 5)
                        
                        # Saisonale Variation (höher im Frühjahr/Sommer)
                        seasonal_variation = 15 * (1 + 0.3 * (current_date.month - 6) / 6)
                        
                        water_level = base_level + daily_variation + weekly_variation + random_variation + seasonal_variation
                        water_level = max(80, min(200, water_level))  # Begrenzen auf 80-200 cm
                        
                        timestamp = current_date.replace(hour=hour, minute=0, second=0, microsecond=0).isoformat()
                        
                        cursor.execute("""
                            INSERT INTO water_levels (timestamp, water_level_cm, river_name, station_name, source, created_at)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (timestamp, round(water_level, 1), 'Steyr', station, 'EHYD (Demo)', datetime.now().isoformat()))
                        
                        data_count += 1
                
                current_date += timedelta(days=1)
                
                # Fortschritt anzeigen
                if data_count % 1000 == 0:
                    print(f"📊 {data_count} Datenpunkte erstellt...")
            
            print(f"✅ {data_count} Demo-Wasserstanddaten erstellt")
        else:
            print(f"✅ {count} Wasserstanddaten bereits vorhanden")
        
        # Commit und schließen
        conn.commit()
        conn.close()
        
        print("✅ Water_levels Tabelle erfolgreich erstellt und gefüllt!")
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Erstellen der water_levels Tabelle: {e}")
        return False

def create_load_profiles_from_water_levels():
    """Erstellt Lastprofile aus den Wasserstanddaten"""
    
    print("🌊 ERSTELLE LASTPROFILE AUS WASSERSTANDDATEN!")
    print("=" * 60)
    
    try:
        # Verbindung zur Datenbank
        conn = sqlite3.connect('instance/bess.db')
        cursor = conn.cursor()
        
        # Hole Wasserstanddaten
        cursor.execute("""
            SELECT timestamp, water_level_cm, river_name, station_name
            FROM water_levels 
            WHERE river_name = 'Steyr'
            ORDER BY timestamp
            LIMIT 1000
        """)
        water_level_data = cursor.fetchall()
        
        if not water_level_data:
            print("❌ Keine Wasserstanddaten gefunden!")
            return None
        
        print(f"📊 {len(water_level_data)} Wasserstanddaten gefunden")
        
        # 1. Wasserstand-Lastprofil
        load_profile_name = f"Steyr Wasserstand {datetime.now().strftime('%Y-%m-%d')}"
        load_profile_description = f"EHYD-Pegelstanddaten für Steyr - {len(water_level_data)} Datenpunkte"
        
        cursor.execute("""
            INSERT INTO load_profiles (name, description, project_id, data_type, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (load_profile_name, load_profile_description, 1, 'water_level', datetime.now().isoformat()))
        
        water_level_profile_id = cursor.lastrowid
        print(f"✅ Wasserstand-Lastprofil erstellt: ID {water_level_profile_id}")
        
        # Speichere Wasserstand-Daten
        for timestamp, water_level_cm, river_name, station_name in water_level_data:
            # Konvertiere Pegelstand zu Last (vereinfachte Formel)
            load_value = (water_level_cm / 100.0) * 10  # Skalierung für Lastprofil
            
            cursor.execute("""
                INSERT INTO load_profile_data (load_profile_id, timestamp, value, unit, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (
                water_level_profile_id,
                timestamp,
                round(load_value, 2),
                'kW',
                json.dumps({
                    'water_level_cm': water_level_cm,
                    'river_name': river_name,
                    'station_name': station_name,
                    'original_unit': 'cm'
                })
            ))
        
        # 2. Wasserkraft-Erzeugungs-Lastprofil
        power_nominal = 540  # kW
        efficiency = 0.85    # 85%
        head = 15           # m
        water_density = 1000 # kg/m³
        gravity = 9.81      # m/s²
        
        hydro_profile_name = f"Steyr Wasserkraft 540kW {datetime.now().strftime('%Y-%m-%d')}"
        hydro_profile_description = f"Wasserkraft-Erzeugung basierend auf EHYD-Pegelständen - {len(water_level_data)} Datenpunkte"
        
        cursor.execute("""
            INSERT INTO load_profiles (name, description, project_id, data_type, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (hydro_profile_name, hydro_profile_description, 1, 'hydro_power', datetime.now().isoformat()))
        
        hydro_profile_id = cursor.lastrowid
        print(f"✅ Wasserkraft-Lastprofil erstellt: ID {hydro_profile_id}")
        
        # Speichere Wasserkraft-Daten
        for timestamp, water_level_cm, river_name, station_name in water_level_data:
            # Wasserkraft-Berechnung
            water_level_m = water_level_cm / 100.0
            
            # Durchfluss basierend auf Pegelstand
            flow_coefficient = 0.8  # m³/s pro m^1.5
            flow = flow_coefficient * (water_level_m ** 1.5)
            
            # Wasserkraft-Formel: P = η * ρ * g * H * Q
            theoretical_power = efficiency * water_density * gravity * head * flow
            actual_power = min(theoretical_power, power_nominal * 1000)  # Begrenzt auf Nennleistung
            generation_kw = actual_power / 1000  # W zu kW
            
            cursor.execute("""
                INSERT INTO load_profile_data (load_profile_id, timestamp, value, unit, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (
                hydro_profile_id,
                timestamp,
                round(generation_kw, 2),
                'kW',
                json.dumps({
                    'water_level_cm': water_level_cm,
                    'flow_m3s': round(flow, 3),
                    'efficiency': efficiency,
                    'head_m': head,
                    'power_nominal_kw': power_nominal,
                    'river_name': river_name,
                    'station_name': station_name
                })
            ))
        
        # Commit und schließen
        conn.commit()
        conn.close()
        
        print(f"✅ {len(water_level_data)} Datenpunkte in beiden Lastprofilen gespeichert")
        print(f"✅ Wasserstand-Lastprofil: '{load_profile_name}'")
        print(f"✅ Wasserkraft-Lastprofil: '{hydro_profile_name}'")
        
        return water_level_profile_id, hydro_profile_id
        
    except Exception as e:
        print(f"❌ Fehler beim Erstellen der Lastprofile: {e}")
        return None

def main():
    """Hauptfunktion"""
    
    print("🚀 ERSTELLE WATER_LEVELS TABELLE UND LASTPROFILE!")
    print("=" * 60)
    
    # Erstelle water_levels Tabelle
    if create_water_levels_table():
        # Erstelle Lastprofile aus Wasserstanddaten
        result = create_load_profiles_from_water_levels()
        
        print("\n" + "=" * 60)
        print("🎯 WATER_LEVELS UND LASTPROFILE ERSTELLUNG ABGESCHLOSSEN!")
        
        if result:
            water_id, hydro_id = result
            print(f"✅ Wasserstand-Lastprofil: ID {water_id}")
            print(f"✅ Wasserkraft-Lastprofil: ID {hydro_id}")
        
        print("🌐 Öffnen Sie: http://127.0.0.1:5000/bess_peak_shaving_analysis")
        print("🎯 Jetzt können Sie die Wasserstand-Lastprofile auswählen!")
    else:
        print("❌ Fehler bei der Tabellen-Erstellung!")

if __name__ == "__main__":
    main() 