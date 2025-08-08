#!/usr/bin/env python3
"""
Überprüfung der Projekt-Kunden-Zuordnung
"""

import sqlite3
import os

def check_project_customers():
    """Überprüft die Projekt-Kunden-Zuordnung in der Datenbank"""
    
    db_path = 'instance/bess.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Datenbank nicht gefunden: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Überprüfung der Projekt-Kunden-Zuordnung...")
        print("=" * 60)
        
        # Alle Projekte mit Kunden laden
        cursor.execute("""
            SELECT p.id, p.name, p.location, p.customer_id, c.name as customer_name
            FROM project p 
            LEFT JOIN customer c ON p.customer_id = c.id
            ORDER BY p.name ASC
        """)
        
        projects = cursor.fetchall()
        
        if not projects:
            print("❌ Keine Projekte in der Datenbank gefunden!")
            return
        
        print(f"📊 Gefundene Projekte: {len(projects)}")
        print("-" * 60)
        
        for project in projects:
            project_id, project_name, location, customer_id, customer_name = project
            
            status = "✅" if customer_name else "❌"
            customer_info = customer_name if customer_name else "KEIN KUNDE ZUGEORDNET"
            
            print(f"{status} Projekt: {project_name}")
            print(f"   - ID: {project_id}")
            print(f"   - Standort: {location or 'Nicht angegeben'}")
            print(f"   - Kunden-ID: {customer_id or 'NULL'}")
            print(f"   - Kunde: {customer_info}")
            print()
        
        # Statistiken
        projects_with_customer = sum(1 for p in projects if p[4])
        projects_without_customer = len(projects) - projects_with_customer
        
        print("📈 Statistiken:")
        print(f"   - Projekte mit Kunde: {projects_with_customer}")
        print(f"   - Projekte ohne Kunde: {projects_without_customer}")
        print(f"   - Gesamt: {len(projects)}")
        
        if projects_without_customer > 0:
            print("\n⚠️  Projekte ohne Kunden-Zuordnung:")
            for project in projects:
                if not project[4]:  # Kein Kundenname
                    print(f"   - {project[1]} (ID: {project[0]})")
        
        # Alle verfügbaren Kunden anzeigen
        cursor.execute("SELECT id, name FROM customer ORDER BY name ASC")
        customers = cursor.fetchall()
        
        print(f"\n👥 Verfügbare Kunden ({len(customers)}):")
        for customer_id, customer_name in customers:
            print(f"   - {customer_name} (ID: {customer_id})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Fehler bei der Datenbanküberprüfung: {e}")

if __name__ == "__main__":
    check_project_customers()
