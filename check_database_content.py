#!/usr/bin/env python3
"""
Überprüfung des gesamten Datenbankinhalts
"""

import sqlite3
import os

def check_database_content():
    """Überprüft den gesamten Datenbankinhalt"""
    
    db_path = 'instance/bess.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Datenbank nicht gefunden: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Überprüfung des gesamten Datenbankinhalts...")
        print("=" * 60)
        
        # Alle Tabellen auflisten
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"📊 Gefundene Tabellen: {len(tables)}")
        for table in tables:
            print(f"   - {table[0]}")
        
        print("\n" + "=" * 60)
        
        # Kunden-Tabelle überprüfen
        print("👥 KUNDEN-TABELLE:")
        cursor.execute("SELECT * FROM customer")
        customers = cursor.fetchall()
        
        if customers:
            print(f"✅ {len(customers)} Kunden gefunden:")
            for customer in customers:
                print(f"   - ID: {customer[0]}, Name: {customer[1]}, Firma: {customer[2]}")
        else:
            print("❌ Keine Kunden in der Datenbank!")
        
        print("\n" + "=" * 60)
        
        # Projekt-Tabelle überprüfen
        print("📋 PROJEKT-TABELLE:")
        cursor.execute("SELECT * FROM project")
        projects = cursor.fetchall()
        
        if projects:
            print(f"✅ {len(projects)} Projekte gefunden:")
            for project in projects:
                print(f"   - ID: {project[0]}, Name: {project[1]}")
                print(f"     Standort: {project[2]}, Kunde-ID: {project[12]}")
                print(f"     BESS Size: {project[4]} kWh, BESS Power: {project[5]} kW")
                print(f"     PV Power: {project[6]} kW, Stromkosten: {project[11]} Ct/kWh")
                print()
        else:
            print("❌ Keine Projekte in der Datenbank!")
        
        print("=" * 60)
        
        # InvestmentCost-Tabelle überprüfen
        print("💰 INVESTMENT-COST-TABELLE:")
        cursor.execute("SELECT * FROM investment_cost")
        costs = cursor.fetchall()
        
        if costs:
            print(f"✅ {len(costs)} Investitionskosten-Einträge gefunden:")
            for cost in costs:
                print(f"   - Projekt-ID: {cost[1]}, Typ: {cost[2]}, Kosten: {cost[3]} €")
        else:
            print("❌ Keine Investitionskosten in der Datenbank!")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Fehler bei der Datenbanküberprüfung: {e}")

if __name__ == "__main__":
    check_database_content()
