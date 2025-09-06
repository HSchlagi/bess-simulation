#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test-Script für aktualisierte aWattar Template-Struktur
"""

def test_awattar_template():
    """Testet die aktualisierte aWattar Template-Struktur"""
    print('Testing updated aWattar page structure...')
    print('=' * 50)
    
    # Prüfe ob die Datei korrekt strukturiert ist
    with open('app/templates/awattar_import.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Prüfe wichtige Elemente
    checks = [
        ('{% extends "base.html" %}', 'Base template extension'),
        ('{% block title %}', 'Title block'),
        ('{% block content %}', 'Content block'),
        ('{% endblock %}', 'End block'),
        ('status-card', 'Status card CSS class'),
        ('price-chart', 'Price chart CSS class')
    ]
    
    print('\nChecking template structure:')
    for check, description in checks:
        if check in content:
            print(f'   ✅ {description}: Found')
        else:
            print(f'   ❌ {description}: Missing')
    
    print('\n✅ Template structure check completed!')

if __name__ == "__main__":
    test_awattar_template()
