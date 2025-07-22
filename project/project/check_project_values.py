#!/usr/bin/env python3
"""
Skript zum Überprüfen der BESS-Werte in der Datenbank
"""

import sqlite3
import os

def check_project_values():
    """Überprüft die BESS-Werte in der Datenbank"""
    
    # Pfad zur Datenbank
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'bess.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Datenbank nicht gefunden: {db_path}")
        return False
    
    try:
        # Verbindung zur Datenbank herstellen
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Überprüfe Projekt-Werte...")
        
        # Alle Projekte abrufen
        cursor.execute("SELECT id, name, bess_size, bess_power, bess_investment, bess_operation_cost FROM project")
        projects = cursor.fetchall()
        
        if not projects:
            print("❌ Keine Projekte in der Datenbank gefunden")
            return False
        
        print(f"📋 Gefundene Projekte: {len(projects)}")
        print("\n" + "="*80)
        print(f"{'ID':<5} {'Name':<30} {'BESS Size':<12} {'BESS Power':<12} {'Investment':<12} {'Operation':<12}")
        print("="*80)
        
        for project in projects:
            project_id, name, bess_size, bess_power, bess_investment, bess_operation_cost = project
            # Sichere Formatierung für None-Werte
            bess_size_str = str(bess_size) if bess_size is not None else "None"
            bess_power_str = str(bess_power) if bess_power is not None else "None"
            bess_investment_str = str(bess_investment) if bess_investment is not None else "None"
            bess_operation_str = str(bess_operation_cost) if bess_operation_cost is not None else "None"
            
            print(f"{project_id:<5} {name:<30} {bess_size_str:<12} {bess_power_str:<12} {bess_investment_str:<12} {bess_operation_str:<12}")
        
        print("="*80)
        
        # Spezifisches Projekt (BESS-Hinterstoder) überprüfen
        cursor.execute("SELECT * FROM project WHERE name LIKE '%Hinterstoder%'")
        hinterstoder = cursor.fetchone()
        
        if hinterstoder:
            print(f"\n🎯 Detaillierte Werte für 'BESS-Hinterstoder':")
            print(f"   BESS Size: {hinterstoder[4]} kWh")
            print(f"   BESS Power: {hinterstoder[5]} kW")
            print(f"   BESS Investment: {hinterstoder[11]} €")
            print(f"   BESS Operation: {hinterstoder[16]} €/Jahr")
            
            # Alle Spalten anzeigen
            cursor.execute("PRAGMA table_info(project)")
            columns = [column[1] for column in cursor.fetchall()]
            print(f"\n📋 Alle Spalten: {columns}")
            
            print(f"\n🔍 Alle Werte für BESS-Hinterstoder:")
            for i, value in enumerate(hinterstoder):
                if i < len(columns):
                    print(f"   {columns[i]}: {value}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Überprüfen der Datenbank: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Überprüfe Projekt-Werte in der Datenbank...")
    success = check_project_values()
    
    if success:
        print("✅ Überprüfung abgeschlossen!")
    else:
        print("❌ Überprüfung fehlgeschlagen!") 