import os
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Supabase Import nur wenn verfügbar
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("Supabase nicht verfügbar - Demo-Modus aktiviert")

class SupabaseMultiUser:
    def __init__(self):
        """Initialisiert die Supabase-Verbindung für Multi-User Funktionalität"""
        self.supabase_url = os.environ.get("SUPABASE_URL", "https://your-project.supabase.co")
        self.supabase_key = os.environ.get("SUPABASE_KEY", "your-anon-key")
        
        # Demo-Modus wenn Supabase nicht verfügbar oder ungültige Schlüssel
        if not SUPABASE_AVAILABLE or self.supabase_url == "https://your-project.supabase.co" or self.supabase_key == "your-anon-key":
            self.demo_mode = True
            self.supabase = None
            print("🔧 Demo-Modus aktiviert - Verwende lokale Daten")
        else:
            self.demo_mode = False
            try:
                self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
                print("✅ Supabase-Verbindung erfolgreich")
            except Exception as e:
                print(f"⚠️ Supabase-Fehler: {e} - Demo-Modus aktiviert")
                self.demo_mode = True
                self.supabase = None
    
    def get_current_user_id(self) -> Optional[str]:
        """Holt die aktuelle User-ID aus der Supabase Session"""
        if self.demo_mode:
            return "demo-user-123"
        
        try:
            user = self.supabase.auth.get_user()
            if user and user.user:
                return user.user.id
            return None
        except Exception as e:
            print(f"Fehler beim Abrufen der User-ID: {e}")
            return "demo-user-123"
    
    def get_user_projects(self, user_id: str) -> List[Dict]:
        """Holt alle Projekte eines Benutzers"""
        if self.demo_mode:
            # Demo-Daten zurückgeben
            return [
                {
                    'id': 'demo-project-1',
                    'name': 'Demo BESS Projekt',
                    'description': 'Ein Beispiel-BESS-Projekt für Demonstrationszwecke',
                    'bess_capacity_kwh': 1000.0,
                    'bess_power_kw': 500.0,
                    'solar_capacity_kw': 200.0,
                    'hydro_capacity_kw': 0.0,
                    'investment_cost_per_kwh': 0.25,
                    'electricity_cost_per_kwh': 0.12,
                    'created_at': '2024-01-15T10:00:00Z',
                    'updated_at': '2024-01-15T10:00:00Z'
                }
            ]
        
        try:
            response = self.supabase.table('projects').select('*').eq('user_id', user_id).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Fehler beim Abrufen der Projekte: {e}")
            return []
    
    def get_project_by_id(self, project_id: str, user_id: str) -> Optional[Dict]:
        """Holt ein spezifisches Projekt eines Benutzers"""
        if self.demo_mode:
            if project_id == 'demo-project-1':
                return {
                    'id': 'demo-project-1',
                    'name': 'Demo BESS Projekt',
                    'description': 'Ein Beispiel-BESS-Projekt für Demonstrationszwecke',
                    'bess_capacity_kwh': 1000.0,
                    'bess_power_kw': 500.0,
                    'solar_capacity_kw': 200.0,
                    'hydro_capacity_kw': 0.0,
                    'investment_cost_per_kwh': 0.25,
                    'electricity_cost_per_kwh': 0.12,
                    'created_at': '2024-01-15T10:00:00Z',
                    'updated_at': '2024-01-15T10:00:00Z'
                }
            return None
        
        try:
            response = self.supabase.table('projects').select('*').eq('id', project_id).eq('user_id', user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Fehler beim Abrufen des Projekts: {e}")
            return None
    
    def create_project(self, user_id: str, project_data: Dict) -> Tuple[bool, str, Optional[str]]:
        """Erstellt ein neues Projekt für einen Benutzer"""
        if self.demo_mode:
            project_id = f"demo-project-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            print(f"Demo: Projekt erstellt mit ID {project_id}")
            return True, "Projekt erfolgreich erstellt (Demo-Modus)", project_id
        
        try:
            project_data['user_id'] = user_id
            project_data['created_at'] = datetime.now().isoformat()
            project_data['updated_at'] = datetime.now().isoformat()
            
            response = self.supabase.table('projects').insert(project_data).execute()
            
            if response.data:
                return True, "Projekt erfolgreich erstellt", response.data[0]['id']
            else:
                return False, "Fehler beim Erstellen des Projekts", None
        except Exception as e:
            return False, f"Fehler beim Erstellen des Projekts: {e}", None
    
    def update_project(self, project_id: str, user_id: str, project_data: Dict) -> Tuple[bool, str]:
        """Aktualisiert ein bestehendes Projekt"""
        if self.demo_mode:
            print(f"Demo: Projekt {project_id} aktualisiert")
            return True, "Projekt erfolgreich aktualisiert (Demo-Modus)"
        
        try:
            project_data['updated_at'] = datetime.now().isoformat()
            
            response = self.supabase.table('projects').update(project_data).eq('id', project_id).eq('user_id', user_id).execute()
            
            if response.data:
                return True, "Projekt erfolgreich aktualisiert"
            else:
                return False, "Fehler beim Aktualisieren des Projekts"
        except Exception as e:
            return False, f"Fehler beim Aktualisieren des Projekts: {e}"
    
    def delete_project(self, project_id: str, user_id: str) -> Tuple[bool, str]:
        """Löscht ein Projekt eines Benutzers"""
        if self.demo_mode:
            print(f"Demo: Projekt {project_id} gelöscht")
            return True, "Projekt erfolgreich gelöscht (Demo-Modus)"
        
        try:
            response = self.supabase.table('projects').delete().eq('id', project_id).eq('user_id', user_id).execute()
            
            if response.data:
                return True, "Projekt erfolgreich gelöscht"
            else:
                return False, "Fehler beim Löschen des Projekts"
        except Exception as e:
            return False, f"Fehler beim Löschen des Projekts: {e}"
    
    def save_simulation_result(self, user_id: str, project_id: str, simulation_data: Dict) -> Tuple[bool, str, Optional[str]]:
        """Speichert ein Simulationsergebnis"""
        if self.demo_mode:
            result_id = f"demo-simulation-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            print(f"Demo: Simulationsergebnis gespeichert mit ID {result_id}")
            return True, "Simulationsergebnis erfolgreich gespeichert (Demo-Modus)", result_id
        
        try:
            result_data = {
                'user_id': user_id,
                'project_id': project_id,
                'simulation_date': datetime.now().isoformat(),
                'simulation_data': simulation_data,
                'created_at': datetime.now().isoformat()
            }
            
            # Berechne wirtschaftliche Kennzahlen
            if 'total_cost' in simulation_data:
                result_data['total_cost'] = simulation_data['total_cost']
            if 'total_savings' in simulation_data:
                result_data['total_savings'] = simulation_data['total_savings']
            if 'payback_period_years' in simulation_data:
                result_data['payback_period_years'] = simulation_data['payback_period_years']
            
            response = self.supabase.table('simulation_results').insert(result_data).execute()
            
            if response.data:
                return True, "Simulationsergebnis erfolgreich gespeichert", response.data[0]['id']
            else:
                return False, "Fehler beim Speichern des Simulationsergebnisses", None
        except Exception as e:
            return False, f"Fehler beim Speichern des Simulationsergebnisses: {e}", None
    
    def get_simulation_results(self, project_id: str, user_id: str) -> List[Dict]:
        """Holt alle Simulationsergebnisse eines Projekts"""
        if self.demo_mode:
            # Demo-Simulationsergebnisse
            return [
                {
                    'id': 'demo-sim-1',
                    'project_id': project_id,
                    'user_id': user_id,
                    'simulation_date': '2024-01-15T14:30:00Z',
                    'total_cost': 50000.0,
                    'total_savings': 15000.0,
                    'payback_period_years': 3.33,
                    'simulation_data': {
                        'bess_utilization': 85.5,
                        'peak_shaving_efficiency': 92.3,
                        'energy_savings_kwh': 15000
                    },
                    'created_at': '2024-01-15T14:30:00Z'
                }
            ]
        
        try:
            response = self.supabase.table('simulation_results').select('*').eq('project_id', project_id).eq('user_id', user_id).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Fehler beim Abrufen der Simulationsergebnisse: {e}")
            return []
    
    def migrate_sqlite_to_supabase(self, sqlite_db_path: str, user_id: str) -> Tuple[bool, str]:
        """Migriert Daten von SQLite zu Supabase (Hilfsfunktion)"""
        if self.demo_mode:
            return True, "Migration im Demo-Modus nicht verfügbar"
        
        try:
            import sqlite3
            from models import Project, Customer, LoadProfile
            
            # SQLite Verbindung
            conn = sqlite3.connect(sqlite_db_path)
            cursor = conn.cursor()
            
            # Projekte migrieren
            cursor.execute("SELECT * FROM project")
            projects = cursor.fetchall()
            
            for project in projects:
                project_data = {
                    'name': project[1] or 'Migriertes Projekt',
                    'description': project[2] or '',
                    'bess_capacity_kwh': project[3] or 0,
                    'bess_power_kw': project[4] or 0,
                    'solar_capacity_kw': project[5] or 0,
                    'hydro_capacity_kw': project[6] or 0,
                    'investment_cost_per_kwh': project[7] or 0,
                    'electricity_cost_per_kwh': project[8] or 0
                }
                
                success, message, project_id = self.create_project(user_id, project_data)
                if not success:
                    print(f"Fehler beim Migrieren von Projekt {project[1]}: {message}")
            
            conn.close()
            return True, f"{len(projects)} Projekte erfolgreich migriert"
            
        except Exception as e:
            return False, f"Fehler bei der Migration: {e}"
