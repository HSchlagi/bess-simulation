#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test-Script für aWattar API-Integration
"""

import requests
import json

def test_awattar_api():
    """Testet alle aWattar API-Endpunkte"""
    base_url = 'http://localhost:5000'
    
    print('Testing aWattar API Endpoints...')
    print('=' * 40)
    
    # 1. Status-Test
    try:
        response = requests.get(f'{base_url}/api/awattar/status')
        print(f'1. Status API: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'   API Connection: {data["status"]["api_connection"]}')
            print(f'   Database Records: {data["status"]["database_records"]}')
        else:
            print(f'   Error: {response.text}')
    except Exception as e:
        print(f'   Error: {e}')
    
    print()
    
    # 2. Latest Prices Test
    try:
        response = requests.get(f'{base_url}/api/awattar/latest?hours=24')
        print(f'2. Latest Prices API: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'   Count: {data["count"]}')
            if data['data']:
                print(f'   Sample: {data["data"][0]}')
        else:
            print(f'   Error: {response.text}')
    except Exception as e:
        print(f'   Error: {e}')
    
    print()
    
    # 3. Test API
    try:
        response = requests.get(f'{base_url}/api/awattar/test')
        print(f'3. Test API: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'   Success: {data["success"]}')
            print(f'   Message: {data["message"]}')
        else:
            print(f'   Error: {response.text}')
    except Exception as e:
        print(f'   Error: {e}')
    
    print()
    print('API Tests completed!')

if __name__ == "__main__":
    test_awattar_api()
