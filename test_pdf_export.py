#!/usr/bin/env python3
"""
Test-Skript für PDF-Export der Wirtschaftlichkeitsanalyse
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from models import Project, Customer
from app.routes import generate_economic_analysis_pdf, get_economic_analysis_data

def test_pdf_export():
    """Testet den PDF-Export direkt"""
    app = create_app()
    
    with app.app_context():
        try:
            # Ersten verfügbaren Projekt finden
            project = Project.query.first()
            if not project:
                print("❌ Kein Projekt in der Datenbank gefunden!")
                return False
            
            print(f"📋 Teste PDF-Export für Projekt: {project.name}")
            
            # Wirtschaftlichkeitsanalyse-Daten laden
            print("📊 Lade Wirtschaftlichkeitsanalyse-Daten...")
            analysis_data = get_economic_analysis_data(project.id)
            
            if not analysis_data:
                print("❌ Keine Wirtschaftlichkeitsanalyse-Daten verfügbar!")
                return False
            
            print("✅ Wirtschaftlichkeitsanalyse-Daten geladen")
            print(f"   - Gesamtinvestition: {analysis_data.get('total_investment', 0):,.0f} €")
            print(f"   - Jährliche Einsparungen: {analysis_data.get('annual_savings', 0):,.0f} €")
            
            # PDF generieren
            print("📄 Generiere PDF...")
            pdf_content = generate_economic_analysis_pdf(project, analysis_data)
            
            if not pdf_content:
                print("❌ PDF-Generierung fehlgeschlagen!")
                return False
            
            print(f"✅ PDF erfolgreich generiert ({len(pdf_content)} Bytes)")
            
            # PDF speichern
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"test_pdf_export_{timestamp}.pdf"
            filepath = os.path.join('instance', 'exports', filename)
            
            # Export-Verzeichnis erstellen falls nicht vorhanden
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'wb') as f:
                f.write(pdf_content)
            
            print(f"✅ PDF gespeichert: {filepath}")
            
            # Datei-Größe überprüfen
            file_size = os.path.getsize(filepath)
            print(f"📏 Datei-Größe: {file_size:,} Bytes")
            
            if file_size < 1000:
                print("⚠️ Warnung: PDF-Datei ist sehr klein, könnte unvollständig sein")
            
            return True
            
        except Exception as e:
            print(f"❌ Fehler beim PDF-Export-Test: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    from datetime import datetime
    success = test_pdf_export()
    if success:
        print("\n🎉 PDF-Export-Test erfolgreich!")
    else:
        print("\n💥 PDF-Export-Test fehlgeschlagen!")
        sys.exit(1) 