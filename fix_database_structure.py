#!/usr/bin/env python3
"""
ERSTELLT DIE FEHLENDEN DATENBANK-TABELLEN FÜR LASTPROFILE!
"""

import sqlite3
import json
from datetime import datetime

def create_load_profile_tables():
    """Erstellt die fehlenden Tabellen für Lastprofile"""
    
    print("🗄️ ERSTELLE FEHLENDE DATENBANK-TABELLEN!")
    print("=" * 60)
    
    try:
        # Verbindung zur Datenbank
        conn = sqlite3.connect('instance/bess.db')
        cursor = conn.cursor()
        
        # Prüfe ob load_profiles Tabelle existiert
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='load_profiles'
        """)
        
        if not cursor.fetchone():
            print("📋 Erstelle load_profiles Tabelle...")
            cursor.execute("""
                CREATE TABLE load_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    project_id INTEGER NOT NULL,
                    data_type TEXT DEFAULT 'load',
                    created_at TEXT NOT NULL,
                    updated_at TEXT,
                    FOREIGN KEY (project_id) REFERENCES projects (id)
                )
            """)
            print("✅ load_profiles Tabelle erstellt")
        else:
            print("✅ load_profiles Tabelle bereits vorhanden")
        
        # Prüfe ob load_profile_data Tabelle existiert
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='load_profile_data'
        """)
        
        if not cursor.fetchone():
            print("📋 Erstelle load_profile_data Tabelle...")
            cursor.execute("""
                CREATE TABLE load_profile_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    load_profile_id INTEGER NOT NULL,
                    timestamp TEXT NOT NULL,
                    value REAL NOT NULL,
                    unit TEXT DEFAULT 'kW',
                    metadata TEXT,
                    FOREIGN KEY (load_profile_id) REFERENCES load_profiles (id)
                )
            """)
            print("✅ load_profile_data Tabelle erstellt")
        else:
            print("✅ load_profile_data Tabelle bereits vorhanden")
        
        # Prüfe ob projects Tabelle existiert
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='projects'
        """)
        
        if not cursor.fetchone():
            print("📋 Erstelle projects Tabelle...")
            cursor.execute("""
                CREATE TABLE projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    customer_id INTEGER,
                    bess_size REAL,
                    bess_power REAL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT,
                    FOREIGN KEY (customer_id) REFERENCES customers (id)
                )
            """)
            print("✅ projects Tabelle erstellt")
            
            # Erstelle Standard-Projekt
            cursor.execute("""
                INSERT INTO projects (name, description, created_at)
                VALUES (?, ?, ?)
            """, ('BESS Hinterstoder', 'Standard BESS-Projekt für Hinterstoder', datetime.now().isoformat()))
            print("✅ Standard-Projekt 'BESS Hinterstoder' erstellt")
        else:
            print("✅ projects Tabelle bereits vorhanden")
        
        # Prüfe ob customers Tabelle existiert
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='customers'
        """)
        
        if not cursor.fetchone():
            print("📋 Erstelle customers Tabelle...")
            cursor.execute("""
                CREATE TABLE customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT,
                    phone TEXT,
                    address TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT
                )
            """)
            print("✅ customers Tabelle erstellt")
            
            # Erstelle Standard-Kunde
            cursor.execute("""
                INSERT INTO customers (name, email, created_at)
                VALUES (?, ?, ?)
            """, ('Standard Kunde', 'kunde@example.com', datetime.now().isoformat()))
            print("✅ Standard-Kunde erstellt")
        else:
            print("✅ customers Tabelle bereits vorhanden")
        
        # Commit und schließen
        conn.commit()
        conn.close()
        
        print("✅ Alle fehlenden Tabellen erfolgreich erstellt!")
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Erstellen der Tabellen: {e}")
        return False

def create_water_level_load_profiles():
    """Erstellt die Wasserstand-Lastprofile nach der Tabellen-Erstellung"""
    
    print("🌊 ERSTELLE WASSERSTAND-LASTPROFILE!")
    print("=" * 60)
    
    try:
        # Verbindung zur Datenbank
        conn = sqlite3.connect('instance/bess.db')
        cursor = conn.cursor()
        
        # Hole alle Wasserstanddaten für Steyr
        cursor.execute("""
            SELECT timestamp, water_level_cm, river_name, station_name
            FROM water_levels 
            WHERE river_name = 'Steyr'
            ORDER BY timestamp
            LIMIT 1000
        """)
        water_level_data = cursor.fetchall()
        
        if not water_level_data:
            print("❌ Keine Wasserstanddaten für Steyr gefunden!")
            return None
        
        print(f"📊 {len(water_level_data)} Wasserstanddaten für Steyr gefunden")
        
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
    
    print("🚀 BEHEBE DATENBANK-STRUKTUR UND ERSTELLE LASTPROFILE!")
    print("=" * 60)
    
    # Erstelle fehlende Tabellen
    if create_load_profile_tables():
        # Erstelle Wasserstand-Lastprofile
        result = create_water_level_load_profiles()
        
        print("\n" + "=" * 60)
        print("🎯 DATENBANK-BEHEBUNG ABGESCHLOSSEN!")
        
        if result:
            water_id, hydro_id = result
            print(f"✅ Wasserstand-Lastprofil: ID {water_id}")
            print(f"✅ Wasserkraft-Lastprofil: ID {hydro_id}")
        
        print("🌐 Öffnen Sie: http://127.0.0.1:5000/bess_peak_shaving_analysis")
        print("🎯 Jetzt können Sie die Wasserstand-Lastprofile auswählen!")
    else:
        print("❌ Fehler bei der Datenbank-Behebung!")

if __name__ == "__main__":
    main() 