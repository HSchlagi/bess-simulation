#!/usr/bin/env python3
"""
Datenbank-Initialisierung für BESS Simulation
"""

import os
import sys
from datetime import datetime, timedelta

# Flask-App-Kontext importieren
from app import create_app, db
from models import *

def init_database():
    """Datenbank initialisieren und Demo-Daten erstellen"""
    app = create_app()
    
    with app.app_context():
        print("🗄️  Datenbank wird initialisiert...")
        
        # Alle Tabellen löschen und neu erstellen
        db.drop_all()
        db.create_all()
        
        print("✅ Tabellen erstellt")
        
        # Demo-Daten erstellen
        create_demo_data()
        
        print("✅ Demo-Daten erstellt")
        print("🎉 Datenbank-Initialisierung abgeschlossen!")

def create_demo_data():
    """Demo-Daten für alle Tabellen erstellen"""
    
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
    
    # Lastprofile erstellen
    load_profile1 = LoadProfile(
        project_id=project1.id,
        name="Standard-Lastprofil",
        description="Tägliches Lastprofil für Hinterstoder",
        data_type="load",
        time_resolution=15
    )
    load_profile2 = LoadProfile(
        project_id=project2.id,
        name="Gewerbe-Lastprofil",
        description="Gewerbliches Lastprofil für Wien",
        data_type="load",
        time_resolution=15
    )
    
    db.session.add_all([load_profile1, load_profile2])
    db.session.commit()
    
    # Investitionskosten erstellen
    costs = [
        InvestmentCost(
            project_id=project1.id,
            component_type="bess",
            cost_eur=150000.0,
            description="BESS-System 100kWh/100kW"
        ),
        InvestmentCost(
            project_id=project1.id,
            component_type="pv",
            cost_eur=80000.0,
            description="PV-Anlage 50kWp"
        ),
        InvestmentCost(
            project_id=project1.id,
            component_type="inverter",
            cost_eur=25000.0,
            description="Wechselrichter 100kW"
        ),
        InvestmentCost(
            project_id=project1.id,
            component_type="installation",
            cost_eur=30000.0,
            description="Installation und Montage"
        ),
        InvestmentCost(
            project_id=project2.id,
            component_type="bess",
            cost_eur=250000.0,
            description="BESS-System 200kWh/150kW"
        ),
        InvestmentCost(
            project_id=project2.id,
            component_type="pv",
            cost_eur=120000.0,
            description="PV-Anlage 100kWp"
        )
    ]
    
    db.session.add_all(costs)
    db.session.commit()
    
    # Referenzpreise erstellen
    prices = [
        ReferencePrice(
            name="Standard-Strompreis AT",
            price_type="electricity",
            price_eur_mwh=85.50,
            region="AT",
            valid_from=datetime(2025, 1, 1).date(),
            valid_to=datetime(2025, 12, 31).date()
        ),
        ReferencePrice(
            name="Standard-Gaspreis AT",
            price_type="gas",
            price_eur_mwh=65.20,
            region="AT",
            valid_from=datetime(2025, 1, 1).date(),
            valid_to=datetime(2025, 12, 31).date()
        ),
        ReferencePrice(
            name="Fernwärme-Preis Hinterstoder",
            price_type="heating",
            price_eur_mwh=45.80,
            region="AT-OÖ",
            valid_from=datetime(2025, 1, 1).date(),
            valid_to=datetime(2025, 12, 31).date()
        )
    ]
    
    db.session.add_all(prices)
    db.session.commit()
    
    # Spot-Preise erstellen (letzte 30 Tage)
    spot_prices = []
    for i in range(30):
        date = datetime.now() - timedelta(days=i)
        for hour in range(24):
            # Basis-Preis mit Tageszeit-Schwankungen
            base_price = 50 + 30 * (0.5 + 0.5 * (hour - 6) / 12)
            if hour >= 6 and hour <= 18:
                base_price += 20
            
            # Zufällige Schwankungen
            import random
            random_factor = 0.8 + 0.4 * random.random()
            price = base_price * random_factor
            
            spot_price = SpotPrice(
                timestamp=date.replace(hour=hour, minute=0, second=0, microsecond=0),
                price_eur_mwh=round(price, 2),
                source="EPEX",
                region="AT",
                price_type="day_ahead"
            )
            spot_prices.append(spot_price)
    
    db.session.add_all(spot_prices)
    db.session.commit()
    
    print(f"📊 Demo-Daten erstellt:")
    print(f"   - {Customer.query.count()} Kunden")
    print(f"   - {Project.query.count()} Projekte")
    print(f"   - {LoadProfile.query.count()} Lastprofile")
    print(f"   - {InvestmentCost.query.count()} Investitionskosten")
    print(f"   - {ReferencePrice.query.count()} Referenzpreise")
    print(f"   - {SpotPrice.query.count()} Spot-Preise")

if __name__ == "__main__":
    try:
        init_database()
    except Exception as e:
        print(f"❌ Fehler bei der Datenbank-Initialisierung: {e}")
        sys.exit(1) 