#!/usr/bin/env python3
"""
Skript zum Beheben fehlender created_at Werte in der Datenbank
"""

from app import create_app, db
from models import Project, Customer
from datetime import datetime

def fix_created_at_dates():
    """Setzt fehlende created_at Werte für Projekte und Kunden"""
    app = create_app()
    
    with app.app_context():
        print("🔧 Behebe fehlende created_at Werte...")
        
        # Projekte ohne created_at
        projects_without_date = Project.query.filter_by(created_at=None).all()
        print(f"📊 {len(projects_without_date)} Projekte ohne created_at gefunden")
        
        for project in projects_without_date:
            project.created_at = datetime.utcnow()
            print(f"  ✅ Projekt '{project.name}' - created_at gesetzt")
        
        # Kunden ohne created_at
        customers_without_date = Customer.query.filter_by(created_at=None).all()
        print(f"📊 {len(customers_without_date)} Kunden ohne created_at gefunden")
        
        for customer in customers_without_date:
            customer.created_at = datetime.utcnow()
            print(f"  ✅ Kunde '{customer.name}' - created_at gesetzt")
        
        # Änderungen speichern
        if projects_without_date or customers_without_date:
            db.session.commit()
            print("✅ Alle fehlenden created_at Werte wurden gesetzt!")
        else:
            print("ℹ️ Alle Datensätze haben bereits created_at Werte")
        
        # Statistiken anzeigen
        total_projects = Project.query.count()
        total_customers = Customer.query.count()
        projects_with_date = Project.query.filter(Project.created_at.isnot(None)).count()
        customers_with_date = Customer.query.filter(Customer.created_at.isnot(None)).count()
        
        print(f"\n📈 Statistiken:")
        print(f"   Projekte: {projects_with_date}/{total_projects} mit created_at")
        print(f"   Kunden: {customers_with_date}/{total_customers} mit created_at")

if __name__ == "__main__":
    fix_created_at_dates()
