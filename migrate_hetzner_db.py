#!/usr/bin/env python3
"""
Migration-Script für Hetzner-Datenbank
Aktualisiert das Schema ohne Datenverlust
"""

import os
import sys
from datetime import datetime

# Flask-App-Kontext importieren
from app import create_app, db
from models import *

def migrate_hetzner_database():
    """Datenbank-Schema auf Hetzner migrieren"""
    app = create_app()
    
    with app.app_context():
        print("🔄 Starte Datenbank-Migration für Hetzner...")
        
        try:
            # Neue Tabellen erstellen (falls nicht vorhanden)
            db.create_all()
            print("✅ Schema-Migration abgeschlossen")
            
            # Demo-Daten nur hinzufügen, falls Tabellen leer sind
            add_demo_data_if_empty()
            
            print("🎉 Hetzner-Datenbank erfolgreich migriert!")
            
        except Exception as e:
            print(f"❌ Fehler bei Migration: {e}")
            return False
    
    return True

def add_demo_data_if_empty():
    """Demo-Daten hinzufügen, falls Tabellen leer sind"""
    
    # Prüfen ob Kunden existieren
    customer_count = Customer.query.count()
    if customer_count == 0:
        print("📊 Füge Demo-Daten hinzu...")
        
        # Kunden erstellen
        customer1 = Customer(
            name="Max Mustermann",
            company="Energie GmbH",
            contact="max@energie-gmbh.at"
        )
        customer2 = Customer(
            name="Anna Schmidt",
            company="Solar Solutions",
            contact="anna@solar-solutions.at"
        )
        
        db.session.add_all([customer1, customer2])
        db.session.commit()
        
        # Projekte erstellen
        project1 = Project(
            name="BESS Hinterstoder",
            location="Hinterstoder, Österreich",
            date=datetime.now().date(),
            bess_size=100.0,  # kWh
            bess_power=100.0,  # kW
            pv_power=50.0,  # kW
            customer_id=customer1.id
        )
        project2 = Project(
            name="Solar-BESS Wien",
            location="Wien, Österreich",
            date=datetime.now().date(),
            bess_size=200.0,  # kWh
            bess_power=150.0,  # kW
            pv_power=100.0,  # kW
            customer_id=customer2.id
        )
        
        db.session.add_all([project1, project2])
        db.session.commit()
        
        print("✅ Demo-Daten hinzugefügt")
    else:
        print(f"ℹ️  {customer_count} Kunden bereits vorhanden - Demo-Daten übersprungen")

if __name__ == "__main__":
    success = migrate_hetzner_database()
    if success:
        print("🚀 Migration erfolgreich - Server kann gestartet werden")
    else:
        print("❌ Migration fehlgeschlagen - Bitte Logs prüfen") 