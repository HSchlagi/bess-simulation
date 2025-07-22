#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Project

app = create_app()

with app.app_context():
    project = Project.query.get(1)
    if project:
        print("=== WIEDERHERSTELLUNG DER PROJEKTWERTE ===")
        
        # Korrekte Werte setzen
        project.bess_size = 5000.0
        project.bess_power = 5000.0
        project.pv_power = 1480.0  # Das war das Problem!
        project.hp_power = 0.0
        project.wind_power = 0.0
        project.hydro_power = 540.0
        
        # Investitionskosten
        project.bess_investment = 1050000.0
        project.pv_investment = 30000.0  # Das war weg!
        project.wind_investment = 50000.0
        project.hydro_investment = 25000.0
        project.hp_investment = 15000.0
        project.other_investment = 16.5
        
        # Betriebskosten
        project.bess_operation_cost = 13125.0
        project.pv_operation_cost = 300.0
        project.wind_operation_cost = 1000.0
        project.hydro_operation_cost = 375.0
        project.hp_operation_cost = 150.0
        project.other_operation_cost = 0.0
        
        db.session.commit()
        
        print("✅ Projektwerte erfolgreich wiederhergestellt!")
        print(f"BESS Size: {project.bess_size}")
        print(f"BESS Power: {project.bess_power}")
        print(f"PV Power: {project.pv_power}")
        print(f"PV Investment: {project.pv_investment}")
        print(f"Other Investment: {project.other_investment}")
    else:
        print("❌ Projekt nicht gefunden!") 