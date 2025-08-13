#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import von Demo-PV- und Wasserkraftdaten für das Last & Erzeugung Overlay
Erstellt realistische Daten basierend auf den Screenshots
"""

import sqlite3
import os
from datetime import datetime, timedelta
import random
import math

def create_demo_pv_hydro_data():
    """Erstellt Demo-PV- und Wasserkraftdaten für 2024"""
    
    # Datenbank verbinden
    db_path = 'instance/bess.db'
    if not os.path.exists(db_path):
        print(f"❌ Datenbank nicht gefunden: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Tabellen erstellen falls nicht vorhanden
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pvsol_export (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            power_kw REAL NOT NULL,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )
    """)
    
    # water_levels Tabelle existiert bereits mit anderer Struktur
    # Wir erstellen eine neue Tabelle für Wasserkraft-Leistung
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hydro_power (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            power_kw REAL NOT NULL,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )
    """)
    
    # Alte Demo-Daten löschen
    cursor.execute("DELETE FROM pvsol_export WHERE project_id = 1")
    cursor.execute("DELETE FROM hydro_power WHERE project_id = 1")
    
    # Zeitraum: 1.1.2024 bis 31.12.2024 (stündlich)
    start_date = datetime(2024, 1, 1, 0, 0, 0)
    end_date = datetime(2024, 12, 31, 23, 0, 0)
    
    current_date = start_date
    data_points = 0
    
    print("🔄 Erstelle Demo-PV- und Wasserkraftdaten...")
    
    while current_date <= end_date:
        # Wasserkraft: Konstant mit saisonalen Schwankungen
        # Winter: 150-200 kW, Sommer: 300-400 kW
        month = current_date.month
        if month in [12, 1, 2]:  # Winter
            hydro_base = random.uniform(150, 200)
        elif month in [6, 7, 8]:  # Sommer
            hydro_base = random.uniform(300, 400)
        else:  # Übergangszeit
            hydro_base = random.uniform(200, 300)
        
        # Kleine Schwankungen
        hydro_power = hydro_base + random.uniform(-20, 20)
        
        # PV-Erzeugung: Nur tagsüber, saisonal abhängig
        hour = current_date.hour
        if 6 <= hour <= 20:  # Tagsüber
            # Saisonale Anpassung basierend auf Screenshots
            if month in [12, 1, 2]:  # Winter (Dezember Screenshot)
                max_pv = random.uniform(400, 500)
            elif month in [3, 4]:  # Frühling (April Screenshot)
                max_pv = random.uniform(1800, 2000)
            elif month in [6, 7, 8]:  # Sommer (August Screenshot)
                max_pv = random.uniform(1600, 1900)
            else:  # Herbst
                max_pv = random.uniform(800, 1200)
            
            # Tagesgang (Glockenkurve)
            peak_hour = 13  # Mittags
            time_factor = math.exp(-((hour - peak_hour) ** 2) / 8)
            pv_power = max_pv * time_factor * random.uniform(0.7, 1.0)
        else:
            pv_power = 0
        
        # Daten einfügen
        timestamp = current_date.strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute(
            "INSERT INTO pvsol_export (project_id, timestamp, power_kw) VALUES (?, ?, ?)",
            (1, timestamp, pv_power)
        )
        
        cursor.execute(
            "INSERT INTO hydro_power (project_id, timestamp, power_kw) VALUES (?, ?, ?)",
            (1, timestamp, hydro_power)
        )
        
        data_points += 1
        current_date += timedelta(hours=1)
    
    conn.commit()
    conn.close()
    
    print(f"✅ Demo-Daten erfolgreich erstellt!")
    print(f"   📊 Datenpunkte: {data_points}")
    print(f"   📅 Zeitraum: {start_date.strftime('%d.%m.%Y')} bis {end_date.strftime('%d.%m.%Y')}")
    print(f"   ⚡ PV-Erzeugung: 0-2000 kW (saisonal)")
    print(f"   💧 Wasserkraft: 150-400 kW (saisonal)")

if __name__ == "__main__":
    create_demo_pv_hydro_data()
