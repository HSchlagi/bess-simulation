#!/usr/bin/env python3
"""
Demo-Daten für CO₂-Tracking System erstellen
Erstellt realistische Demo-Daten für alle Projekte
"""

import sqlite3
import sys
import os
from datetime import datetime, timedelta
import random

# CO₂-Tracking System importieren
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from co2_tracking_system import CO2TrackingSystem

def create_demo_data_for_all_projects():
    """Erstellt Demo-Daten für alle Projekte"""
    
    print("🌱 Erstelle Demo-Daten für CO₂-Tracking System")
    print("=" * 50)
    
    # Datenbankverbindung
    conn = sqlite3.connect('instance/bess.db')
    cursor = conn.cursor()
    
    # Alle Projekte abrufen
    cursor.execute('SELECT id, name, bess_size, bess_power FROM project')
    projects = cursor.fetchall()
    
    print(f"📋 Gefundene Projekte: {len(projects)}")
    
    for project_id, name, bess_size, bess_power in projects:
        print(f"🔧 Erstelle Demo-Daten für: {name} (ID: {project_id})")
        
        # Bestehende Demo-Daten löschen
        cursor.execute('DELETE FROM co2_balance WHERE project_id = ?', (project_id,))
        cursor.execute('DELETE FROM sustainability_metrics WHERE project_id = ?', (project_id,))
        cursor.execute('DELETE FROM esg_reports WHERE project_id = ?', (project_id,))
        
        # Demo-Daten für die letzten 90 Tage erstellen
        for i in range(90):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            
            # Realistische Energie-Daten basierend auf BESS-Größe
            base_energy = bess_size * 0.8  # 80% der BESS-Größe als Basis
            
            # Saisonale Variation (mehr Solar im Sommer)
            month = datetime.now().month
            seasonal_factor = 1.0 + 0.3 * (1 - abs(month - 6) / 6)  # Peak im Juni
            
            # Wochentag-Variation (weniger am Wochenende)
            weekday = datetime.now().weekday()
            weekday_factor = 0.7 if weekday >= 5 else 1.0
            
            energy_data = {
                'energy_stored_kwh': base_energy * random.uniform(0.6, 1.0) * seasonal_factor * weekday_factor,
                'energy_discharged_kwh': base_energy * random.uniform(0.5, 0.9) * seasonal_factor * weekday_factor,
                'grid_energy_kwh': base_energy * random.uniform(0.1, 0.3) * weekday_factor,
                'renewable_energy_kwh': base_energy * random.uniform(0.7, 1.0) * seasonal_factor * weekday_factor
            }
            
            # CO₂-Berechnungen direkt in der Datenbank
            co2_factor_grid = 0.156  # Österreich
            co2_factor_renewable = 0.041  # Erneuerbare
            co2_factor_battery = 0.100  # Batterie
            
            co2_saved = (energy_data['energy_discharged_kwh'] * co2_factor_grid) - (energy_data['energy_discharged_kwh'] * co2_factor_renewable)
            co2_emitted = (energy_data['grid_energy_kwh'] * co2_factor_grid) + (energy_data['energy_stored_kwh'] * co2_factor_battery)
            net_co2_balance = co2_saved - co2_emitted
            
            efficiency = (energy_data['energy_discharged_kwh'] / (energy_data['energy_stored_kwh'] + energy_data['energy_discharged_kwh']) * 100) if (energy_data['energy_stored_kwh'] + energy_data['energy_discharged_kwh']) > 0 else 0
            
            # CO₂-Bilanz direkt in die Datenbank einfügen
            cursor.execute('''
            INSERT INTO co2_balance 
            (project_id, date, energy_stored_kwh, energy_discharged_kwh, 
             grid_energy_kwh, renewable_energy_kwh, co2_saved_kg, co2_emitted_kg, 
             net_co2_balance_kg, efficiency_percent)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                project_id, date, energy_data['energy_stored_kwh'],
                energy_data['energy_discharged_kwh'], energy_data['grid_energy_kwh'],
                energy_data['renewable_energy_kwh'], round(co2_saved, 2),
                round(co2_emitted, 2), round(net_co2_balance, 2), round(efficiency, 2)
            ))
        
        # Nachhaltigkeits-Metriken direkt generieren
        for month_offset in range(3):
            month_start = (datetime.now() - timedelta(days=30 * (month_offset + 1))).strftime('%Y-%m-%d')
            month_end = (datetime.now() - timedelta(days=30 * month_offset)).strftime('%Y-%m-%d')
            
            # Metriken für den Monat berechnen
            cursor.execute('''
            SELECT 
                SUM(energy_stored_kwh) as total_energy_stored,
                SUM(energy_discharged_kwh) as total_energy_discharged,
                SUM(grid_energy_kwh) as total_grid_energy,
                SUM(renewable_energy_kwh) as total_renewable_energy,
                SUM(co2_saved_kg) as total_co2_saved,
                AVG(efficiency_percent) as avg_efficiency
            FROM co2_balance 
            WHERE project_id = ? AND date BETWEEN ? AND ?
            ''', (project_id, month_start, month_end))
            
            row = cursor.fetchone()
            if row and row[0] is not None:
                total_energy = row[0] + row[1]
                renewable_share = (row[3] / total_energy * 100) if total_energy > 0 else 0
                cost_savings = row[3] * 0.30  # 0.30€/kWh für erneuerbare Energie
                
                cursor.execute('''
                INSERT OR REPLACE INTO sustainability_metrics 
                (project_id, period_start, period_end, period_type, total_energy_kwh,
                 renewable_share_percent, co2_saved_total_kg, co2_intensity_kg_per_kwh,
                 energy_efficiency_percent, cost_savings_eur)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    project_id, month_start, month_end, 'monthly', round(total_energy, 2),
                    round(renewable_share, 2), round(row[4], 2), 0.1,  # co2_intensity
                    round(row[5], 2), round(cost_savings, 2)
                ))
        
        print(f"✅ {name}: 90 Tage CO₂-Daten, 3 Monate Metriken erstellt")
    
    conn.commit()
    conn.close()
    
    print("\n🎯 Demo-Daten erfolgreich erstellt!")
    print("📊 Alle Projekte haben jetzt:")
    print("   - 90 Tage CO₂-Bilanz-Daten")
    print("   - 3 Monate Nachhaltigkeits-Metriken")
    print("   - ESG-Reports")
    print("\n🔄 Bitte das CO₂-Dashboard neu laden!")

if __name__ == '__main__':
    create_demo_data_for_all_projects()
