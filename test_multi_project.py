#!/usr/bin/env python3
"""
Test für Multi-Projekt BESS-Funktionalität
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.live_data_service import live_bess_service
from models import BESSProjectMapping, Project

def test_multi_project_functionality():
    """Testet die Multi-Projekt BESS-Funktionalität"""
    
    app = create_app()
    
    with app.app_context():
        try:
            print("🚀 Teste Multi-Projekt BESS-Funktionalität...")
            
            # 1. Teste Live Service
            print("\n📊 1. Live Service Test:")
            mappings = live_bess_service.get_project_mappings()
            print(f"   ✅ Projekt-Mappings abgerufen: {len(mappings)}")
            
            for mapping in mappings:
                print(f"   - {mapping['project_name']}: {mapping['display_name']} ({mapping['site']}/{mapping['device']})")
            
            # 2. Teste Projekt-spezifische Daten
            print("\n📊 2. Projekt-spezifische Daten:")
            projects = Project.query.all()
            print(f"   Verfügbare Projekte: {len(projects)}")
            
            for project in projects[:2]:  # Teste erste 2 Projekte
                print(f"\n   📋 Projekt: {project.name} (ID: {project.id})")
                
                # Projekt-Mappings
                project_mappings = live_bess_service.get_project_mappings(project.id)
                print(f"      Mappings: {len(project_mappings)}")
                
                # Projekt-Device-Summary
                device_summary = live_bess_service.get_project_device_summary(project.id)
                print(f"      Geräte: {device_summary.get('device_count', 0)}")
                print(f"      Standorte: {device_summary.get('site_count', 0)}")
                print(f"      Gesamtleistung: {device_summary.get('total_power_kw', 0)} kW")
                
                # Projekt-Live-Daten
                live_data = live_bess_service.get_project_live_data(project.id, limit=5)
                print(f"      Live-Daten: {len(live_data)} Datensätze")
            
            # 3. Teste Admin-Funktionalität
            print("\n📊 3. Admin-Funktionalität:")
            all_mappings = live_bess_service.get_project_mappings()
            
            active_count = sum(1 for m in all_mappings if m['is_active'])
            auto_sync_count = sum(1 for m in all_mappings if m['auto_sync'])
            
            print(f"   Gesamt-Mappings: {len(all_mappings)}")
            print(f"   Aktive Mappings: {active_count}")
            print(f"   Auto-Sync Mappings: {auto_sync_count}")
            
            # 4. Teste MQTT-Topic-Generierung
            print("\n📊 4. MQTT-Topic-Generierung:")
            for mapping in mappings[:2]:
                topic = mapping['mqtt_topic']
                print(f"   {mapping['display_name']}: {topic}")
            
            # 5. Teste Datenbank-Beziehungen
            print("\n📊 5. Datenbank-Beziehungen:")
            for mapping_obj in BESSProjectMapping.query.all()[:2]:
                print(f"   {mapping_obj.project.name} -> {mapping_obj.display_name}")
                print(f"      Telemetrie-Daten: {len(mapping_obj.telemetry_data)}")
                print(f"      Letzte Sync: {mapping_obj.last_sync}")
            
            print("\n🎉 Alle Tests erfolgreich!")
            return True
            
        except Exception as e:
            print(f"❌ Fehler beim Testen: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    print("=" * 60)
    print("🧪 Multi-Projekt BESS-Funktionalität Test")
    print("=" * 60)
    
    success = test_multi_project_functionality()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Alle Tests bestanden!")
    else:
        print("❌ Tests fehlgeschlagen!")
    print("=" * 60)
