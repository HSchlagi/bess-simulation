#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migration-Script: Use Cases projektabhängig machen
Erstellt project_id Spalte und migriert bestehende Use Cases
"""

import sys
import os
from datetime import datetime

# Flask-App importieren
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app import create_app, db
from models import *

def migrate_use_cases_to_project_based():
    """Migriert Use Cases zu projektabhängigen Use Cases"""
    print("🔄 Migriere Use Cases zu projektabhängigen Use Cases...")
    
    try:
        # 1. Neue Spalte hinzufügen (falls nicht vorhanden)
        try:
            with db.engine.connect() as conn:
                conn.execute(db.text("ALTER TABLE use_case ADD COLUMN project_id INTEGER"))
                conn.commit()
            print("✅ project_id Spalte hinzugefügt")
        except Exception as e:
            print(f"ℹ️ project_id Spalte bereits vorhanden oder Fehler: {e}")
        
        # 2. Alle Projekte abrufen
        projects = Project.query.all()
        print(f"📊 {len(projects)} Projekte gefunden")
        
        # 3. Für jedes Projekt Standard-Use-Cases erstellen
        for project in projects:
            print(f"\n🏗️ Erstelle Use Cases für Projekt: {project.name} (ID: {project.id})")
            
            # Bestehende Use Cases für dieses Projekt löschen (falls vorhanden)
            try:
                existing_use_cases = UseCase.query.filter_by(project_id=project.id).all()
                for uc in existing_use_cases:
                    db.session.delete(uc)
            except:
                # Falls project_id noch nicht existiert, überspringen
                pass
            
            # Neue projektabhängige Use Cases erstellen
            use_cases = [
                {
                    'name': 'UC1',
                    'description': f'Verbrauch ohne Eigenerzeugung - {project.name}',
                    'scenario_type': 'consumption_only',
                    'pv_power_mwp': 0.0,
                    'hydro_power_kw': 0.0,
                    'hydro_energy_mwh_year': 0.0,
                    'wind_power_kw': 0.0,
                    'bess_size_mwh': project.bess_size / 1000 if project.bess_size else 0.0,  # kWh zu MWh
                    'bess_power_mw': project.bess_power / 1000 if project.bess_power else 0.0  # kW zu MW
                },
                {
                    'name': 'UC2',
                    'description': f'Verbrauch + PV ({project.pv_power or 0} kW) - {project.name}',
                    'scenario_type': 'pv_consumption',
                    'pv_power_mwp': (project.pv_power or 0) / 1000,  # kW zu MWp
                    'hydro_power_kw': 0.0,
                    'hydro_energy_mwh_year': 0.0,
                    'wind_power_kw': 0.0,
                    'bess_size_mwh': project.bess_size / 1000 if project.bess_size else 0.0,
                    'bess_power_mw': project.bess_power / 1000 if project.bess_power else 0.0
                },
                {
                    'name': 'UC3',
                    'description': f'Verbrauch + PV + Wasserkraft ({project.hydro_power or 0} kW) - {project.name}',
                    'scenario_type': 'pv_hydro_consumption',
                    'pv_power_mwp': (project.pv_power or 0) / 1000,
                    'hydro_power_kw': project.hydro_power or 0.0,
                    'hydro_energy_mwh_year': 2700.0,  # Standard-Wert
                    'wind_power_kw': 0.0,
                    'bess_size_mwh': project.bess_size / 1000 if project.bess_size else 0.0,
                    'bess_power_mw': project.bess_power / 1000 if project.bess_power else 0.0
                }
            ]
            
            for uc_data in use_cases:
                uc_data['project_id'] = project.id
                use_case = UseCase(**uc_data)
                db.session.add(use_case)
                print(f"  ✅ {uc_data['name']}: {uc_data['description']}")
        
        # 4. Alte globale Use Cases löschen (falls vorhanden)
        try:
            old_use_cases = UseCase.query.filter_by(project_id=None).all()
            for uc in old_use_cases:
                db.session.delete(uc)
                print(f"🗑️ Alten Use Case gelöscht: {uc.name}")
        except:
            pass
        
        # 5. Änderungen speichern
        db.session.commit()
        print("\n✅ Migration erfolgreich abgeschlossen!")
        
        # 6. Statistiken anzeigen
        total_use_cases = UseCase.query.count()
        print(f"📊 Insgesamt {total_use_cases} projektabhängige Use Cases erstellt")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Fehler bei der Migration: {e}")
        raise

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        migrate_use_cases_to_project_based()
