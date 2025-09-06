#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug-Script für aWattar Import-Probleme
"""

from awattar_data_fetcher import awattar_fetcher
from datetime import datetime, timedelta

def debug_awattar_import():
    """Debug der aWattar Import-Funktionalität"""
    print('Debug aWattar Import...')
    print('=' * 40)
    
    # 1. Test der API-Verbindung
    print('\n1. Testing API connection...')
    api_response = awattar_fetcher.fetch_market_data()
    print(f'   API Response: {api_response["success"]}')
    if not api_response['success']:
        print(f'   Error: {api_response["error"]}')
        return False
    
    # 2. Test des Parsings
    print('\n2. Testing data parsing...')
    parsed_data = awattar_fetcher.parse_market_data(api_response)
    print(f'   Parsed {len(parsed_data)} data points')
    if not parsed_data:
        print('   Error: No data parsed')
        return False
    
    # 3. Test der Datenbank-Integration
    print('\n3. Testing database integration...')
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            # Test mit nur 1 Datensatz
            test_data = parsed_data[:1]
            save_result = awattar_fetcher.save_to_database(test_data)
            
            print(f'   Save result: {save_result["success"]}')
            if save_result['success']:
                print(f'   Saved: {save_result["saved_count"]}')
                print(f'   Skipped: {save_result["skipped_count"]}')
                print(f'   Errors: {save_result["error_count"]}')
            else:
                print(f'   Error: {save_result["error"]}')
                return False
                
    except Exception as e:
        print(f'   Database error: {e}')
        return False
    
    # 4. Test des kompletten Workflows
    print('\n4. Testing complete workflow...')
    try:
        with app.app_context():
            # Test mit heutigem Datum
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow = today + timedelta(days=1)
            
            result = awattar_fetcher.fetch_and_save(
                start_date=today,
                end_date=tomorrow
            )
            
            print(f'   Workflow result: {result["success"]}')
            if result['success']:
                print(f'   Total processed: {result["save_result"]["total_processed"]}')
                print(f'   Saved: {result["save_result"]["saved_count"]}')
            else:
                print(f'   Error: {result["error"]}')
                print(f'   Step: {result.get("step", "unknown")}')
                return False
                
    except Exception as e:
        print(f'   Workflow error: {e}')
        return False
    
    print('\n✅ All tests passed!')
    return True

if __name__ == "__main__":
    debug_awattar_import()
