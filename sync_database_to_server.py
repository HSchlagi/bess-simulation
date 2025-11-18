#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Einfaches Script zum Synchronisieren der Datenbank auf den Server
Kopiert die lokale Datenbank-Datei (mit Backup auf dem Server)
"""

import os
import shutil
from datetime import datetime

def create_backup(db_path, backup_dir='backups'):
    """Erstellt ein Backup der Datenbank"""
    if not os.path.exists(db_path):
        print(f"[FEHLER] Datenbank nicht gefunden: {db_path}")
        return None
    
    # Backup-Verzeichnis erstellen
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Backup-Dateiname mit Timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"bess_backup_{timestamp}.db"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    # Datenbank kopieren
    shutil.copy2(db_path, backup_path)
    
    print(f"[OK] Backup erstellt: {backup_path}")
    return backup_path

def show_database_info(db_path):
    """Zeigt Informationen über die Datenbank"""
    if not os.path.exists(db_path):
        print(f"[FEHLER] Datenbank nicht gefunden: {db_path}")
        return
    
    import sqlite3
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Datenbank-Größe
        size_mb = os.path.getsize(db_path) / (1024 * 1024)
        print(f"\n[INFO] Datenbank-Groesse: {size_mb:.2f} MB")
        
        # Anzahl Projekte
        cursor.execute("SELECT COUNT(*) FROM project")
        project_count = cursor.fetchone()[0]
        print(f"[INFO] Anzahl Projekte: {project_count}")
        
        # Anzahl Use Cases
        cursor.execute("SELECT COUNT(*) FROM use_case")
        use_case_count = cursor.fetchone()[0]
        print(f"[INFO] Anzahl Use Cases: {use_case_count}")
        
        # Anzahl Market Price Configs
        cursor.execute("SELECT COUNT(*) FROM market_price_config")
        config_count = cursor.fetchone()[0]
        print(f"[INFO] Anzahl Marktpreis-Konfigurationen: {config_count}")
        
    except Exception as e:
        print(f"[WARNUNG] Konnte Datenbank-Info nicht laden: {e}")
    finally:
        conn.close()

def main():
    db_path = 'instance/bess.db'
    
    print("=" * 60)
    print("Datenbank-Synchronisation")
    print("=" * 60)
    
    # Backup erstellen
    backup_path = create_backup(db_path)
    
    if not backup_path:
        return
    
    # Datenbank-Info anzeigen
    show_database_info(db_path)
    
    print("\n" + "=" * 60)
    print("[ANLEITUNG] Datenbank auf Server uebertragen:")
    print("=" * 60)
    print("\n1. Lokale Datenbank-Datei kopieren:")
    print(f"   Quell-Datei: {os.path.abspath(db_path)}")
    print(f"   Backup erstellt: {os.path.abspath(backup_path)}")
    print("\n2. Auf dem Server (ueber WinSCP oder scp):")
    print("   - Verbinden Sie sich mit dem Server")
    print("   - Kopieren Sie die Datei 'instance/bess.db' nach:")
    print("     /opt/bess-simulation/instance/bess.db")
    print("\n3. Auf dem Server - Backup erstellen:")
    print("   cd /opt/bess-simulation")
    print("   mkdir -p backups")
    print("   cp instance/bess.db backups/bess_backup_$(date +%Y%m%d_%H%M%S).db")
    print("\n4. Auf dem Server - Datenbank ersetzen:")
    print("   # Alte Datenbank sichern")
    print("   mv instance/bess.db instance/bess.db.old")
    print("   # Neue Datenbank kopieren (von lokal)")
    print("   # Dann: Service neu starten")
    print("   sudo systemctl restart bess")
    print("\n" + "=" * 60)
    print("[WICHTIG]")
    print("  - Erstellen Sie IMMER ein Backup auf dem Server!")
    print("  - Pruefen Sie die Datenbank-Groesse vor dem Kopieren")
    print("  - Die Datenbank wird ALLE Daten ueberschreiben!")
    print("=" * 60)

if __name__ == '__main__':
    main()

