#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test-Script für optimierten aWattar Scheduler
"""

from awattar_scheduler import AWattarScheduler

def test_awattar_scheduler():
    """Testet den optimierten aWattar Scheduler"""
    print('aWattar Scheduler Test (optimiert für 14:00 Uhr)')
    print('=' * 50)
    
    scheduler = AWattarScheduler()
    
    # Test der neuen Import-Funktionen
    print('\n1. Testing import_daily_prices (für nächsten Tag)...')
    if scheduler.initialize():
        result = scheduler.import_daily_prices()
        print(f'   Result: {result}')
    else:
        print('   ❌ Scheduler initialization failed')
    
    print('\n2. Testing import_today_prices (für aktuellen Tag)...')
    if scheduler.initialize():
        result = scheduler.import_today_prices()
        print(f'   Result: {result}')
    else:
        print('   ❌ Scheduler initialization failed')
    
    print('\n3. Testing schedule configuration...')
    if scheduler.initialize():
        success = scheduler.setup_schedule()
        print(f'   Schedule setup: {success}')
        
        status = scheduler.get_status()
        print(f'   Next jobs: {len(status["next_jobs"])} scheduled')
        for job in status['next_jobs'][:3]:  # Show first 3 jobs
            print(f'     - {job}')
    else:
        print('   ❌ Scheduler initialization failed')
    
    print('\n✅ Scheduler test completed!')

if __name__ == "__main__":
    test_awattar_scheduler()
