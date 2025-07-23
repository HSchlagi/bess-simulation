#!/usr/bin/env python3
"""
Test Filter - Überprüft die Spot-Preis-Filterfunktion
"""

import sqlite3
from datetime import datetime

def test_filter_function():
    """Testet die Filterfunktion für verschiedene Zeiträume"""
    
    print("🧪 Teste Spot-Preis-Filterfunktion...")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('instance/bess.db')
        cursor = conn.cursor()
        
        # Test 1: Heute (2025)
        print("📅 Test 1: Heute (2025)")
        start_date = datetime(2025, 7, 23, 0, 0, 0)
        end_date = datetime(2025, 7, 23, 23, 59, 59)
        
        cursor.execute("""
            SELECT COUNT(*) FROM spot_price 
            WHERE timestamp BETWEEN ? AND ?
        """, (start_date, end_date))
        
        count_today = cursor.fetchone()[0]
        print(f"   Datenpunkte heute: {count_today}")
        
        # Test 2: 2024 (ganzes Jahr)
        print("📅 Test 2: 2024 (ganzes Jahr)")
        start_date_2024 = datetime(2024, 1, 1, 0, 0, 0)
        end_date_2024 = datetime(2024, 12, 31, 23, 59, 59)
        
        cursor.execute("""
            SELECT COUNT(*) FROM spot_price 
            WHERE timestamp BETWEEN ? AND ?
        """, (start_date_2024, end_date_2024))
        
        count_2024 = cursor.fetchone()[0]
        print(f"   Datenpunkte 2024: {count_2024}")
        
        # Test 3: Januar 2024
        print("📅 Test 3: Januar 2024")
        start_date_jan = datetime(2024, 1, 1, 0, 0, 0)
        end_date_jan = datetime(2024, 1, 31, 23, 59, 59)
        
        cursor.execute("""
            SELECT COUNT(*) FROM spot_price 
            WHERE timestamp BETWEEN ? AND ?
        """, (start_date_jan, end_date_jan))
        
        count_jan = cursor.fetchone()[0]
        print(f"   Datenpunkte Januar 2024: {count_jan}")
        
        # Test 4: Datenquelle für 2024
        print("📅 Test 4: Datenquelle für 2024")
        cursor.execute("""
            SELECT DISTINCT source FROM spot_price 
            WHERE timestamp BETWEEN ? AND ?
        """, (start_date_2024, end_date_2024))
        
        sources_2024 = cursor.fetchall()
        print(f"   Datenquellen 2024: {[s[0] for s in sources_2024]}")
        
        # Test 5: Preis-Statistiken 2024
        print("📅 Test 5: Preis-Statistiken 2024")
        cursor.execute("""
            SELECT AVG(price_eur_mwh), MAX(price_eur_mwh), MIN(price_eur_mwh)
            FROM spot_price 
            WHERE timestamp BETWEEN ? AND ?
        """, (start_date_2024, end_date_2024))
        
        stats_2024 = cursor.fetchone()
        print(f"   Durchschnitt 2024: {stats_2024[0]:.2f} €/MWh")
        print(f"   Maximum 2024: {stats_2024[1]:.2f} €/MWh")
        print(f"   Minimum 2024: {stats_2024[2]:.2f} €/MWh")
        
        conn.close()
        
        print("=" * 50)
        print("✅ Filterfunktion-Test abgeschlossen!")
        
        # Zusammenfassung
        print("\n📊 ZUSAMMENFASSUNG:")
        print(f"   • Heute (2025): {count_today} Datenpunkte")
        print(f"   • 2024 (ganzes Jahr): {count_2024} Datenpunkte")
        print(f"   • Januar 2024: {count_jan} Datenpunkte")
        print(f"   • Erwartet für 2024: 8760 Datenpunkte")
        print(f"   • Erwartet für Januar 2024: 744 Datenpunkte (31 Tage × 24 Stunden)")
        
        if count_2024 == 8760:
            print("   ✅ 2024-Daten vollständig!")
        else:
            print(f"   ⚠️ 2024-Daten unvollständig: {count_2024}/8760")
        
        if count_jan == 744:
            print("   ✅ Januar 2024 vollständig!")
        else:
            print(f"   ⚠️ Januar 2024 unvollständig: {count_jan}/744")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Testen: {e}")
        return False

if __name__ == "__main__":
    test_filter_function() 