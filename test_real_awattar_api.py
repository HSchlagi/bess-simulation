#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test der echten aWattar API-Calls
"""

import requests
import json

def test_real_awattar_api():
    """Test der echten aWattar API-Endpunkte"""
    print('Testing real aWattar API calls...')
    print('=' * 40)

    base_url = 'http://localhost:5000'

    # 1. Status-Test
    try:
        response = requests.get(f'{base_url}/api/awattar/status')
        print(f'1. Status API: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'   Success: {data["success"]}')
            if data['success']:
                print(f'   API Connection: {data["status"]["api_connection"]}')
                print(f'   Database Records: {data["status"]["database_records"]}')
                print(f'   Last 24h: {data["status"]["last_24h"]}')
                print(f'   Latest Price: {data["status"]["latest_price"]}')
            else:
                print(f'   Error: {data["error"]}')
        else:
            print(f'   HTTP Error: {response.text}')
    except Exception as e:
        print(f'   Connection Error: {e}')

    print()

    # 2. Latest Prices Test
    try:
        response = requests.get(f'{base_url}/api/awattar/latest?hours=24')
        print(f'2. Latest Prices API: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'   Success: {data["success"]}')
            if data['success']:
                print(f'   Data points: {len(data["data"]) if data["data"] else 0}')
                if data['data'] and len(data['data']) > 0:
                    print(f'   First price: {data["data"][0]["price_eur_mwh"]} €/MWh')
                    print(f'   Last price: {data["data"][-1]["price_eur_mwh"]} €/MWh')
            else:
                print(f'   Error: {data["error"]}')
        else:
            print(f'   HTTP Error: {response.text}')
    except Exception as e:
        print(f'   Connection Error: {e}')

    print()

    # 3. Test API
    try:
        response = requests.get(f'{base_url}/api/awattar/test')
        print(f'3. Test API: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'   Success: {data["success"]}')
            if data['success']:
                print(f'   Message: {data["message"]}')
            else:
                print(f'   Error: {data["error"]}')
        else:
            print(f'   HTTP Error: {response.text}')
    except Exception as e:
        print(f'   Connection Error: {e}')

    print()
    print('Real API tests completed!')

if __name__ == "__main__":
    test_real_awattar_api()
