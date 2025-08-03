#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migration-Script für BESS-Simulation Erweiterung
Erstellt neue Tabellen und Standard-Use-Cases
"""

import sys
import os
from datetime import datetime, date
from sqlalchemy import create_engine, text

# Flask-App importieren
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app import create_app, db
from models import *

def create_standard_use_cases():
    """Erstellt die Standard-Use-Cases für Hinterstoder"""
    print("Erstelle Standard-Use-Cases...")
    
    use_cases = [
        {
            'name': 'UC1',
            'description': 'Verbrauch ohne Eigenerzeugung',
            'scenario_type': 'consumption_only',
            'pv_power_mwp': 0.0,
            'hydro_power_kw': 0.0,
            'hydro_energy_mwh_year': 0.0
        },
        {
            'name': 'UC2', 
            'description': 'Verbrauch + PV (1,95 MWp)',
            'scenario_type': 'pv_consumption',
            'pv_power_mwp': 1.95,
            'hydro_power_kw': 0.0,
            'hydro_energy_mwh_year': 0.0
        },
        {
            'name': 'UC3',
            'description': 'Verbrauch + PV + Wasserkraft (650 kW, 2700 MWh/a)',
            'scenario_type': 'pv_hydro_consumption', 
            'pv_power_mwp': 1.95,
            'hydro_power_kw': 650.0,
            'hydro_energy_mwh_year': 2700.0
        }
    ]
    
    for uc_data in use_cases:
        # Prüfen ob Use Case bereits existiert
        existing = UseCase.query.filter_by(name=uc_data['name']).first()
        if not existing:
            use_case = UseCase(**uc_data)
            db.session.add(use_case)
            print(f"  - {uc_data['name']}: {uc_data['description']}")
        else:
            print(f"  - {uc_data['name']}: Bereits vorhanden")
    
    db.session.commit()

def create_standard_revenue_models():
    """Erstellt Standard-Erlösmodelle"""
    print("Erstelle Standard-Erlösmodelle...")
    
    revenue_models = [
        {
            'name': 'Arbitrage Spotmarkt',
            'revenue_type': 'arbitrage',
            'price_eur_mwh': 0.0,  # Wird dynamisch berechnet
            'availability_hours': 8760,
            'efficiency_factor': 0.85,
            'description': 'Erlöse durch Lade-/Entladeoptimierung basierend auf Spotpreisen'
        },
        {
            'name': 'SRL+ (Positive Sekundärregelenergie)',
            'revenue_type': 'srl_positive', 
            'price_eur_mwh': 45.0,
            'availability_hours': 8760,
            'efficiency_factor': 0.95,
            'description': 'Erlöse durch Bereitstellung positiver Sekundärregelenergie'
        },
        {
            'name': 'SRL- (Negative Sekundärregelenergie)',
            'revenue_type': 'srl_negative',
            'price_eur_mwh': 35.0,
            'availability_hours': 8760,
            'efficiency_factor': 0.95,
            'description': 'Erlöse durch Bereitstellung negativer Sekundärregelenergie'
        },
        {
            'name': 'Day-Ahead Handel',
            'revenue_type': 'day_ahead',
            'price_eur_mwh': 0.0,  # Wird dynamisch berechnet
            'availability_hours': 8760,
            'efficiency_factor': 0.90,
            'description': 'Erlöse durch Day-Ahead Markthandel'
        },
        {
            'name': 'Intraday Handel',
            'revenue_type': 'intraday',
            'price_eur_mwh': 0.0,  # Wird dynamisch berechnet
            'availability_hours': 8760,
            'efficiency_factor': 0.88,
            'description': 'Erlöse durch Intraday Markthandel'
        }
    ]
    
    for rm_data in revenue_models:
        existing = RevenueModel.query.filter_by(name=rm_data['name']).first()
        if not existing:
            revenue_model = RevenueModel(**rm_data)
            db.session.add(revenue_model)
            print(f"  - {rm_data['name']}")
        else:
            print(f"  - {rm_data['name']}: Bereits vorhanden")
    
    db.session.commit()

def create_standard_grid_tariffs():
    """Erstellt Standard-Netzentgelte für Österreich"""
    print("Erstelle Standard-Netzentgelte...")
    
    grid_tariffs = [
        {
            'name': 'AT Bezug Standard',
            'tariff_type': 'consumption',
            'base_price_eur_mwh': 25.0,
            'spot_multiplier': 1.2,
            'region': 'AT',
            'valid_from': date(2024, 1, 1),
            'valid_to': date(2025, 12, 31)
        },
        {
            'name': 'AT Einspeisung Standard',
            'tariff_type': 'feed_in',
            'base_price_eur_mwh': 15.0,
            'spot_multiplier': 0.8,
            'region': 'AT',
            'valid_from': date(2024, 1, 1),
            'valid_to': date(2025, 12, 31)
        }
    ]
    
    for gt_data in grid_tariffs:
        existing = GridTariff.query.filter_by(name=gt_data['name']).first()
        if not existing:
            grid_tariff = GridTariff(**gt_data)
            db.session.add(grid_tariff)
            print(f"  - {gt_data['name']}")
        else:
            print(f"  - {gt_data['name']}: Bereits vorhanden")
    
    db.session.commit()

def create_standard_legal_charges():
    """Erstellt Standard-Gesetzesabgaben"""
    print("Erstelle Standard-Gesetzesabgaben...")
    
    legal_charges = [
        {
            'name': 'Stromabgabe 2024',
            'charge_type': 'electricity_tax',
            'amount_eur_mwh': 1.0,
            'region': 'AT',
            'valid_from': date(2024, 1, 1),
            'valid_to': date(2024, 12, 31),
            'description': 'Stromabgabe in Österreich 2024'
        },
        {
            'name': 'Stromabgabe 2025+',
            'charge_type': 'electricity_tax',
            'amount_eur_mwh': 15.0,
            'region': 'AT',
            'valid_from': date(2025, 1, 1),
            'valid_to': date(2030, 12, 31),
            'description': 'Stromabgabe in Österreich ab 2025'
        },
        {
            'name': 'Netzverlustentgelt AT',
            'charge_type': 'network_loss',
            'amount_eur_mwh': 8.5,
            'region': 'AT',
            'valid_from': date(2024, 1, 1),
            'valid_to': date(2025, 12, 31),
            'description': 'Netzverlustentgelt Österreich'
        },
        {
            'name': 'Clearinggebühr EPEX',
            'charge_type': 'clearing_fee',
            'amount_eur_mwh': 0.15,
            'region': 'AT',
            'valid_from': date(2024, 1, 1),
            'valid_to': date(2025, 12, 31),
            'description': 'Clearinggebühr EPEX Spotmarkt'
        }
    ]
    
    for lc_data in legal_charges:
        existing = LegalCharges.query.filter_by(name=lc_data['name']).first()
        if not existing:
            legal_charge = LegalCharges(**lc_data)
            db.session.add(legal_charge)
            print(f"  - {lc_data['name']}")
        else:
            print(f"  - {lc_data['name']}: Bereits vorhanden")
    
    db.session.commit()

def create_standard_renewable_subsidies():
    """Erstellt Standard-Förderungen für erneuerbare Energien"""
    print("Erstelle Standard-Förderungen...")
    
    renewable_subsidies = [
        {
            'name': 'PV Förderung 2024',
            'technology_type': 'pv',
            'subsidy_eur_mwh': 0.0,
            'region': 'AT',
            'year': 2024,
            'max_capacity_mw': 1000.0,
            'description': 'PV Förderung Österreich 2024 (0 EUR/MWh)'
        },
        {
            'name': 'BESS Förderung 2024',
            'technology_type': 'bess',
            'subsidy_eur_mwh': 0.0,
            'region': 'AT',
            'year': 2024,
            'max_capacity_mw': 100.0,
            'description': 'BESS Förderung Österreich 2024 (0 EUR/MWh)'
        }
    ]
    
    for rs_data in renewable_subsidies:
        existing = RenewableSubsidy.query.filter_by(name=rs_data['name']).first()
        if not existing:
            renewable_subsidy = RenewableSubsidy(**rs_data)
            db.session.add(renewable_subsidy)
            print(f"  - {rs_data['name']}")
        else:
            print(f"  - {rs_data['name']}: Bereits vorhanden")
    
    db.session.commit()

def create_regulatory_changes():
    """Erstellt gesetzliche Änderungen"""
    print("Erstelle gesetzliche Änderungen...")
    
    regulatory_changes = [
        {
            'name': 'Stromabgabe Erhöhung 2025',
            'change_type': 'tax_increase',
            'old_value_eur_mwh': 1.0,
            'new_value_eur_mwh': 15.0,
            'change_year': 2025,
            'region': 'AT',
            'description': 'Erhöhung der Stromabgabe von 1 EUR auf 15 EUR/MWh ab 2025'
        }
    ]
    
    for rc_data in regulatory_changes:
        existing = RegulatoryChanges.query.filter_by(name=rc_data['name']).first()
        if not existing:
            regulatory_change = RegulatoryChanges(**rc_data)
            db.session.add(regulatory_change)
            print(f"  - {rc_data['name']}")
        else:
            print(f"  - {rc_data['name']}: Bereits vorhanden")
    
    db.session.commit()

def main():
    """Hauptfunktion für die Migration"""
    print("=== BESS-Simulation Datenbank-Migration ===")
    print(f"Startzeit: {datetime.now()}")
    
    try:
        # Flask-App erstellen
        app = create_app()
        
        with app.app_context():
            # Datenbank-Tabellen erstellen
            print("\n1. Erstelle neue Datenbank-Tabellen...")
            db.create_all()
            print("   ✓ Tabellen erfolgreich erstellt")
            
            # Standard-Daten einfügen
            print("\n2. Füge Standard-Daten ein...")
            create_standard_use_cases()
            create_standard_revenue_models()
            create_standard_grid_tariffs()
            create_standard_legal_charges()
            create_standard_renewable_subsidies()
            create_regulatory_changes()
            
            print("\n✓ Migration erfolgreich abgeschlossen!")
            print(f"Endzeit: {datetime.now()}")
            
    except Exception as e:
        print(f"\n❌ Fehler bei der Migration: {e}")
        db.session.rollback()
        sys.exit(1)

if __name__ == "__main__":
    main() 