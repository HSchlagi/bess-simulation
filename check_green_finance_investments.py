#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script zum Prüfen der gespeicherten Green Finance Investitionen
"""

import sqlite3
import os
import sys
from datetime import datetime

# Windows Encoding-Fix
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def check_investments():
    """Prüft alle gespeicherten Green Finance Investitionen"""
    
    # Datenbankpfad
    db_path = os.path.join('instance', 'bess.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Datenbank nicht gefunden: {db_path}")
        return
    
    print("=" * 70)
    print("Green Finance Investitionen - Übersicht")
    print("=" * 70)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Prüfe ob Tabelle existiert
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='green_finance_investments'
        """)
        
        if not cursor.fetchone():
            print("⚠️  Tabelle 'green_finance_investments' existiert noch nicht.")
            print("   Es wurden noch keine Investitionen gespeichert.")
            conn.close()
            return
        
        # Alle Investitionen abrufen
        cursor.execute("""
            SELECT 
                id, 
                project_id, 
                investment_type, 
                amount_eur, 
                investment_date, 
                description, 
                created_at
            FROM green_finance_investments
            ORDER BY investment_date DESC, created_at DESC
        """)
        
        investments = cursor.fetchall()
        
        if not investments:
            print("\n📊 Keine Investitionen gefunden.")
            print("   Die Tabelle existiert, ist aber leer.")
        else:
            print(f"\n📊 Anzahl Investitionen: {len(investments)}")
            print("-" * 70)
            
            total_amount = 0
            type_totals = {}
            
            for inv in investments:
                inv_id, project_id, inv_type, amount, inv_date, description, created_at = inv
                
                # Projektname abrufen (falls vorhanden)
                project_name = "Unbekannt"
                if project_id:
                    cursor.execute("SELECT name FROM project WHERE id = ?", (project_id,))
                    project_result = cursor.fetchone()
                    if project_result:
                        project_name = project_result[0]
                
                print(f"\n🔹 Investition ID: {inv_id}")
                print(f"   Projekt: {project_name} (ID: {project_id or 'Kein Projekt'})")
                print(f"   Typ: {inv_type}")
                print(f"   Betrag: {amount:,.2f} €")
                print(f"   Datum: {inv_date}")
                if description:
                    print(f"   Beschreibung: {description[:50]}{'...' if len(description) > 50 else ''}")
                print(f"   Erstellt am: {created_at}")
                
                total_amount += amount
                if inv_type in type_totals:
                    type_totals[inv_type] += amount
                else:
                    type_totals[inv_type] = amount
            
            print("\n" + "=" * 70)
            print("📈 ZUSAMMENFASSUNG")
            print("=" * 70)
            print(f"\n💰 Gesamtbetrag aller Investitionen: {total_amount:,.2f} €")
            print(f"📊 Anzahl Investitionen: {len(investments)}")
            
            if type_totals:
                print("\n📋 Aufteilung nach Typ:")
                for inv_type, amount in sorted(type_totals.items(), key=lambda x: x[1], reverse=True):
                    percentage = (amount / total_amount * 100) if total_amount > 0 else 0
                    print(f"   • {inv_type}: {amount:,.2f} € ({percentage:.1f}%)")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Datenbankfehler: {e}")
    except Exception as e:
        print(f"❌ Fehler: {e}")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    check_investments()

