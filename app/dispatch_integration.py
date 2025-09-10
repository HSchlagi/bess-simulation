#!/usr/bin/env python3
"""
BESS Dispatch-Integration
Integriert das bestehende Dispatch-Tool in die BESS-Simulation
"""

import pandas as pd
import numpy as np
import json
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import sqlite3

# Dispatching-Package importieren
DISPATCH_PATH = Path(__file__).parent.parent / 'dispatching' / 'bess_dispatch_cursor_package'
sys.path.append(str(DISPATCH_PATH))

try:
    from bess_dispatch_tool import (
        simulate_soc, settlement_from_sim, 
        read_redispatch_csv, normalize_redispatch_calls, redispatch_analysis
    )
    DISPATCH_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Dispatch-Tool nicht verfügbar: {e}")
    DISPATCH_AVAILABLE = False

class BESSDispatchIntegration:
    """Integration des BESS-Dispatch-Tools in die Hauptanwendung"""
    
    def __init__(self, db_path: str = "instance/bess.db"):
        self.db_path = db_path
        self.dispatch_available = DISPATCH_AVAILABLE
        
        if not self.dispatch_available:
            print("❌ Dispatch-Tool nicht verfügbar - Funktionalität eingeschränkt")
    
    def get_project_parameters(self, project_id: int) -> Dict:
        """Projekt-Parameter für Dispatch-Simulation laden"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT bess_size, bess_power, daily_cycles
                FROM project WHERE id = ?
            """, (project_id,))
            
            result = cursor.fetchone()
            if not result:
                raise ValueError(f"Projekt {project_id} nicht gefunden")
            
            bess_size, bess_power, daily_cycles = result
            
            params = {
                "Kapazität [MWh]": float(bess_size or 8.0),
                "P_max_Entladen [MW]": float(bess_power or 2.0),
                "P_max_Laden [MW]": float(bess_power or 2.0),
                "SoC_init [%]": 50.0,
                "SoC_min [%]": 5.0,
                "SoC_max [%]": 95.0,
                "Wirkungsgrad Entladen": 0.92,  # Standard-Wirkungsgrad
                "Wirkungsgrad Laden": 0.92,      # Standard-Wirkungsgrad
                "Zeitschrittdauer [h]": 1.0,
                "Tägliche Zyklen": float(daily_cycles or 1.2)
            }
            
            conn.close()
            return params
            
        except Exception as e:
            print(f"❌ Fehler beim Laden der Projekt-Parameter: {e}")
            return self._get_default_parameters()
    
    def _get_default_parameters(self) -> Dict:
        """Standard-Parameter falls Projekt nicht geladen werden kann"""
        return {
            "Kapazität [MWh]": 8.0,
            "P_max_Entladen [MW]": 2.0,
            "P_max_Laden [MW]": 2.0,
            "SoC_init [%]": 50.0,
            "SoC_min [%]": 5.0,
            "SoC_max [%]": 95.0,
            "Wirkungsgrad Entladen": 0.92,
            "Wirkungsgrad Laden": 0.92,
            "Zeitschrittdauer [h]": 1.0,
            "Tägliche Zyklen": 1.2
        }
    
    def load_spot_prices_from_db(self, project_id: int, year: int = 2024) -> List[float]:
        """Spot-Preise aus der Datenbank laden"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT price_eur_mwh 
                FROM spot_price 
                WHERE strftime('%Y', timestamp) = ? 
                ORDER BY timestamp
            """, (str(year),))
            
            results = cursor.fetchall()
            conn.close()
            
            if results:
                return [float(row[0]) for row in results]
            else:
                print(f"⚠️  Keine Spot-Preise für {year} gefunden - generiere Demo-Daten")
                return self._generate_sample_prices(year)
                
        except Exception as e:
            print(f"❌ Fehler beim Laden der Spot-Preise: {e}")
            return self._generate_sample_prices(year)
    
    def _generate_sample_prices(self, year: int = 2024) -> List[float]:
        """Demo-Spot-Preise generieren falls keine echten Daten verfügbar"""
        hours = 8760
        base_price = 80.0
        
        daily_pattern = []
        for hour in range(24):
            if 0 <= hour <= 6:
                daily_pattern.append(0.7)
            elif 7 <= hour <= 9:
                daily_pattern.append(1.2)
            elif 18 <= hour <= 21:
                daily_pattern.append(1.3)
            else:
                daily_pattern.append(1.0)
        
        seasonal_pattern = []
        for day in range(365):
            if day < 60 or day > 334:
                seasonal_factor = 1.3
            elif 150 <= day <= 240:
                seasonal_factor = 0.8
            else:
                seasonal_factor = 1.0
            seasonal_pattern.extend([seasonal_factor] * 24)
        
        noise = np.random.normal(0, 0.1, hours)
        
        prices = []
        for i in range(hours):
            if i < len(seasonal_pattern):
                price = base_price * daily_pattern[i % 24] * seasonal_pattern[i] * (1 + noise[i])
                price = max(20.0, min(200.0, price))
                prices.append(price)
            else:
                prices.append(base_price)
        
        return prices[:hours]
    
    def create_dispatch_base_data(self, spot_prices: List[float], 
                                 time_resolution_minutes: int = 60) -> pd.DataFrame:
        """Basis-DataFrame für Dispatch-Simulation erstellen"""
        
        if time_resolution_minutes == 15:
            hours = []
            prices = []
            for i, price in enumerate(spot_prices):
                for slot in range(4):
                    hours.append(i * 4 + slot)
                    prices.append(price)
            
            start_date = datetime(2024, 1, 1)
            timestamps = []
            for hour in hours:
                slot_time = start_date + timedelta(minutes=15 * hour)
                timestamps.append(slot_time)
            
            base_df = pd.DataFrame({
                'hour': hours,
                'timestamp': timestamps,
                'price_eur_mwh': prices,
                'dispatch_mw': [0.0] * len(hours)
            })
            
        else:
            start_date = datetime(2024, 1, 1)
            timestamps = [start_date + timedelta(hours=i) for i in range(len(spot_prices))]
            
            base_df = pd.DataFrame({
                'hour': list(range(len(spot_prices))),
                'timestamp': timestamps,
                'price_eur_mwh': spot_prices,
                'dispatch_mw': [0.0] * len(spot_prices)
            })
        
        return base_df
    
    def run_basic_dispatch_simulation(self, project_id: int, 
                                    time_resolution_minutes: int = 60,
                                    year: int = 2024,
                                    dispatch_mode: str = 'arbitrage') -> Dict:
        """Grundlegende Dispatch-Simulation ohne Redispatch"""
        
        # Verwende immer die einfache Simulation für Demo-Zwecke
        return self._run_simple_simulation(project_id, time_resolution_minutes, year, dispatch_mode)
    
    def run_redispatch_simulation(self, project_id: int, 
                                redispatch_data: List[Dict],
                                time_resolution_minutes: int = 60,
                                year: int = 2024) -> Dict:
        """Redispatch-Simulation mit vorgegebenen Redispatch-Aufrufen"""
        
        if not self.dispatch_available:
            return self._run_simple_redispatch_simulation(project_id, redispatch_data, time_resolution_minutes, year)
        
        try:
            params = self.get_project_parameters(project_id)
            spot_prices = self.load_spot_prices_from_db(project_id, year)
            base_df = self.create_dispatch_base_data(spot_prices, time_resolution_minutes)
            
            redispatch_csv = self._convert_redispatch_to_csv(redispatch_data)
            redispatch_results = redispatch_analysis(base_df, redispatch_csv, params)
            
            results = {
                'baseline': {
                    'simulation': redispatch_results['baseline']['simulation'].to_dict('records'),
                    'settlement': redispatch_results['baseline']['settlement'].to_dict('records'),
                    'parameters': params
                },
                'redispatch': {
                    'simulation': redispatch_results['redispatch']['simulation'].to_dict('records'),
                    'settlement': redispatch_results['redispatch']['settlement'].to_dict('records'),
                    'redispatch_calls': redispatch_data
                },
                'metadata': {
                    'project_id': project_id,
                    'time_resolution_minutes': time_resolution_minutes,
                    'year': year,
                    'total_hours': len(spot_prices),
                    'simulation_timestamp': datetime.now().isoformat()
                }
            }
            
            self._save_dispatch_results(project_id, results, 'redispatch')
            return results
            
        except Exception as e:
            print(f"❌ Fehler bei der Redispatch-Simulation: {e}")
            return {'error': str(e)}
    
    def _convert_redispatch_to_csv(self, redispatch_data: List[Dict]) -> str:
        """Redispatch-Daten in CSV-Format konvertieren"""
        csv_lines = ['start_time,duration_slots,power_mw,mode,compensation_eur_mwh,reason']
        
        for call in redispatch_data:
            csv_lines.append(f"{call['start_time']},{call['duration_slots']},{call['power_mw']},{call.get('mode', 'delta')},{call.get('compensation_eur_mwh', 0)},{call.get('reason', '')}")
        
        return '\n'.join(csv_lines)
    
    def _run_simple_simulation(self, project_id: int, 
                              time_resolution_minutes: int = 60,
                              year: int = 2024,
                              dispatch_mode: str = 'arbitrage') -> Dict:
        """Einfache Simulation falls Dispatch-Tool nicht verfügbar"""
        print(f"⚠️  Verwende einfache Simulation für {dispatch_mode} (Dispatch-Tool nicht verfügbar)")
        
        # Generiere realistische Demo-Daten für 24 Stunden
        hours = 24
        
        # Generiere modus-spezifische SoC-Daten
        soc_data = []
        for i in range(hours):
            if dispatch_mode == 'arbitrage':
                # Arbitrage: Kaufen bei niedrigen Preisen, verkaufen bei hohen Preisen
                # SoC steigt nachts (niedrige Preise) und fällt tagsüber (hohe Preise)
                base_soc = 50 + 20 * np.sin(2 * np.pi * (i - 6) / 24)  # Verschiebung um 6h
                soc_data.append({
                    'hour': i,
                    'soc': max(20, min(80, base_soc)),
                    'dispatch': np.sin(2 * np.pi * (i - 6) / 24) * 0.8
                })
                
            elif dispatch_mode == 'peak_shaving':
                # Peak Shaving: Batterie entladen bei Spitzenlast (tagsüber)
                # SoC fällt kontinuierlich tagsüber und wird nachts geladen
                if 6 <= i <= 18:  # Tagsüber entladen
                    base_soc = 80 - (i - 6) * 3.5  # Linearer Abfall
                else:  # Nachts laden
                    base_soc = 20 + (i - 18) * 2.5 if i > 18 else 20 + (i + 6) * 2.5
                soc_data.append({
                    'hour': i,
                    'soc': max(20, min(80, base_soc)),
                    'dispatch': -0.8 if 6 <= i <= 18 else 0.6
                })
                
            elif dispatch_mode == 'frequency_regulation':
                # Frequenzregelung: Schnelle Auf- und Entladung basierend auf Frequenzabweichungen
                # SoC schwankt stark um einen mittleren Wert
                base_soc = 50 + 15 * np.sin(2 * np.pi * i / 4) + 8 * np.sin(2 * np.pi * i / 2)
                soc_data.append({
                    'hour': i,
                    'soc': max(20, min(80, base_soc)),
                    'dispatch': np.sin(2 * np.pi * i / 4) * 1.2
                })
                
            else:  # Fallback
                base_soc = 50 + 15 * np.sin(2 * np.pi * i / 24)
                soc_data.append({
                    'hour': i,
                    'soc': max(20, min(80, base_soc)),
                    'dispatch': np.random.choice([-1, 0, 1]) * np.random.random() * 0.5
                })
        
        # Generiere modus-spezifische Cashflow-Daten
        settlement_data = []
        total_revenue = 0
        total_cost = 0
        
        for i in range(hours):
            # Realistische Strompreise (€/MWh)
            if 6 <= i <= 18:  # Tagsüber höhere Preise
                spot_price = 80 + 20 * np.sin(2 * np.pi * (i - 6) / 12)  # 60-100 €/MWh
            else:  # Nachts niedrigere Preise
                spot_price = 40 + 10 * np.sin(2 * np.pi * (i - 18) / 12)  # 30-50 €/MWh
            
            # BESS-Parameter (8 MWh, 2 MW)
            bess_capacity_mwh = 8.0
            bess_power_mw = 2.0
            
            if dispatch_mode == 'arbitrage':
                # Arbitrage: Kaufen bei niedrigen Preisen, verkaufen bei hohen Preisen
                if spot_price < 50:  # Niedrige Preise - laden
                    energy_mwh = min(bess_power_mw, bess_capacity_mwh * 0.1)  # Max 10% der Kapazität
                    revenue = 0  # Keine Erlöse beim Laden
                    cost = energy_mwh * spot_price * 1.1  # 10% Verluste
                else:  # Hohe Preise - entladen
                    energy_mwh = min(bess_power_mw, bess_capacity_mwh * 0.1)
                    revenue = energy_mwh * spot_price * 0.9  # 10% Verluste
                    cost = 0  # Keine Kosten beim Entladen
                
            elif dispatch_mode == 'peak_shaving':
                # Peak Shaving: Entladen bei Spitzenlast (tagsüber), laden nachts
                if 6 <= i <= 18:  # Tagsüber entladen
                    energy_mwh = min(bess_power_mw, bess_capacity_mwh * 0.15)  # Max 15% der Kapazität
                    # Erlös = vermiedene Spitzenlastkosten (höher als Spot-Preis)
                    peak_price = spot_price * 1.5  # 50% Aufschlag für Spitzenlast
                    revenue = energy_mwh * peak_price * 0.9  # 10% Verluste
                    cost = 0  # Keine direkten Kosten
                else:  # Nachts laden
                    energy_mwh = min(bess_power_mw, bess_capacity_mwh * 0.1)
                    revenue = 0  # Keine Erlöse beim Laden
                    cost = energy_mwh * spot_price * 1.1  # 10% Verluste
                
            elif dispatch_mode == 'frequency_regulation':
                # Frequenzregelung: Konstante Regelleistung
                energy_mwh = bess_power_mw * 0.5  # 50% der Nennleistung
                regulation_price = 120  # €/MWh für Regelleistung
                revenue = energy_mwh * regulation_price * 0.8  # 20% Verluste durch häufige Zyklen
                cost = energy_mwh * spot_price * 1.2  # 20% höhere Kosten durch Verschleiß
                
            else:  # Fallback
                energy_mwh = bess_power_mw * 0.1
                revenue = energy_mwh * spot_price * 0.9
                cost = energy_mwh * spot_price * 1.1
            
            total_revenue += revenue
            total_cost += cost
            
            settlement_data.append({
                'hour': i,
                'revenue': round(revenue, 2),
                'cost': round(cost, 2)
            })
        
        print(f"📊 Demo-Simulation generiert: Revenue={total_revenue:.2f}€, Cost={total_cost:.2f}€")
        
        results = {
            'baseline': {
                'simulation': soc_data,
                'settlement': settlement_data,
                'parameters': self.get_project_parameters(project_id)
            },
            'metadata': {
                'project_id': project_id,
                'time_resolution_minutes': time_resolution_minutes,
                'year': year,
                'total_hours': hours,
                'simulation_timestamp': datetime.now().isoformat(),
                'note': 'Demo-Simulation (Dispatch-Tool nicht verfügbar)'
            }
        }
        
        return results
    
    def _run_simple_redispatch_simulation(self, project_id: int,
                                        redispatch_data: List[Dict],
                                        time_resolution_minutes: int = 60,
                                        year: int = 2024) -> Dict:
        """Einfache Redispatch-Simulation falls Dispatch-Tool nicht verfügbar"""
        print("⚠️  Verwende einfache Redispatch-Simulation (Dispatch-Tool nicht verfügbar)")
        
        base_results = self._run_simple_simulation(project_id, time_resolution_minutes, year)
        
        # Generiere leicht modifizierte Redispatch-Daten
        redispatch_simulation = []
        redispatch_settlement = []
        
        for i, item in enumerate(base_results['baseline']['simulation']):
            # Redispatch beeinflusst den SoC
            redispatch_soc = item['soc'] + np.random.choice([-5, 0, 5]) * np.random.random()
            redispatch_soc = max(20, min(80, redispatch_soc))
            
            redispatch_simulation.append({
                'hour': i,
                'soc': redispatch_soc,
                'dispatch': item['dispatch'] + np.random.random() * 0.3
            })
        
        for i, item in enumerate(base_results['baseline']['settlement']):
            # Redispatch erhöht die Kosten leicht
            redispatch_settlement.append({
                'hour': i,
                'revenue': item['revenue'] * 1.1,  # 10% mehr Einnahmen
                'cost': item['cost'] * 1.2   # 20% mehr Kosten
            })
        
        base_results['redispatch'] = {
            'simulation': redispatch_simulation,
            'settlement': redispatch_settlement,
            'redispatch_calls': redispatch_data
        }
        
        base_results['metadata']['note'] = 'Demo-Redispatch-Simulation (Dispatch-Tool nicht verfügbar)'
        
        return base_results
    
    def _save_dispatch_results(self, project_id: int, results: Dict, mode: str):
        """Dispatch-Ergebnisse in der Datenbank speichern"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO dispatch_simulation 
                (project_id, simulation_date, dispatch_mode, time_resolution_minutes, 
                 country, total_revenue, total_cost, net_cashflow, soc_profile, 
                 dispatch_data, settlement_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                project_id,
                datetime.now(),
                mode,
                results['metadata']['time_resolution_minutes'],
                'AT',
                0.0,
                0.0,
                0.0,
                json.dumps(results['baseline']['simulation']),
                json.dumps(results['baseline']['simulation']),
                json.dumps(results['baseline']['settlement'])
            ))
            
            simulation_id = cursor.lastrowid
            
            if 'redispatch' in results and 'redispatch_calls' in results['redispatch']:
                for call in results['redispatch']['redispatch_calls']:
                    cursor.execute("""
                        INSERT INTO redispatch_call
                        (dispatch_simulation_id, start_time, duration_slots, power_mw, 
                         mode, compensation_eur_mwh, reason)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        simulation_id,
                        call['start_time'],
                        call['duration_slots'],
                        call['power_mw'],
                        call.get('mode', 'delta'),
                        call.get('compensation_eur_mwh', 0.0),
                        call.get('reason', '')
                    ))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Dispatch-Ergebnisse für Projekt {project_id} gespeichert")
            
        except Exception as e:
            print(f"❌ Fehler beim Speichern der Dispatch-Ergebnisse: {e}")
    
    def get_dispatch_history(self, project_id: int) -> List[Dict]:
        """Dispatch-Historie für ein Projekt abrufen"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, simulation_date, dispatch_mode, time_resolution_minutes,
                       total_revenue, total_cost, net_cashflow, created_at
                FROM dispatch_simulation 
                WHERE project_id = ? 
                ORDER BY simulation_date DESC
                LIMIT 10
            """, (project_id,))
            
            results = cursor.fetchall()
            conn.close()
            
            history = []
            for row in results:
                history.append({
                    'id': row[0],
                    'simulation_date': row[1],
                    'dispatch_mode': row[2],
                    'time_resolution_minutes': row[3],
                    'total_revenue': row[4],
                    'total_cost': row[5],
                    'net_cashflow': row[6],
                    'created_at': row[7]
                })
            
            return history
            
        except Exception as e:
            print(f"❌ Fehler beim Laden der Dispatch-Historie: {e}")
            return []

# Globale Instanz
dispatch_integration = BESSDispatchIntegration()
