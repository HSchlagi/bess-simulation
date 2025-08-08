#!/usr/bin/env python3
"""
Repariert die Datenbankstruktur nach der Wiederherstellung
"""

import sqlite3
import os

def fix_database_structure():
    """Repariert die Datenbankstruktur"""
    
    try:
        conn = sqlite3.connect('instance/bess.db')
        cursor = conn.cursor()
        
        print("🔧 Repariere Datenbankstruktur...")
        
        # Prüfe und füge fehlende Spalten hinzu
        cursor.execute("PRAGMA table_info(project)")
        columns = [col[1] for col in cursor.fetchall()]
        
        print(f"Bestehende Spalten in project: {columns}")
        
        # Füge current_electricity_cost hinzu, falls fehlend
        if 'current_electricity_cost' not in columns:
            print("➕ Füge current_electricity_cost Spalte hinzu...")
            cursor.execute("""
                ALTER TABLE project 
                ADD COLUMN current_electricity_cost REAL DEFAULT 12.5
            """)
            print("✅ current_electricity_cost Spalte hinzugefügt")
        
        # Füge other_power hinzu, falls fehlend
        if 'other_power' not in columns:
            print("➕ Füge other_power Spalte hinzu...")
            cursor.execute("""
                ALTER TABLE project 
                ADD COLUMN other_power REAL
            """)
            print("✅ other_power Spalte hinzugefügt")
        
        # Füge use_case_id hinzu, falls fehlend
        if 'use_case_id' not in columns:
            print("➕ Füge use_case_id Spalte hinzu...")
            cursor.execute("""
                ALTER TABLE project 
                ADD COLUMN use_case_id INTEGER
            """)
            print("✅ use_case_id Spalte hinzugefügt")
        
        # Füge simulation_year hinzu, falls fehlend
        if 'simulation_year' not in columns:
            print("➕ Füge simulation_year Spalte hinzu...")
            cursor.execute("""
                ALTER TABLE project 
                ADD COLUMN simulation_year INTEGER DEFAULT 2024
            """)
            print("✅ simulation_year Spalte hinzugefügt")
        
        # Füge created_at hinzu, falls fehlend
        if 'created_at' not in columns:
            print("➕ Füge created_at Spalte hinzu...")
            cursor.execute("""
                ALTER TABLE project 
                ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            """)
            print("✅ created_at Spalte hinzugefügt")
        
        # Prüfe customer Tabelle
        cursor.execute("PRAGMA table_info(customer)")
        customer_columns = [col[1] for col in cursor.fetchall()]
        print(f"Bestehende Spalten in customer: {customer_columns}")
        
        # Füge company Spalte hinzu, falls fehlend
        if 'company' not in customer_columns:
            print("➕ Füge company Spalte zu customer hinzu...")
            cursor.execute("""
                ALTER TABLE customer 
                ADD COLUMN company TEXT
            """)
            print("✅ company Spalte hinzugefügt")
        
        # Prüfe investment_cost Tabelle
        cursor.execute("PRAGMA table_info(investment_cost)")
        cost_columns = [col[1] for col in cursor.fetchall()]
        print(f"Bestehende Spalten in investment_cost: {cost_columns}")
        
        # Füge description Spalte hinzu, falls fehlend
        if 'description' not in cost_columns:
            print("➕ Füge description Spalte zu investment_cost hinzu...")
            cursor.execute("""
                ALTER TABLE investment_cost 
                ADD COLUMN description TEXT
            """)
            print("✅ description Spalte hinzugefügt")
        
        # Füge created_at Spalte hinzu, falls fehlend
        if 'created_at' not in cost_columns:
            print("➕ Füge created_at Spalte zu investment_cost hinzu...")
            cursor.execute("""
                ALTER TABLE investment_cost 
                ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            """)
            print("✅ created_at Spalte hinzugefügt")
        
        conn.commit()
        print("✅ Datenbankstruktur erfolgreich repariert!")
        
        # Überprüfung
        cursor.execute("SELECT * FROM customer")
        customers = cursor.fetchall()
        print(f"\n📋 Kunden ({len(customers)}):")
        for customer in customers:
            print(f"   - {customer[1]} ({customer[2]})")
        
        cursor.execute("SELECT * FROM project")
        projects = cursor.fetchall()
        print(f"\n📋 Projekte ({len(projects)}):")
        for project in projects:
            print(f"   - {project[1]} (Kunde-ID: {project[12]})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Fehler bei der Reparatur: {e}")

if __name__ == "__main__":
    fix_database_structure() 