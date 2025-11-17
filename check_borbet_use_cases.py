#!/usr/bin/env python3
"""
Prüft, welche Use Cases für BORBET existieren und entfernt Standard-Use Cases (UC1, UC2, UC3)
wenn projektspezifische Use Cases vorhanden sind.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import Project, UseCase

def check_and_clean_borbet_use_cases():
    """Prüft und bereinigt Use Cases für BORBET"""
    
    app = create_app()
    with app.app_context():
        # BORBET-Projekt finden
        borbet = Project.query.filter(Project.name.ilike('%BORBET%')).first()
        
        if not borbet:
            print("BORBET-Projekt nicht gefunden!")
            return
        
        print(f"Projekt gefunden: {borbet.name} (ID: {borbet.id})")
        print()
        
        # Alle Use Cases für BORBET laden
        all_use_cases = UseCase.query.filter_by(project_id=borbet.id).all()
        
        print(f"Gefundene Use Cases für BORBET: {len(all_use_cases)}")
        print()
        
        for uc in all_use_cases:
            print(f"  - {uc.name} (ID: {uc.id})")
            print(f"    Beschreibung: {uc.description}")
            print(f"    Szenario: {uc.scenario_type}")
            print()
        
        # Standard-Use Cases identifizieren (UC1, UC2, UC3 ohne Projekt-Präfix)
        standard_use_cases = [uc for uc in all_use_cases if uc.name in ['UC1', 'UC2', 'UC3']]
        project_specific_use_cases = [uc for uc in all_use_cases if uc.name not in ['UC1', 'UC2', 'UC3']]
        
        print(f"Standard-Use Cases (UC1, UC2, UC3): {len(standard_use_cases)}")
        print(f"Projektspezifische Use Cases: {len(project_specific_use_cases)}")
        print()
        
        # Wenn projektspezifische Use Cases vorhanden sind, Standard-Use Cases löschen
        if project_specific_use_cases and standard_use_cases:
            print("⚠️ WARNUNG: Es gibt sowohl Standard-Use Cases als auch projektspezifische Use Cases!")
            print("   Lösche Standard-Use Cases (UC1, UC2, UC3)...")
            print()
            
            for uc in standard_use_cases:
                print(f"   Lösche: {uc.name} (ID: {uc.id})")
                UseCase.query.filter_by(id=uc.id).delete()
            
            from app import db
            db.session.commit()
            print()
            print("✅ Standard-Use Cases gelöscht!")
            print()
            print("Verbleibende Use Cases für BORBET:")
            remaining = UseCase.query.filter_by(project_id=borbet.id).all()
            for uc in remaining:
                print(f"  - {uc.name} (ID: {uc.id})")
        elif standard_use_cases and not project_specific_use_cases:
            print("ℹ️ Nur Standard-Use Cases vorhanden. Diese werden verwendet.")
        elif project_specific_use_cases and not standard_use_cases:
            print("✅ Nur projektspezifische Use Cases vorhanden. Alles in Ordnung!")
        else:
            print("⚠️ Keine Use Cases für BORBET gefunden!")

if __name__ == '__main__':
    check_and_clean_borbet_use_cases()

