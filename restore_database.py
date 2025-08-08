#!/usr/bin/env python3
"""
Wiederherstellung der Datenbank aus dem neuesten Backup
"""

import sqlite3
import os
import shutil
from datetime import datetime

def restore_database():
    """Stellt die Datenbank aus dem neuesten Backup wieder her"""
    
    backup_file = "instance/bess_backup_2025-07-24_09-47-54.db"
    current_db = "instance/bess.db"
    
    if not os.path.exists(backup_file):
        print(f"❌ Backup nicht gefunden: {backup_file}")
        return False
    
    try:
        # Backup der aktuellen DB erstellen
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_current = f"instance/bess_corrupted_{timestamp}.db"
        
        if os.path.exists(current_db):
            shutil.copy2(current_db, backup_current)
            print(f"✅ Aktuelle DB als Backup gespeichert: {backup_current}")
        
        # Backup wiederherstellen
        shutil.copy2(backup_file, current_db)
        print(f"✅ Datenbank aus Backup wiederhergestellt: {backup_file}")
        
        # Überprüfung
        conn = sqlite3.connect(current_db)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM customer")
        customers = cursor.fetchall()
        print(f"✅ {len(customers)} Kunden wiederhergestellt:")
        for customer in customers:
            print(f"   - {customer[1]} ({customer[2]})")
        
        cursor.execute("SELECT * FROM project")
        projects = cursor.fetchall()
        print(f"✅ {len(projects)} Projekte wiederhergestellt:")
        for project in projects:
            print(f"   - {project[1]} (Kunde-ID: {project[12]})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Fehler bei der Wiederherstellung: {e}")
        return False

if __name__ == "__main__":
    print("🔄 Wiederherstellung der Datenbank...")
    if restore_database():
        print("✅ Datenbank erfolgreich wiederhergestellt!")
    else:
        print("❌ Wiederherstellung fehlgeschlagen!")
