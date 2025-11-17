#!/usr/bin/env python3
"""
Prueft alle Use Cases in der Datenbank
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import Project, UseCase

def check_all_use_cases():
    """Prueft alle Use Cases in der Datenbank"""
    
    app = create_app()
    with app.app_context():
        # Alle Use Cases laden
        all_use_cases = UseCase.query.all()
        
        print(f"Gesamt Use Cases in Datenbank: {len(all_use_cases)}")
        print()
        
        # Nach Projekt gruppieren
        by_project = {}
        for uc in all_use_cases:
            project_id = uc.project_id if uc.project_id else 'None'
            if project_id not in by_project:
                by_project[project_id] = []
            by_project[project_id].append(uc)
        
        for project_id, use_cases in by_project.items():
            if project_id == 'None':
                print(f"Use Cases ohne Projekt (project_id=None): {len(use_cases)}")
            else:
                project = Project.query.get(project_id)
                project_name = project.name if project else f"Unbekannt (ID: {project_id})"
                print(f"Projekt: {project_name} (ID: {project_id}): {len(use_cases)} Use Cases")
            
            for uc in use_cases:
                print(f"  - {uc.name} (ID: {uc.id})")
            print()
        
        # Pruefe speziell nach UC1, UC2, UC3
        print("Use Cases mit Namen UC1, UC2, UC3:")
        standard_names = ['UC1', 'UC2', 'UC3']
        for name in standard_names:
            use_cases = UseCase.query.filter_by(name=name).all()
            if use_cases:
                print(f"  {name}: {len(use_cases)} gefunden")
                for uc in use_cases:
                    project = Project.query.get(uc.project_id) if uc.project_id else None
                    project_name = project.name if project else "Kein Projekt"
                    print(f"    - ID: {uc.id}, Projekt: {project_name} (ID: {uc.project_id})")

if __name__ == '__main__':
    check_all_use_cases()

