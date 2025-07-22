#!/usr/bin/env python3
"""
Test-Skript für alle Flask-Routen
"""

import requests
import json

def test_all_routes():
    """Testet alle verfügbaren Routen"""
    
    base_url = "http://127.0.0.1:5000"
    
    print("🧪 Teste alle Flask-Routen...")
    print("=" * 60)
    
    # Alle Routen definieren
    routes = [
        # Hauptseiten
        ("/", "GET", "Startseite"),
        ("/dashboard", "GET", "Dashboard"),
        ("/projects", "GET", "Projekte"),
        ("/customers", "GET", "Kunden"),
        ("/spot_prices", "GET", "Spot-Preise"),
        ("/investment_costs", "GET", "Investitionskosten"),
        ("/reference_prices", "GET", "Referenzpreise"),
        ("/economic_analysis", "GET", "Wirtschaftlichkeitsanalyse"),
        ("/preview_data", "GET", "Datenvorschau"),
        ("/import_data", "GET", "Datenimport"),
        ("/new_project", "GET", "Neues Projekt"),
        ("/new_customer", "GET", "Neuer Kunde"),
        ("/view_project", "GET", "Projekt anzeigen"),
        ("/edit_project", "GET", "Projekt bearbeiten"),
        ("/view_customer", "GET", "Kunde anzeigen"),
        ("/edit_customer", "GET", "Kunde bearbeiten"),
        ("/import_load", "GET", "Lastprofil importieren"),
        ("/bess-peak-shaving-analysis", "GET", "BESS Peak Shaving Analyse"),
        ("/data_import_center", "GET", "Datenimport-Center"),
        ("/load_profile_detail", "GET", "Lastprofil Details"),
        
        # API-Routen
        ("/api/projects", "GET", "API: Projekte abrufen"),
        ("/api/customers", "GET", "API: Kunden abrufen"),
        ("/api/investment-costs", "GET", "API: Investitionskosten abrufen"),
        ("/api/reference-prices", "GET", "API: Referenzpreise abrufen"),
        ("/api/projects/1", "GET", "API: Projekt 1 abrufen"),
        ("/api/customers/1", "GET", "API: Kunde 1 abrufen"),
        ("/api/load-profiles/1", "GET", "API: Lastprofil 1 abrufen"),
    ]
    
    results = {
        "success": [],
        "error": [],
        "not_found": []
    }
    
    for route, method, description in routes:
        try:
            print(f"🔍 Teste: {description}")
            print(f"   Route: {method} {route}")
            
            if method == "GET":
                response = requests.get(f"{base_url}{route}")
            elif method == "POST":
                response = requests.post(f"{base_url}{route}")
            else:
                print(f"   ❌ Unbekannte Methode: {method}")
                continue
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ Erfolgreich")
                results["success"].append(f"{method} {route} - {description}")
            elif response.status_code == 404:
                print(f"   ❌ Nicht gefunden")
                results["not_found"].append(f"{method} {route} - {description}")
            else:
                print(f"   ⚠️ Fehler: {response.status_code}")
                results["error"].append(f"{method} {route} - {description} ({response.status_code})")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Server nicht erreichbar")
            results["error"].append(f"{method} {route} - {description} (Server nicht erreichbar)")
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            results["error"].append(f"{method} {route} - {description} (Exception: {e})")
        
        print()
    
    # Zusammenfassung
    print("📊 TEST-ZUSAMMENFASSUNG")
    print("=" * 60)
    print(f"✅ Erfolgreich: {len(results['success'])}")
    print(f"❌ Fehler: {len(results['error'])}")
    print(f"🔍 Nicht gefunden: {len(results['not_found'])}")
    
    if results["not_found"]:
        print("\n🔍 NICHT GEFUNDENE ROUTEN:")
        for route in results["not_found"]:
            print(f"   - {route}")
    
    if results["error"]:
        print("\n❌ FEHLERHAFTE ROUTEN:")
        for route in results["error"]:
            print(f"   - {route}")
    
    print("\n🏁 Test abgeschlossen!")

if __name__ == "__main__":
    test_all_routes() 