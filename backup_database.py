#!/usr/bin/env python3
"""
Datenbank-Sicherung: SQL-Dump erstellen
"""

import sqlite3
import os
from datetime import datetime

def create_sql_dump():
    """Erstellt einen SQL-Dump der Datenbank"""
    
    db_path = 'instance/bess.db'
    
    if not os.path.exists(db_path):
        print("❌ Datenbank nicht gefunden:", db_path)
        return False
    
    # Zeitstempel für Backup-Datei
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    dump_path = f'instance/bess_backup_{timestamp}.sql'
    
    try:
        # Verbindung zur Datenbank
        conn = sqlite3.connect(db_path)
        
        # SQL-Dump erstellen
        with open(dump_path, 'w', encoding='utf-8') as f:
            for line in conn.iterdump():
                f.write(f'{line}\n')
        
        conn.close()
        
        # Dateigröße prüfen
        file_size = os.path.getsize(dump_path)
        file_size_mb = file_size / (1024 * 1024)
        
        print(f"✅ SQL-Dump erstellt: {dump_path}")
        print(f"   Größe: {file_size_mb:.2f} MB")
        print(f"   Zeitstempel: {timestamp}")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Erstellen des SQL-Dumps: {e}")
        return False

def list_backups():
    """Listet alle verfügbaren Backups auf"""
    
    print("\n📋 Verfügbare Datenbank-Backups:")
    
    # SQLite-Dateien
    print("\n🗄️  SQLite-Dateien:")
    for file in os.listdir('instance'):
        if file.endswith('.db'):
            file_path = os.path.join('instance', file)
            file_size = os.path.getsize(file_path)
            file_size_mb = file_size / (1024 * 1024)
            mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            print(f"   📄 {file} ({file_size_mb:.2f} MB) - {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # SQL-Dumps
    print("\n📄 SQL-Dumps:")
    for file in os.listdir('instance'):
        if file.endswith('.sql'):
            file_path = os.path.join('instance', file)
            file_size = os.path.getsize(file_path)
            file_size_mb = file_size / (1024 * 1024)
            mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            print(f"   📄 {file} ({file_size_mb:.2f} MB) - {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    print("🚀 Erstelle Datenbank-Sicherung")
    
    # SQL-Dump erstellen
    success = create_sql_dump()
    
    if success:
        print("\n✅ Sicherung erfolgreich erstellt")
    else:
        print("\n❌ Sicherung fehlgeschlagen")
    
    # Alle Backups auflisten
    list_backups() 