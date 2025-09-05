#!/usr/bin/env python3
"""
Erstellt eine aktuelle Datenbank-Sicherung für Hetzner-Deployment
"""

import sqlite3
import gzip
from datetime import datetime
import os

def create_hetzner_backup():
    """Erstellt eine komprimierte Datenbank-Sicherung für Hetzner"""
    
    db_path = 'instance/bess.db'
    if not os.path.exists(db_path):
        print(f"❌ Datenbank nicht gefunden: {db_path}")
        return False
    
    # Backup-Dateiname mit Zeitstempel
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_name = f'database_backup_hetzner_{timestamp}.sql.gz'
    
    try:
        # Datenbankverbindung
        conn = sqlite3.connect(db_path)
        
        # Komprimierte Sicherung erstellen
        with gzip.open(backup_name, 'wt', encoding='utf-8') as f:
            for line in conn.iterdump():
                f.write(f'{line}\n')
        
        conn.close()
        
        # Dateigröße ermitteln
        file_size = os.path.getsize(backup_name)
        file_size_mb = file_size / (1024 * 1024)
        
        print(f"✅ Hetzner-Datenbank-Sicherung erstellt:")
        print(f"   📁 Datei: {backup_name}")
        print(f"   📊 Größe: {file_size_mb:.2f} MB")
        print(f"   🕒 Zeitstempel: {timestamp}")
        
        return backup_name
        
    except Exception as e:
        print(f"❌ Fehler beim Erstellen der Sicherung: {e}")
        return False

if __name__ == "__main__":
    create_hetzner_backup()
