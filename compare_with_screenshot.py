import requests
import json

# Aktuelle Simulation abrufen
response = requests.post('http://127.0.0.1:5000/api/simulation/run', 
                        json={'project_id': 1, 'use_case': 'UC1', 'bess_mode': 'arbitrage', 'simulation_year': 2024})
result = response.json() if response.status_code == 200 else {}

print('=== VERGLEICH MIT SCREENSHOT-DATEN ===')
print('📊 AKTUELLE BERECHNUNG:')
print(f'  - Erlöse: {result.get("annual_revenues", 0):,.0f}€')
print(f'  - Investition: {result.get("total_investment", 0):,.0f}€')
print(f'  - ROI: {result.get("roi_percent", 0):.1f}%')
print(f'  - Amortisation: {result.get("payback_years", 0):.1f} Jahre')
print(f'  - Zyklen: {result.get("annual_cycles", 0)}')

print('\n📊 SCREENSHOT-DATEN (UC1 2024):')
print('  - Erlöse: 728.000€')
print('  - Netto-Gesamterlös: 686.000€')
print('  - Zyklen: 552')
print('  - Verhältnis: 17:1')

# Prozentualer Vergleich
current_revenue = result.get('annual_revenues', 0)
screenshot_revenue = 728000
percentage = (current_revenue / screenshot_revenue * 100) if screenshot_revenue > 0 else 0

print('\n📊 PROZENTUALER VERGLEICH:')
print(f'  - Erlöse: {percentage:.1f}% des Screenshot-Werts')
print(f'  - Abweichung: {percentage - 100:.1f}%')

# Anpassungsfaktor berechnen
adjustment_factor = screenshot_revenue / current_revenue if current_revenue > 0 else 1
print(f'  - Anpassungsfaktor: {adjustment_factor:.3f}')

print('\n💡 EMPFEHLUNG:')
if percentage > 120:
    print('  - Aktuelle Erlöse sind zu hoch - Anpassungsfaktor verwenden')
elif percentage < 80:
    print('  - Aktuelle Erlöse sind zu niedrig - Anpassungsfaktor verwenden')
else:
    print('  - Aktuelle Erlöse sind im akzeptablen Bereich')
