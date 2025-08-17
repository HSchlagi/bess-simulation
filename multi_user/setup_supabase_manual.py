#!/usr/bin/env python3
"""
Manuelles Supabase Setup für BESS-Simulation Multi-User
=======================================================

Dieses Skript führt die SQL-Befehle manuell aus, da die exec_sql Funktion nicht verfügbar ist.
Die Befehle müssen manuell im Supabase Dashboard ausgeführt werden.
"""

import os
from supabase import create_client, Client

# Supabase-Konfiguration
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL:
    SUPABASE_URL = "https://wxkbyeueyrxoevcwwqop.supabase.co"
if not SUPABASE_KEY:
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind4a2J5ZXVleXJ4b2V2Y3d3cW9wIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk2NDQ4OTAsImV4cCI6MjA2NTIyMDg5MH0.5VUcUYlANZf_GkGrd2vPWDsduS9OaIfIhSiS1xsXONU"

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Supabase-Verbindung hergestellt")
except Exception as e:
    print(f"❌ Supabase-Verbindung fehlgeschlagen: {e}")
    exit(1)

def check_existing_tables():
    """Prüft, welche Tabellen bereits existieren"""
    print("\n🔍 Prüfe existierende Tabellen...")
    
    tables_to_check = ['projects', 'customers', 'load_profiles', 'load_values', 'simulation_results']
    
    for table_name in tables_to_check:
        try:
            # Versuche eine Abfrage auf die Tabelle
            response = supabase.table(table_name).select("id").limit(1).execute()
            print(f"✅ Tabelle '{table_name}' existiert bereits")
        except Exception as e:
            if "relation" in str(e).lower() and "does not exist" in str(e).lower():
                print(f"❌ Tabelle '{table_name}' existiert NICHT")
            else:
                print(f"⚠️ Tabelle '{table_name}' Status unklar: {e}")

def generate_sql_commands():
    """Generiert die SQL-Befehle für die manuelle Ausführung"""
    print("\n📋 SQL-Befehle für manuelle Ausführung im Supabase Dashboard:")
    print("=" * 60)
    
    sql_commands = [
        # Projects Table
        """
-- Projekte-Tabelle erstellen
CREATE TABLE IF NOT EXISTS projects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  location TEXT,
  date DATE,
  bess_size REAL,
  bess_power REAL,
  pv_power REAL,
  hp_power REAL,
  wind_power REAL,
  hydro_power REAL,
  other_power REAL,
  current_electricity_cost REAL DEFAULT 12.5,
  use_case_id INTEGER,
  simulation_year INTEGER DEFAULT 2024,
  created_at TIMESTAMP DEFAULT NOW()
);
        """,
        
        # Customers Table
        """
-- Kunden-Tabelle erstellen
CREATE TABLE IF NOT EXISTS customers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  company TEXT,
  contact TEXT,
  phone TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
        """,
        
        # Load Profiles Table
        """
-- Lastprofile-Tabelle erstellen
CREATE TABLE IF NOT EXISTS load_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  description TEXT,
  data_type TEXT,
  time_resolution INTEGER DEFAULT 15,
  created_at TIMESTAMP DEFAULT NOW()
);
        """,
        
        # Load Values Table
        """
-- Lastprofilwerte-Tabelle erstellen
CREATE TABLE IF NOT EXISTS load_values (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  load_profile_id UUID REFERENCES load_profiles(id) ON DELETE CASCADE,
  timestamp TIMESTAMP NOT NULL,
  power_kw REAL NOT NULL,
  energy_kwh REAL,
  created_at TIMESTAMP DEFAULT NOW()
);
        """,
        
        # Simulation Results Table
        """
-- Simulationsergebnisse-Tabelle erstellen
CREATE TABLE IF NOT EXISTS simulation_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
  timestamp TIMESTAMP DEFAULT NOW(),
  capacity_kwh REAL,
  state_of_charge REAL,
  simulation_data JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);
        """,
        
        # RLS Policies
        """
-- RLS für alle Tabellen aktivieren
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE load_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE load_values ENABLE ROW LEVEL SECURITY;
ALTER TABLE simulation_results ENABLE ROW LEVEL SECURITY;
        """,
        
        # Projects Policies
        """
-- Policies für projects
CREATE POLICY "Users can view their own projects"
ON projects FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own projects"
ON projects FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own projects"
ON projects FOR UPDATE
USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own projects"
ON projects FOR DELETE
USING (auth.uid() = user_id);
        """,
        
        # Customers Policies
        """
-- Policies für customers
CREATE POLICY "Users can view their own customers"
ON customers FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own customers"
ON customers FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own customers"
ON customers FOR UPDATE
USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own customers"
ON customers FOR DELETE
USING (auth.uid() = user_id);
        """,
        
        # Load Profiles Policies
        """
-- Policies für load_profiles
CREATE POLICY "Users can view their own load profiles"
ON load_profiles FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own load profiles"
ON load_profiles FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own load profiles"
ON load_profiles FOR UPDATE
USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own load profiles"
ON load_profiles FOR DELETE
USING (auth.uid() = user_id);
        """,
        
        # Load Values Policies
        """
-- Policies für load_values
CREATE POLICY "Users can access load values through load profiles"
ON load_values FOR ALL
USING (
  auth.uid() = (
    SELECT user_id FROM load_profiles WHERE load_profiles.id = load_values.load_profile_id
  )
);
        """,
        
        # Simulation Results Policies
        """
-- Policies für simulation_results
CREATE POLICY "Users can view their own simulation results"
ON simulation_results FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own simulation results"
ON simulation_results FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own simulation results"
ON simulation_results FOR UPDATE
USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own simulation results"
ON simulation_results FOR DELETE
USING (auth.uid() = user_id);
        """
    ]
    
    for i, command in enumerate(sql_commands, 1):
        print(f"\n--- Befehl {i} ---")
        print(command.strip())
        print("-" * 40)

def test_connection():
    """Testet die Verbindung und zeigt Benutzerinformationen"""
    print("\n🧪 Teste Verbindung...")
    
    try:
        # Versuche Benutzerinformationen abzurufen
        user = supabase.auth.get_user()
        if user.user:
            print(f"✅ Verbindung erfolgreich")
            print(f"📧 Benutzer: {user.user.email}")
            print(f"🆔 User ID: {user.user.id}")
        else:
            print("⚠️ Kein Benutzer angemeldet")
    except Exception as e:
        print(f"❌ Verbindungstest fehlgeschlagen: {e}")

if __name__ == "__main__":
    print("🚀 BESS-Simulation Multi-User Setup")
    print("=" * 40)
    
    test_connection()
    check_existing_tables()
    generate_sql_commands()
    
    print("\n📝 NÄCHSTE SCHRITTE:")
    print("1. Gehen Sie zu https://app.supabase.com")
    print("2. Wählen Sie Ihr Projekt aus")
    print("3. Gehen Sie zu 'SQL Editor'")
    print("4. Führen Sie die obigen SQL-Befehle nacheinander aus")
    print("5. Starten Sie dann die BESS-Simulation neu")
    
    print("\n✅ Setup-Anleitung abgeschlossen!")
