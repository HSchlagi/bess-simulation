#!/usr/bin/env python3
"""
Datenbankinitialisierung für BESS Simulation
"""

from app import create_app, db
from models import (
    Customer, Project, 
    LoadProfile, LoadValue,
    WeatherData, WeatherValue,
    SolarData, SolarValue,
    HydroData, HydroValue,
    WindData, WindValue,
    PVSolData, PVSolValue,
    Simulation, SimulationResult
)

def init_database():
    """Initialisiert die Datenbank mit allen Tabellen"""
    app = create_app()
    
    with app.app_context():
        print("Erstelle Datenbanktabellen...")
        
        # Alle Tabellen erstellen
        db.create_all()
        
        print("✅ Datenbank erfolgreich initialisiert!")
        print(f"📁 Datenbankdatei: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # Tabellen auflisten
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"📊 Erstellte Tabellen: {len(tables)}")
        for table in tables:
            print(f"   - {table}")

if __name__ == '__main__':
    init_database() 