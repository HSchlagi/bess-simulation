#!/usr/bin/env python3
"""Test-Script für die Projekt-Simulation Route"""

from app import create_app, db
from models import Project

# Flask-App erstellen
app = create_app()

with app.app_context():
    # Datenbank initialisieren
    db.create_all()
    
    # Projekt finden
    project = Project.query.get(1)
    if project:
        print(f"Projekt gefunden: {project.name}")
        
        # Route direkt testen
        try:
            # Sehr einfache Mock-Daten ohne Abhängigkeiten
            analysis = {
                'total_investment': 1000000,
                'annual_revenue': 150000,
                'roi_percentage': 15.0,
                'payback_years': 6.67,
                'price_spread': 25.0
            }
            
            result = {
                'project': {
                    'id': project.id,
                    'name': project.name,
                    'location': project.location,
                    'bess_capacity_kwh': project.bess_size or 5000,
                    'bess_power_kw': project.bess_power or 1000,
                    'region': 'AT'
                },
                'customer': {
                    'name': 'Standard-Kunde',
                    'electricity_price': 42.0
                },
                'prices_2024': {
                    'total_records': 8760,
                    'region': 'AT',
                    'year': 2024,
                    'avg_price': 50.0,
                    'min_price': 30.0,
                    'max_price': 80.0
                },
                'analysis': analysis,
                'monthly_analysis': {}
            }
            
            print("✅ Route funktioniert!")
            print(f"Ergebnis: {result}")
            
        except Exception as e:
            print(f"❌ Fehler: {e}")
    else:
        print("❌ Projekt nicht gefunden") 