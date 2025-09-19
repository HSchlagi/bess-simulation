#!/usr/bin/env python3
"""
Migration für BESS-Projekt-Zuordnung
Erstellt die neuen Tabellen für Live BESS Integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from models import BESSProjectMapping, BESSTelemetryData

def migrate_bess_mapping():
    """Erstellt die BESS-Projekt-Zuordnung Tabellen"""
    
    app = create_app()
    
    with app.app_context():
        try:
            print("🚀 Starte BESS-Projekt-Zuordnung Migration...")
            
            # Erstelle alle neuen Tabellen
            print("📊 Erstelle BESSProjectMapping Tabelle...")
            db.create_all()
            
            # Prüfe ob Tabellen erstellt wurden
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'bess_project_mapping' in tables:
                print("✅ BESSProjectMapping Tabelle erfolgreich erstellt")
            else:
                print("❌ Fehler: BESSProjectMapping Tabelle nicht gefunden")
                
            if 'bess_telemetry_data' in tables:
                print("✅ BESSTelemetryData Tabelle erfolgreich erstellt")
            else:
                print("❌ Fehler: BESSTelemetryData Tabelle nicht gefunden")
            
            # Prüfe Indizes
            mapping_indexes = inspector.get_indexes('bess_project_mapping')
            telemetry_indexes = inspector.get_indexes('bess_telemetry_data')
            
            print(f"📈 BESSProjectMapping Indizes: {len(mapping_indexes)}")
            print(f"📈 BESSTelemetryData Indizes: {len(telemetry_indexes)}")
            
            # Erstelle Demo-Daten (optional)
            create_demo_mappings()
            
            print("🎉 Migration erfolgreich abgeschlossen!")
            
        except Exception as e:
            print(f"❌ Fehler bei Migration: {e}")
            db.session.rollback()
            raise

def create_demo_mappings():
    """Erstellt Demo-BESS-Zuordnungen für vorhandene Projekte"""
    
    try:
        from models import Project
        
        # Hole alle Projekte
        projects = Project.query.limit(3).all()
        
        if not projects:
            print("⚠️ Keine Projekte gefunden - Demo-Daten übersprungen")
            return
        
        print(f"📝 Erstelle Demo-Zuordnungen für {len(projects)} Projekte...")
        
        demo_mappings = [
            {
                'site': 'demo_site_1',
                'device': 'bess_001',
                'bess_name': 'Demo BESS System 1',
                'description': 'Demo BESS-System für Testzwecke',
                'location': 'Demo Standort 1',
                'manufacturer': 'Demo Hersteller',
                'model': 'Demo Model 100',
                'rated_power_kw': 100.0,
                'rated_energy_kwh': 200.0
            },
            {
                'site': 'demo_site_2',
                'device': 'bess_002',
                'bess_name': 'Demo BESS System 2',
                'description': 'Demo BESS-System für Testzwecke',
                'location': 'Demo Standort 2',
                'manufacturer': 'Demo Hersteller',
                'model': 'Demo Model 200',
                'rated_power_kw': 250.0,
                'rated_energy_kwh': 500.0
            }
        ]
        
        created_count = 0
        
        for i, project in enumerate(projects):
            if i < len(demo_mappings):
                mapping_data = demo_mappings[i]
                
                # Prüfe ob Mapping bereits existiert
                existing = BESSProjectMapping.query.filter_by(
                    site=mapping_data['site'],
                    device=mapping_data['device']
                ).first()
                
                if not existing:
                    mapping = BESSProjectMapping(
                        project_id=project.id,
                        **mapping_data
                    )
                    
                    db.session.add(mapping)
                    created_count += 1
                    
                    print(f"✅ Demo-Mapping erstellt: {project.name} -> {mapping_data['bess_name']}")
        
        if created_count > 0:
            db.session.commit()
            print(f"🎉 {created_count} Demo-Mappings erfolgreich erstellt")
        else:
            print("ℹ️ Alle Demo-Mappings bereits vorhanden")
            
    except Exception as e:
        print(f"⚠️ Fehler beim Erstellen der Demo-Daten: {e}")
        db.session.rollback()

def verify_migration():
    """Überprüft die Migration"""
    
    app = create_app()
    
    with app.app_context():
        try:
            print("\n🔍 Überprüfe Migration...")
            
            # Prüfe Tabellen
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            required_tables = ['bess_project_mapping', 'bess_telemetry_data']
            
            for table in required_tables:
                if table in tables:
                    from sqlalchemy import text
                    count = db.session.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                    print(f"✅ {table}: {count} Datensätze")
                else:
                    print(f"❌ {table}: Tabelle nicht gefunden")
            
            # Prüfe Beziehungen
            mappings = BESSProjectMapping.query.count()
            print(f"📊 BESS-Mappings: {mappings}")
            
            # Prüfe Demo-Daten
            demo_mappings = BESSProjectMapping.query.filter(
                BESSProjectMapping.site.like('demo_%')
            ).count()
            print(f"🎭 Demo-Mappings: {demo_mappings}")
            
            print("✅ Migration-Verifikation abgeschlossen")
            
        except Exception as e:
            print(f"❌ Fehler bei Verifikation: {e}")

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 BESS-Projekt-Zuordnung Migration")
    print("=" * 60)
    
    migrate_bess_mapping()
    verify_migration()
    
    print("\n" + "=" * 60)
    print("🎉 Migration abgeschlossen!")
    print("=" * 60)
