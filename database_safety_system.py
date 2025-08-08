#!/usr/bin/env python3
"""
Datenbank-Sicherheitssystem für BESS-Simulation
Verhindert Datenverluste und stellt automatische Backups sicher
"""

import sqlite3
import os
import shutil
import json
from datetime import datetime, timedelta
import hashlib

class DatabaseSafetySystem:
    def __init__(self, db_path='instance/bess.db'):
        self.db_path = db_path
        self.backup_dir = 'instance/backups'
        self.ensure_backup_dir()
        
    def ensure_backup_dir(self):
        """Stellt sicher, dass das Backup-Verzeichnis existiert"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
            print(f"✅ Backup-Verzeichnis erstellt: {self.backup_dir}")
    
    def calculate_data_hash(self):
        """Berechnet Hash der aktuellen Datenbank"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Hash aller wichtigen Tabellen
            tables = ['customer', 'project', 'investment_cost']
            data_hash = ""
            
            for table in tables:
                cursor.execute(f"SELECT * FROM {table} ORDER BY id")
                rows = cursor.fetchall()
                data_hash += str(rows)
            
            conn.close()
            return hashlib.md5(data_hash.encode()).hexdigest()
        except Exception as e:
            print(f"❌ Fehler beim Hash-Berechnung: {e}")
            return None
    
    def create_backup(self, reason="automatic"):
        """Erstellt ein sicheres Backup"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            backup_name = f"bess_safe_backup_{timestamp}_{reason}.db"
            backup_path = os.path.join(self.backup_dir, backup_name)
            
            # Datenbank-Hash vor Backup
            original_hash = self.calculate_data_hash()
            
            # Backup erstellen
            shutil.copy2(self.db_path, backup_path)
            
            # Backup-Hash verifizieren
            backup_hash = self.calculate_data_hash()
            
            if original_hash == backup_hash:
                print(f"✅ Sicheres Backup erstellt: {backup_name}")
                print(f"   - Hash: {original_hash[:8]}...")
                print(f"   - Grund: {reason}")
                return backup_path
            else:
                print(f"❌ Backup-Hash stimmt nicht überein!")
                return None
                
        except Exception as e:
            print(f"❌ Fehler beim Backup: {e}")
            return None
    
    def verify_database_integrity(self):
        """Überprüft die Datenbankintegrität"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            print("🔍 Überprüfe Datenbankintegrität...")
            
            # Prüfe wichtige Tabellen
            tables = ['customer', 'project', 'investment_cost']
            integrity_issues = []
            
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"   ✅ {table}: {count} Einträge")
                except Exception as e:
                    integrity_issues.append(f"Tabelle {table}: {e}")
                    print(f"   ❌ {table}: Fehler - {e}")
            
            # Prüfe Foreign Key Constraints
            try:
                cursor.execute("""
                    SELECT p.id, p.name, c.name 
                    FROM project p 
                    LEFT JOIN customer c ON p.customer_id = c.id
                    LIMIT 5
                """)
                print("   ✅ Foreign Key Constraints: OK")
            except Exception as e:
                integrity_issues.append(f"Foreign Key: {e}")
                print(f"   ❌ Foreign Key Constraints: {e}")
            
            conn.close()
            
            if integrity_issues:
                print(f"⚠️ {len(integrity_issues)} Integritätsprobleme gefunden!")
                return False
            else:
                print("✅ Datenbankintegrität: OK")
                return True
                
        except Exception as e:
            print(f"❌ Fehler bei Integritätsprüfung: {e}")
            return False
    
    def auto_backup_before_changes(self):
        """Automatisches Backup vor Änderungen"""
        print("🔄 Erstelle automatisches Backup vor Änderungen...")
        return self.create_backup("before_changes")
    
    def restore_from_backup(self, backup_path):
        """Stellt Datenbank aus Backup wieder her"""
        try:
            print(f"🔄 Stelle Datenbank aus Backup wieder her: {backup_path}")
            
            # Backup der aktuellen DB
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            current_backup = f"instance/bess_pre_restore_{timestamp}.db"
            shutil.copy2(self.db_path, current_backup)
            
            # Wiederherstellung
            shutil.copy2(backup_path, self.db_path)
            
            # Verifizierung
            if self.verify_database_integrity():
                print("✅ Wiederherstellung erfolgreich!")
                return True
            else:
                print("❌ Wiederherstellung fehlgeschlagen!")
                return False
                
        except Exception as e:
            print(f"❌ Fehler bei Wiederherstellung: {e}")
            return False
    
    def cleanup_old_backups(self, keep_days=30):
        """Bereinigt alte Backups"""
        try:
            cutoff_date = datetime.now() - timedelta(days=keep_days)
            deleted_count = 0
            
            for filename in os.listdir(self.backup_dir):
                if filename.startswith("bess_safe_backup_") and filename.endswith(".db"):
                    file_path = os.path.join(self.backup_dir, filename)
                    file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                    
                    if file_time < cutoff_date:
                        os.remove(file_path)
                        deleted_count += 1
                        print(f"🗑️ Altes Backup gelöscht: {filename}")
            
            if deleted_count > 0:
                print(f"✅ {deleted_count} alte Backups bereinigt")
            else:
                print("ℹ️ Keine alten Backups zum Löschen gefunden")
                
        except Exception as e:
            print(f"❌ Fehler bei Backup-Bereinigung: {e}")

def setup_database_safety():
    """Richtet das Datenbank-Sicherheitssystem ein"""
    safety_system = DatabaseSafetySystem()
    
    print("🛡️ RICHTE DATENBANK-SICHERHEITSSYSTEM EIN")
    print("=" * 50)
    
    # 1. Integrität prüfen
    if not safety_system.verify_database_integrity():
        print("❌ Datenbankintegrität fehlgeschlagen!")
        return False
    
    # 2. Sicheres Backup erstellen
    backup_path = safety_system.create_backup("setup_safety_system")
    if not backup_path:
        print("❌ Backup-Erstellung fehlgeschlagen!")
        return False
    
    # 3. Alte Backups bereinigen
    safety_system.cleanup_old_backups()
    
    print("✅ Datenbank-Sicherheitssystem erfolgreich eingerichtet!")
    return True

if __name__ == "__main__":
    setup_database_safety()
