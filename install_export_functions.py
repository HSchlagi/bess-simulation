#!/usr/bin/env python3
"""
Installations-Skript für Export-Funktionen
Installiert alle notwendigen Abhängigkeiten für PDF, Excel und CSV Export
"""

import subprocess
import sys
import os
from pathlib import Path

def install_package(package):
    """Installiert ein Python-Paket"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} erfolgreich installiert")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Fehler beim Installieren von {package}")
        return False

def check_package(package):
    """Überprüft ob ein Paket installiert ist"""
    try:
        __import__(package)
        return True
    except ImportError:
        return False

def main():
    print("🚀 Installation der Export-Funktionen für BESS-Simulation")
    print("=" * 60)
    
    # Liste der benötigten Pakete
    required_packages = [
        "reportlab>=4.0.0",
        "openpyxl>=3.1.0", 
        "pandas>=2.0.0",
        "Pillow>=10.0.0",
        "matplotlib>=3.7.0"
    ]
    
    # Optionale Pakete für erweiterte Funktionen
    optional_packages = [
        "seaborn>=0.12.0",
        "xlsxwriter>=3.1.0",
        "weasyprint>=60.0"
    ]
    
    print("\n📦 Installiere erforderliche Pakete...")
    success_count = 0
    
    for package in required_packages:
        package_name = package.split('>=')[0]
        if check_package(package_name):
            print(f"✅ {package_name} bereits installiert")
            success_count += 1
        else:
            if install_package(package):
                success_count += 1
    
    print(f"\n📊 {success_count}/{len(required_packages)} erforderliche Pakete installiert")
    
    if success_count == len(required_packages):
        print("\n🎉 Alle erforderlichen Pakete erfolgreich installiert!")
        
        # Erstelle Export-Verzeichnisse
        export_dirs = ["export", "export_templates"]
        for dir_name in export_dirs:
            Path(dir_name).mkdir(exist_ok=True)
            print(f"📁 Verzeichnis '{dir_name}' erstellt")
        
        # Erstelle Standard-Templates
        try:
            from export_functions import create_default_templates
            create_default_templates()
            print("📋 Standard-Export-Templates erstellt")
        except Exception as e:
            print(f"⚠️  Fehler beim Erstellen der Templates: {e}")
        
        print("\n✨ Export-Funktionen sind bereit!")
        print("\nVerfügbare Export-Formate:")
        print("  📄 PDF Export - Professionelle Projektberichte")
        print("  📊 Excel Export - Simulationsdaten mit Grafiken")
        print("  📋 CSV Export - Rohdaten für weitere Verarbeitung")
        print("  📦 Batch Export - Mehrere Projekte gleichzeitig")
        
        print("\n🔗 Zugriff über:")
        print("  - Export-Zentrum: /export/")
        print("  - Projekt-Seiten: Export-Dropdown bei jedem Projekt")
        print("  - Navigation: Daten → Export-Zentrum")
        
    else:
        print("\n❌ Installation nicht vollständig. Bitte überprüfen Sie die Fehlermeldungen.")
        print("\n💡 Tipps:")
        print("  - Stellen Sie sicher, dass Sie Administrator-Rechte haben")
        print("  - Überprüfen Sie Ihre Internet-Verbindung")
        print("  - Versuchen Sie: pip install --upgrade pip")
    
    print("\n" + "=" * 60)
    print("Installation abgeschlossen!")

if __name__ == "__main__":
    main()
