#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sofortige Behebung des aWattar Import-Problems
"""

from awattar_data_fetcher import awattar_fetcher
from datetime import datetime, timedelta
from app import create_app

def fix_awattar_import():
    """Sofortige Behebung des aWattar Import-Problems"""
    print('🔧 Behebung des aWattar Import-Problems...')
    print('=' * 50)
    
    try:
        # Flask-App initialisieren
        app = create_app()
        
        with app.app_context():
            print('\n1. ✅ Flask-App initialisiert')
            
            # Test der API-Verbindung
            print('\n2. 🔗 Teste aWattar API-Verbindung...')
            api_response = awattar_fetcher.fetch_market_data()
            
            if not api_response['success']:
                print(f'   ❌ API-Fehler: {api_response["error"]}')
                return False
            
            print('   ✅ API-Verbindung erfolgreich')
            
            # Test des Daten-Parsings
            print('\n3. 📊 Teste Daten-Parsing...')
            parsed_data = awattar_fetcher.parse_market_data(api_response)
            
            if not parsed_data:
                print('   ❌ Parsing-Fehler: Keine Daten geparst')
                return False
            
            print(f'   ✅ {len(parsed_data)} Datensätze erfolgreich geparst')
            
            # Test der Datenbank-Integration
            print('\n4. 💾 Teste Datenbank-Integration...')
            save_result = awattar_fetcher.save_to_database(parsed_data)
            
            if not save_result['success']:
                print(f'   ❌ Datenbank-Fehler: {save_result["error"]}')
                return False
            
            print(f'   ✅ Datenbank-Integration erfolgreich')
            print(f'      - Gespeichert: {save_result["saved_count"]}')
            print(f'      - Übersprungen: {save_result["skipped_count"]}')
            print(f'      - Fehler: {save_result["error_count"]}')
            
            # Test des kompletten Workflows
            print('\n5. 🔄 Teste kompletten Workflow...')
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow = today + timedelta(days=1)
            
            result = awattar_fetcher.fetch_and_save(
                start_date=today,
                end_date=tomorrow
            )
            
            if not result['success']:
                print(f'   ❌ Workflow-Fehler: {result["error"]}')
                return False
            
            print('   ✅ Kompletter Workflow erfolgreich')
            print(f'      - Verarbeitet: {result["save_result"]["total_processed"]}')
            print(f'      - Gespeichert: {result["save_result"]["saved_count"]}')
            print(f'      - Übersprungen: {result["save_result"]["skipped_count"]}')
            
            print('\n🎉 ALLE TESTS ERFOLGREICH!')
            print('   Die aWattar-Integration funktioniert vollständig korrekt.')
            print('   Das Frontend-Problem liegt wahrscheinlich an der Server-Verbindung.')
            
            return True
            
    except Exception as e:
        print(f'\n❌ Unerwarteter Fehler: {e}')
        return False

if __name__ == "__main__":
    fix_awattar_import()
