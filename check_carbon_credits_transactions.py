#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script zum Prüfen der Carbon Credits Transaktionen
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

def check_transactions():
    """Prüft alle Carbon Credits Transaktionen"""
    
    # Datenbankpfad
    db_path = os.path.join('instance', 'bess.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Datenbank nicht gefunden: {db_path}")
        return
    
    print("=" * 70)
    print("Carbon Credits Transaktionen - Übersicht")
    print("=" * 70)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Prüfe ob Tabelle existiert
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='carbon_credits_transactions'
        """)
        
        if not cursor.fetchone():
            print("⚠️  Tabelle 'carbon_credits_transactions' existiert noch nicht.")
            print("   Es wurden noch keine Transaktionen gespeichert.")
            conn.close()
            return
        
        # Alle Transaktionen abrufen
        cursor.execute("""
            SELECT 
                id, 
                project_id, 
                transaction_type, 
                credits, 
                price_per_credit_eur, 
                total_value_eur,
                transaction_date, 
                notes, 
                created_at
            FROM carbon_credits_transactions
            ORDER BY transaction_date DESC, created_at DESC
        """)
        
        transactions = cursor.fetchall()
        
        if not transactions:
            print("\n📊 Keine Transaktionen gefunden.")
            print("   Die Tabelle existiert, ist aber leer.")
        else:
            print(f"\n📊 Anzahl Transaktionen: {len(transactions)}")
            print("-" * 70)
            
            # Statistiken berechnen
            total_generated = 0
            total_sold = 0
            total_revenue = 0
            
            for trans in transactions:
                trans_id, project_id, trans_type, credits, price_per_credit, total_value, trans_date, notes, created_at = trans
                
                # Projektname abrufen (falls vorhanden)
                project_name = "Unbekannt"
                if project_id:
                    cursor.execute("SELECT name FROM project WHERE id = ?", (project_id,))
                    project_result = cursor.fetchone()
                    if project_result:
                        project_name = project_result[0]
                
                print(f"\n🔹 Transaktion ID: {trans_id}")
                print(f"   Projekt: {project_name} (ID: {project_id or 'Kein Projekt'})")
                print(f"   Typ: {trans_type}")
                print(f"   Credits: {credits}")
                if trans_type == 'sell':
                    print(f"   Preis pro Credit: {price_per_credit:.2f} €")
                    print(f"   Gesamtbetrag: {total_value:.2f} €")
                print(f"   Datum: {trans_date}")
                if notes:
                    print(f"   Notizen: {notes[:50]}{'...' if len(notes) > 50 else ''}")
                print(f"   Erstellt am: {created_at}")
                
                # Statistiken aktualisieren
                if trans_type == 'generate':
                    total_generated += credits
                elif trans_type == 'sell':
                    total_sold += credits
                    total_revenue += total_value
            
            # Verfügbare Credits berechnen
            available_credits = total_generated - total_sold
            
            print("\n" + "=" * 70)
            print("📈 ZUSAMMENFASSUNG")
            print("=" * 70)
            print(f"\n💰 Generierte Credits: {total_generated}")
            print(f"💰 Verkaufte Credits: {total_sold}")
            print(f"💰 Verfügbare Credits: {available_credits}")
            print(f"💰 Gesamtumsatz: {total_revenue:,.2f} €")
            
            if total_sold > 0:
                avg_price = total_revenue / total_sold
                print(f"💰 Durchschnittspreis: {avg_price:.2f} € pro Credit")
            
            # Nach Projekt gruppiert
            cursor.execute("""
                SELECT 
                    project_id,
                    SUM(CASE WHEN transaction_type = 'generate' THEN credits ELSE 0 END) as generated,
                    SUM(CASE WHEN transaction_type = 'sell' THEN credits ELSE 0 END) as sold,
                    SUM(CASE WHEN transaction_type = 'sell' THEN total_value_eur ELSE 0 END) as revenue
                FROM carbon_credits_transactions
                GROUP BY project_id
            """)
            
            project_stats = cursor.fetchall()
            if project_stats:
                print("\n📋 Aufteilung nach Projekt:")
                for project_id, generated, sold, revenue in project_stats:
                    cursor.execute("SELECT name FROM project WHERE id = ?", (project_id,))
                    project_result = cursor.fetchone()
                    project_name = project_result[0] if project_result else f"Projekt {project_id}"
                    available = generated - sold
                    print(f"   • {project_name} (ID: {project_id}):")
                    print(f"     - Generiert: {generated}")
                    print(f"     - Verkauft: {sold}")
                    print(f"     - Verfügbar: {available}")
                    print(f"     - Umsatz: {revenue:,.2f} €")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Datenbankfehler: {e}")
    except Exception as e:
        print(f"❌ Fehler: {e}")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    check_transactions()

