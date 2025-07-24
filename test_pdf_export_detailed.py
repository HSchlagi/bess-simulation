#!/usr/bin/env python3
"""
Detailliertes Test-Skript für PDF-Export der Wirtschaftlichkeitsanalyse
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from models import Project, Customer
from app.routes import generate_economic_analysis_pdf, get_economic_analysis_data

def test_pdf_export_detailed():
    """Testet den PDF-Export mit detaillierter Fehlerbehandlung"""
    app = create_app()
    
    with app.app_context():
        try:
            # Ersten verfügbaren Projekt finden
            project = Project.query.first()
            if not project:
                print("❌ Kein Projekt in der Datenbank gefunden!")
                return False
            
            print(f"📋 Teste PDF-Export für Projekt: {project.name}")
            print(f"   - Projekt-ID: {project.id}")
            print(f"   - Kunde: {project.customer.name if project.customer else 'Kein Kunde'}")
            
            # Schritt 1: Wirtschaftlichkeitsanalyse-Daten laden
            print("\n🔍 Schritt 1: Lade Wirtschaftlichkeitsanalyse-Daten...")
            analysis_data = get_economic_analysis_data(project.id)
            
            if not analysis_data:
                print("❌ Fehler beim Laden der Wirtschaftlichkeitsanalyse-Daten!")
                return False
            
            print("✅ Wirtschaftlichkeitsanalyse-Daten erfolgreich geladen")
            print(f"   - Gesamtinvestition: {analysis_data['total_investment']:,.0f} €")
            print(f"   - Jährlicher Gesamtnutzen: {analysis_data['total_annual_benefit']:,.0f} €")
            print(f"   - Amortisationszeit: {analysis_data['payback_period']:.1f} Jahre")
            print(f"   - ROI: {analysis_data['roi']:.1f}%")
            
            # Schritt 2: PDF generieren
            print("\n🔍 Schritt 2: Generiere PDF...")
            pdf_content = generate_economic_analysis_pdf(project, analysis_data)
            
            if not pdf_content:
                print("❌ Fehler beim PDF-Generieren!")
                return False
            
            print("✅ PDF erfolgreich generiert")
            print(f"   - PDF-Größe: {len(pdf_content):,} Bytes")
            
            # Schritt 3: PDF-Datei speichern
            print("\n🔍 Schritt 3: Speichere PDF-Datei...")
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"test_wirtschaftlichkeitsanalyse_{project.name}_{timestamp}.pdf"
            filepath = os.path.join('instance', 'exports', filename)
            
            # Export-Verzeichnis erstellen falls nicht vorhanden
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'wb') as f:
                f.write(pdf_content)
            
            print("✅ PDF-Datei erfolgreich gespeichert")
            print(f"   - Dateipfad: {filepath}")
            print(f"   - Dateigröße: {os.path.getsize(filepath):,} Bytes")
            
            # Schritt 4: PDF-Datei überprüfen
            print("\n🔍 Schritt 4: Überprüfe PDF-Datei...")
            if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                print("✅ PDF-Datei ist gültig und nicht leer")
                
                # Erste Bytes überprüfen (PDF-Header)
                with open(filepath, 'rb') as f:
                    header = f.read(10)
                    if header.startswith(b'%PDF'):
                        print("✅ PDF-Header ist korrekt")
                    else:
                        print("⚠️ PDF-Header scheint nicht korrekt zu sein")
                        print(f"   - Erste Bytes: {header}")
            else:
                print("❌ PDF-Datei ist leer oder nicht vorhanden!")
                return False
            
            print("\n🎉 PDF-Export-Test erfolgreich abgeschlossen!")
            return True
            
        except Exception as e:
            print(f"❌ Fehler beim PDF-Export-Test: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    print("🚀 Starte detaillierten PDF-Export-Test...")
    success = test_pdf_export_detailed()
    
    if success:
        print("\n✅ PDF-Export funktioniert korrekt!")
        sys.exit(0)
    else:
        print("\n❌ PDF-Export hat Fehler!")
        sys.exit(1) 