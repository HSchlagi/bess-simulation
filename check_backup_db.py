#!/usr/bin/env python3
import sqlite3
import os

def check_backup_db(filename):
    print(f"\n=== PRÜFE BACKUP: {filename} ===")
    
    if not os.path.exists(f"instance/{filename}"):
        print(f"❌ Backup nicht gefunden: {filename}")
        return
    
    try:
        conn = sqlite3.connect(f"instance/{filename}")
        cursor = conn.cursor()
        
        # Kunden prüfen
        cursor.execute("SELECT * FROM customer")
        customers = cursor.fetchall()
        print(f"Kunden: {len(customers)}")
        for c in customers:
            print(f"  - {c[1]} ({c[2]})")
        
        # Projekte prüfen
        cursor.execute("SELECT * FROM project")
        projects = cursor.fetchall()
        print(f"Projekte: {len(projects)}")
        for p in projects:
            print(f"  - {p[1]} (Kunde-ID: {p[12]})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Fehler: {e}")

# Prüfe alle Backups
backups = [
    "bess_backup_2025-07-23_18-04.db",
    "bess_backup_2025-07-24_09-47-54.db"
]

for backup in backups:
    check_backup_db(backup)
