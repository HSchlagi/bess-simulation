#!/usr/bin/env python3
"""
Test-Skript für Chart-API
"""

import sqlite3
import json
from datetime import datetime

def test_chart_api():
    """Testet die Chart-API direkt"""
    
    print("🔧 Teste Chart-API...")
    print("=" * 60)
    
    try:
        # Direkte Datenbankverbindung
        conn = sqlite3.connect('instance/bess.db')
        cursor = conn.cursor()
        
        # Teste water_level Tabelle
        print("📊 Teste water_level Tabelle...")
        cursor.execute("SELECT COUNT(*) FROM water_level")
        count = cursor.fetchone()[0]
        print(f"✅ {count} Pegelstanddaten in der Datenbank")
        
        if count > 0:
            # Lade einige Beispieldaten
            cursor.execute("""
                SELECT timestamp, water_level_cm, station_name, river_name, source 
                FROM water_level 
                WHERE river_name LIKE '%Steyr%'
                ORDER BY timestamp DESC 
                LIMIT 10
            """)
            
            rows = cursor.fetchall()
            print(f"📊 {len(rows)} Steyr-Datenpunkte gefunden:")
            
            for row in rows:
                print(f"  📅 {row[0]} | {row[1]} cm | {row[2]} | {row[3]} | {row[4]}")
            
            # Simuliere API-Response
            water_levels = []
            for row in rows:
                water_levels.append({
                    'timestamp': row[0],
                    'water_level_cm': float(row[1]),
                    'station_name': row[2],
                    'river_name': row[3],
                    'source': row[4]
                })
            
            api_response = {
                'success': True,
                'data': water_levels,
                'source': 'EHYD (Demo) - Basierend auf echten österreichischen Mustern',
                'message': f'{len(water_levels)} Pegelstanddaten geladen'
            }
            
            print(f"\n📊 API-Response:")
            print(json.dumps(api_response, indent=2, ensure_ascii=False))
            
            # Teste Chart-Daten
            print(f"\n📈 Chart-Daten vorbereitet:")
            labels = [row[0][:10] for row in rows]  # Nur Datum
            values = [float(row[1]) for row in rows]
            
            print(f"  📅 Labels: {labels}")
            print(f"  📊 Values: {values}")
            
        else:
            print("⚠️ Keine Pegelstanddaten in der Datenbank")
            print("💡 Laden Sie zuerst EHYD-Daten mit: python test_fix_ehyd.py")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Chart-API Test abgeschlossen!")

if __name__ == "__main__":
    test_chart_api() 