#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Einfacher Test für aWattar-Integration
"""

from awattar_data_fetcher import awattar_fetcher

def test_awattar_simple():
    """Einfacher Test der aWattar-Integration"""
    print('aWattar Integration Test')
    print('=' * 30)
    
    # 1. API-Test
    print('1. Testing API connection...')
    api_response = awattar_fetcher.fetch_market_data()
    if api_response['success']:
        print('   ✅ API connection successful')
        data_count = len(api_response['data'].get('data', []))
        print(f'   📊 Fetched {data_count} price points')
    else:
        print(f'   ❌ API connection failed: {api_response["error"]}')
        return False
    
    # 2. Parsing-Test
    print('\n2. Testing data parsing...')
    parsed_data = awattar_fetcher.parse_market_data(api_response)
    if parsed_data:
        print('   ✅ Data parsing successful')
        print(f'   📊 Parsed {len(parsed_data)} price points')
        sample = parsed_data[0]
        print(f'   📋 Sample: {sample["timestamp"]} - {sample["price_eur_mwh"]} €/MWh')
    else:
        print('   ❌ Data parsing failed')
        return False
    
    # 3. Datenbank-Test
    print('\n3. Testing database integration...')
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            save_result = awattar_fetcher.save_to_database(parsed_data[:3])
            
            if save_result['success']:
                print('   ✅ Database integration successful')
                print(f'   💾 Saved {save_result["saved_count"]} price points')
            else:
                print(f'   ❌ Database integration failed: {save_result["error"]}')
                return False
                
    except ImportError:
        print('   ⚠️  Flask app not available, skipping database test')
    except Exception as e:
        print(f'   ❌ Database test error: {e}')
        return False
    
    print('\n🎉 aWattar integration test completed successfully!')
    return True

if __name__ == "__main__":
    test_awattar_simple()
