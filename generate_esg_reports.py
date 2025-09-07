#!/usr/bin/env python3
"""
ESG-Reports für alle Projekte generieren
Erstellt ESG-Reports für das CO₂-Tracking System
"""

import sqlite3
import sys
import os
from datetime import datetime, timedelta
import json

# CO₂-Tracking System importieren
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from co2_tracking_system import CO2TrackingSystem

def generate_esg_reports_for_all_projects():
    """Generiert ESG-Reports für alle Projekte"""
    
    print("🌱 Generiere ESG-Reports für alle Projekte")
    print("=" * 50)
    
    # Datenbankverbindung
    conn = sqlite3.connect('instance/bess.db')
    cursor = conn.cursor()
    
    # Alle Projekte abrufen
    cursor.execute('SELECT id, name FROM project')
    projects = cursor.fetchall()
    
    print(f"📋 Gefundene Projekte: {len(projects)}")
    
    # CO₂-Tracking System initialisieren
    co2_system = CO2TrackingSystem()
    
    for project_id, name in projects:
        print(f"🔧 Generiere ESG-Report für: {name} (ID: {project_id})")
        
        # Bestehende ESG-Reports löschen
        cursor.execute('DELETE FROM esg_reports WHERE project_id = ?', (project_id,))
        
        # ESG-Report generieren
        try:
            esg_report = co2_system.generate_esg_report(project_id, 'monthly')
            print(f"✅ {name}: ESG-Report generiert - Score: {esg_report['overall_esg_score']}")
        except Exception as e:
            print(f"❌ {name}: Fehler beim Generieren des ESG-Reports: {e}")
    
    conn.commit()
    conn.close()
    
    print("\n🎯 ESG-Reports erfolgreich generiert!")
    print("📊 Alle Projekte haben jetzt ESG-Reports mit Scores")
    print("🔄 Bitte das CO₂-Dashboard neu laden!")

if __name__ == '__main__':
    generate_esg_reports_for_all_projects()
