#!/usr/bin/env python3
"""
ERSTELLT AUTOMATISCH EIN WASSERSTAND-LASTPROFIL AUS DEN EHYD-DATEN!
"""

import sqlite3
import json
from datetime import datetime, timedelta

def create_water_level_load_profile():
    """Erstellt automatisch ein Wasserstand-Lastprofil aus den EHYD-Daten"""
    
    print("🌊 ERSTELLE WASSERSTAND-LASTPROFIL AUTOMATISCH!")
    print("=" * 60)
    
    try:
        # Verbindung zur Datenbank
        conn = sqlite3.connect('instance/bess.db')
        cursor = conn.cursor()
        
        # Prüfe ob Wasserstand-Lastprofil bereits existiert
        cursor.execute("""
            SELECT id, name FROM load_profiles 
            WHERE name LIKE '%Wasserstand%' OR name LIKE '%Steyr%' OR name LIKE '%EHYD%'
        """)
        existing_profiles = cursor.fetchall()
        
        if existing_profiles:
            print(f"✅ Wasserstand-Lastprofil bereits vorhanden: {existing_profiles[0][1]}")
            return existing_profiles[0][0]
        
        # Hole alle Wasserstanddaten für Steyr
        cursor.execute("""
            SELECT timestamp, water_level_cm, river_name, station_name
            FROM water_levels 
            WHERE river_name = 'Steyr'
            ORDER BY timestamp
        """)
        water_level_data = cursor.fetchall()
        
        if not water_level_data:
            print("❌ Keine Wasserstanddaten für Steyr gefunden!")
            return None
        
        print(f"📊 {len(water_level_data)} Wasserstanddaten für Steyr gefunden")
        
        # Erstelle Lastprofil-Daten
        load_profile_name = f"Steyr Wasserstand {datetime.now().strftime('%Y-%m-%d')}"
        load_profile_description = f"EHYD-Pegelstanddaten für Steyr - {len(water_level_data)} Datenpunkte"
        
        # Konvertiere Wasserstanddaten zu Lastprofil-Format
        load_profile_data = []
        for timestamp, water_level_cm, river_name, station_name in water_level_data:
            # Konvertiere Pegelstand zu Last (vereinfachte Formel)
            # Höherer Pegelstand = höhere Last (für BESS-Simulation)
            load_value = (water_level_cm / 100.0) * 10  # Skalierung für Lastprofil
            
            load_profile_data.append({
                'timestamp': timestamp,
                'value': round(load_value, 2),
                'unit': 'kW',
                'source': 'EHYD',
                'metadata': {
                    'water_level_cm': water_level_cm,
                    'river_name': river_name,
                    'station_name': station_name,
                    'original_unit': 'cm'
                }
            })
        
        # Erstelle das Lastprofil in der Datenbank
        cursor.execute("""
            INSERT INTO load_profiles (name, description, project_id, data_type, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (load_profile_name, load_profile_description, 1, 'water_level', datetime.now().isoformat()))
        
        load_profile_id = cursor.lastrowid
        print(f"✅ Lastprofil erstellt: ID {load_profile_id}")
        
        # Speichere die Lastprofil-Daten
        for data_point in load_profile_data:
            cursor.execute("""
                INSERT INTO load_profile_data (load_profile_id, timestamp, value, unit, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (
                load_profile_id,
                data_point['timestamp'],
                data_point['value'],
                data_point['unit'],
                json.dumps(data_point['metadata'])
            ))
        
        # Commit und schließen
        conn.commit()
        conn.close()
        
        print(f"✅ {len(load_profile_data)} Datenpunkte in Lastprofil gespeichert")
        print(f"✅ Wasserstand-Lastprofil '{load_profile_name}' erfolgreich erstellt!")
        
        return load_profile_id
        
    except Exception as e:
        print(f"❌ Fehler beim Erstellen des Wasserstand-Lastprofils: {e}")
        return None

def create_hydro_power_load_profile():
    """Erstellt ein Wasserkraft-Erzeugungs-Lastprofil basierend auf den Wasserstanddaten"""
    
    print("⚡ ERSTELLE WASSERKRAFT-ERZEUGUNGS-LASTPROFIL!")
    print("=" * 60)
    
    try:
        # Verbindung zur Datenbank
        conn = sqlite3.connect('instance/bess.db')
        cursor = conn.cursor()
        
        # Prüfe ob Wasserkraft-Lastprofil bereits existiert
        cursor.execute("""
            SELECT id, name FROM load_profiles 
            WHERE name LIKE '%Wasserkraft%' OR name LIKE '%540kW%'
        """)
        existing_profiles = cursor.fetchall()
        
        if existing_profiles:
            print(f"✅ Wasserkraft-Lastprofil bereits vorhanden: {existing_profiles[0][1]}")
            return existing_profiles[0][0]
        
        # Hole alle Wasserstanddaten für Steyr
        cursor.execute("""
            SELECT timestamp, water_level_cm, river_name, station_name
            FROM water_levels 
            WHERE river_name = 'Steyr'
            ORDER BY timestamp
        """)
        water_level_data = cursor.fetchall()
        
        if not water_level_data:
            print("❌ Keine Wasserstanddaten für Steyr gefunden!")
            return None
        
        print(f"📊 {len(water_level_data)} Wasserstanddaten für Wasserkraft-Berechnung")
        
        # Wasserkraft-Parameter
        power_nominal = 540  # kW
        efficiency = 0.85    # 85%
        head = 15           # m
        water_density = 1000 # kg/m³
        gravity = 9.81      # m/s²
        
        # Erstelle Lastprofil-Daten für Wasserkraft-Erzeugung
        load_profile_name = f"Steyr Wasserkraft 540kW {datetime.now().strftime('%Y-%m-%d')}"
        load_profile_description = f"Wasserkraft-Erzeugung basierend auf EHYD-Pegelständen - {len(water_level_data)} Datenpunkte"
        
        load_profile_data = []
        for timestamp, water_level_cm, river_name, station_name in water_level_data:
            # Wasserkraft-Berechnung
            water_level_m = water_level_cm / 100.0
            
            # Durchfluss basierend auf Pegelstand (vereinfachte Formel)
            flow_coefficient = 0.8  # m³/s pro m^1.5
            flow = flow_coefficient * (water_level_m ** 1.5)
            
            # Wasserkraft-Formel: P = η * ρ * g * H * Q
            theoretical_power = efficiency * water_density * gravity * head * flow
            actual_power = min(theoretical_power, power_nominal * 1000)  # Begrenzt auf Nennleistung
            generation_kw = actual_power / 1000  # W zu kW
            
            load_profile_data.append({
                'timestamp': timestamp,
                'value': round(generation_kw, 2),
                'unit': 'kW',
                'source': 'EHYD_Wasserkraft',
                'metadata': {
                    'water_level_cm': water_level_cm,
                    'flow_m3s': round(flow, 3),
                    'efficiency': efficiency,
                    'head_m': head,
                    'power_nominal_kw': power_nominal,
                    'river_name': river_name,
                    'station_name': station_name
                }
            })
        
        # Erstelle das Lastprofil in der Datenbank
        cursor.execute("""
            INSERT INTO load_profiles (name, description, project_id, data_type, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (load_profile_name, load_profile_description, 1, 'hydro_power', datetime.now().isoformat()))
        
        load_profile_id = cursor.lastrowid
        print(f"✅ Wasserkraft-Lastprofil erstellt: ID {load_profile_id}")
        
        # Speichere die Lastprofil-Daten
        for data_point in load_profile_data:
            cursor.execute("""
                INSERT INTO load_profile_data (load_profile_id, timestamp, value, unit, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (
                load_profile_id,
                data_point['timestamp'],
                data_point['value'],
                data_point['unit'],
                json.dumps(data_point['metadata'])
            ))
        
        # Commit und schließen
        conn.commit()
        conn.close()
        
        print(f"✅ {len(load_profile_data)} Wasserkraft-Datenpunkte gespeichert")
        print(f"✅ Wasserkraft-Lastprofil '{load_profile_name}' erfolgreich erstellt!")
        
        return load_profile_id
        
    except Exception as e:
        print(f"❌ Fehler beim Erstellen des Wasserkraft-Lastprofils: {e}")
        return None

def main():
    """Hauptfunktion - erstellt beide Lastprofile"""
    
    print("🚀 ERSTELLE WASSERSTAND- UND WASSERKRAFT-LASTPROFILE!")
    print("=" * 60)
    
    # Erstelle Wasserstand-Lastprofil
    water_level_id = create_water_level_load_profile()
    
    # Erstelle Wasserkraft-Erzeugungs-Lastprofil
    hydro_power_id = create_hydro_power_load_profile()
    
    print("\n" + "=" * 60)
    print("🎯 LASTPROFIL-ERSTELLUNG ABGESCHLOSSEN!")
    
    if water_level_id:
        print(f"✅ Wasserstand-Lastprofil: ID {water_level_id}")
    if hydro_power_id:
        print(f"✅ Wasserkraft-Lastprofil: ID {hydro_power_id}")
    
    print("🌐 Öffnen Sie: http://127.0.0.1:5000/bess_peak_shaving_analysis")
    print("🎯 Jetzt können Sie die Wasserstand-Lastprofile auswählen!")

if __name__ == "__main__":
    main() 