#!/usr/bin/env python3
"""
Automatisierte Datenbank-Sicherung mit Rotation und Monitoring
"""

import sqlite3
import os
import shutil
import gzip
import json
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backup.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class BackupAutomation:
    def __init__(self):
        self.db_path = 'instance/bess.db'
        self.backup_dir = 'backups'
        self.config_file = 'backup_config.json'
        self.stats_file = 'backup_stats.json'
        
        # Backup-Konfiguration
        self.config = {
            'retention': {
                'daily': 7,      # 7 tägliche Backups
                'weekly': 4,     # 4 wöchentliche Backups
                'monthly': 12    # 12 monatliche Backups
            },
            'compression': True,
            'email_notifications': False,
            'email_config': {
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'username': '',
                'password': '',
                'to_email': ''
            }
        }
        
        # Backup-Statistiken
        self.stats = {
            'total_backups': 0,
            'successful_backups': 0,
            'failed_backups': 0,
            'last_backup': None,
            'total_size_mb': 0
        }
        
        self._load_config()
        self._load_stats()
        self._ensure_backup_dir()
    
    def _load_config(self):
        """Lädt die Backup-Konfiguration"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
                logging.info("Backup-Konfiguration geladen")
            except Exception as e:
                logging.error(f"Fehler beim Laden der Konfiguration: {e}")
    
    def _save_config(self):
        """Speichert die Backup-Konfiguration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            logging.info("Backup-Konfiguration gespeichert")
        except Exception as e:
            logging.error(f"Fehler beim Speichern der Konfiguration: {e}")
    
    def _load_stats(self):
        """Lädt die Backup-Statistiken"""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r') as f:
                    self.stats = json.load(f)
            except Exception as e:
                logging.error(f"Fehler beim Laden der Statistiken: {e}")
    
    def _save_stats(self):
        """Speichert die Backup-Statistiken"""
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            logging.error(f"Fehler beim Speichern der Statistiken: {e}")
    
    def _ensure_backup_dir(self):
        """Stellt sicher, dass das Backup-Verzeichnis existiert"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
            logging.info(f"Backup-Verzeichnis erstellt: {self.backup_dir}")
    
    def create_backup(self, backup_type='daily'):
        """Erstellt ein neues Backup"""
        if not os.path.exists(self.db_path):
            logging.error(f"Datenbank nicht gefunden: {self.db_path}")
            return False
        
        timestamp = datetime.now()
        date_str = timestamp.strftime('%Y-%m-%d_%H-%M-%S')
        
        # Backup-Dateiname
        if backup_type == 'daily':
            filename = f"bess_daily_{date_str}"
        elif backup_type == 'weekly':
            filename = f"bess_weekly_{date_str}"
        elif backup_type == 'monthly':
            filename = f"bess_monthly_{date_str}"
        else:
            filename = f"bess_{backup_type}_{date_str}"
        
        backup_path = os.path.join(self.backup_dir, f"{filename}.sql")
        
        try:
            # SQL-Dump erstellen
            conn = sqlite3.connect(self.db_path)
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                for line in conn.iterdump():
                    f.write(f'{line}\n')
            
            conn.close()
            
            # Komprimierung
            if self.config['compression']:
                compressed_path = f"{backup_path}.gz"
                with open(backup_path, 'rb') as f_in:
                    with gzip.open(compressed_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # Original-Datei löschen
                os.remove(backup_path)
                backup_path = compressed_path
            
            # Statistiken aktualisieren
            file_size = os.path.getsize(backup_path)
            file_size_mb = file_size / (1024 * 1024)
            
            self.stats['total_backups'] += 1
            self.stats['successful_backups'] += 1
            self.stats['last_backup'] = timestamp.isoformat()
            self.stats['total_size_mb'] += file_size_mb
            
            self._save_stats()
            
            logging.info(f"✅ Backup erstellt: {backup_path} ({file_size_mb:.2f} MB)")
            
            # Backup-Rotation
            self._rotate_backups()
            
            # E-Mail-Benachrichtigung
            if self.config['email_notifications']:
                self._send_notification(f"Backup erfolgreich: {filename}", 
                                      f"Backup erstellt: {backup_path}\nGröße: {file_size_mb:.2f} MB")
            
            return True
            
        except Exception as e:
            logging.error(f"❌ Fehler beim Erstellen des Backups: {e}")
            
            self.stats['total_backups'] += 1
            self.stats['failed_backups'] += 1
            self._save_stats()
            
            if self.config['email_notifications']:
                self._send_notification(f"Backup fehlgeschlagen: {filename}", 
                                      f"Fehler: {str(e)}")
            
            return False
    
    def _rotate_backups(self):
        """Führt Backup-Rotation durch"""
        logging.info("🔄 Führe Backup-Rotation durch")
        
        # Alle Backup-Dateien auflisten
        backup_files = []
        for file in os.listdir(self.backup_dir):
            if file.endswith('.sql') or file.endswith('.sql.gz'):
                file_path = os.path.join(self.backup_dir, file)
                mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                backup_files.append((file_path, mod_time, file))
        
        # Nach Typ und Datum sortieren
        daily_backups = []
        weekly_backups = []
        monthly_backups = []
        
        for file_path, mod_time, filename in backup_files:
            if 'daily' in filename:
                daily_backups.append((file_path, mod_time))
            elif 'weekly' in filename:
                weekly_backups.append((file_path, mod_time))
            elif 'monthly' in filename:
                monthly_backups.append((file_path, mod_time))
        
        # Alte Backups löschen
        self._cleanup_backups(daily_backups, self.config['retention']['daily'], 'täglich')
        self._cleanup_backups(weekly_backups, self.config['retention']['weekly'], 'wöchentlich')
        self._cleanup_backups(monthly_backups, self.config['retention']['monthly'], 'monatlich')
    
    def _cleanup_backups(self, backups, max_count, backup_type):
        """Löscht alte Backups basierend auf Retention-Policy"""
        if len(backups) > max_count:
            # Nach Datum sortieren (älteste zuerst)
            backups.sort(key=lambda x: x[1])
            
            # Alte Backups löschen
            to_delete = backups[:-max_count]
            for file_path, mod_time in to_delete:
                try:
                    os.remove(file_path)
                    logging.info(f"🗑️  Altes {backup_type} Backup gelöscht: {os.path.basename(file_path)}")
                except Exception as e:
                    logging.error(f"Fehler beim Löschen von {file_path}: {e}")
    
    def _send_notification(self, subject, message):
        """Sendet E-Mail-Benachrichtigung"""
        if not self.config['email_notifications']:
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config['email_config']['username']
            msg['To'] = self.config['email_config']['to_email']
            msg['Subject'] = f"BESS Backup: {subject}"
            
            msg.attach(MIMEText(message, 'plain'))
            
            server = smtplib.SMTP(self.config['email_config']['smtp_server'], 
                                self.config['email_config']['smtp_port'])
            server.starttls()
            server.login(self.config['email_config']['username'], 
                        self.config['email_config']['password'])
            
            text = msg.as_string()
            server.sendmail(self.config['email_config']['username'], 
                          self.config['email_config']['to_email'], text)
            server.quit()
            
            logging.info("📧 E-Mail-Benachrichtigung gesendet")
            
        except Exception as e:
            logging.error(f"Fehler beim Senden der E-Mail-Benachrichtigung: {e}")
    
    def list_backups(self):
        """Listet alle verfügbaren Backups auf"""
        logging.info("📋 Verfügbare Backups:")
        
        if not os.path.exists(self.backup_dir):
            logging.info("Kein Backup-Verzeichnis gefunden")
            return
        
        backup_files = []
        for file in os.listdir(self.backup_dir):
            if file.endswith('.sql') or file.endswith('.sql.gz'):
                file_path = os.path.join(self.backup_dir, file)
                file_size = os.path.getsize(file_path)
                file_size_mb = file_size / (1024 * 1024)
                mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                backup_files.append((file, file_size_mb, mod_time))
        
        # Nach Datum sortieren (neueste zuerst)
        backup_files.sort(key=lambda x: x[2], reverse=True)
        
        for filename, size_mb, mod_time in backup_files:
            logging.info(f"   📄 {filename} ({size_mb:.2f} MB) - {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def get_backup_stats(self):
        """Gibt Backup-Statistiken zurück"""
        logging.info("📊 Backup-Statistiken:")
        logging.info(f"   Gesamte Backups: {self.stats['total_backups']}")
        logging.info(f"   Erfolgreiche Backups: {self.stats['successful_backups']}")
        logging.info(f"   Fehlgeschlagene Backups: {self.stats['failed_backups']}")
        logging.info(f"   Erfolgsrate: {(self.stats['successful_backups']/max(self.stats['total_backups'], 1)*100):.1f}%")
        logging.info(f"   Gesamtgröße: {self.stats['total_size_mb']:.2f} MB")
        
        if self.stats['last_backup']:
            last_backup = datetime.fromisoformat(self.stats['last_backup'])
            logging.info(f"   Letztes Backup: {last_backup.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def test_restore(self, backup_file):
        """Testet die Wiederherstellung eines Backups"""
        backup_path = os.path.join(self.backup_dir, backup_file)
        
        if not os.path.exists(backup_path):
            logging.error(f"Backup-Datei nicht gefunden: {backup_path}")
            return False
        
        test_db_path = 'instance/bess_test_restore.db'
        
        try:
            # Backup entpacken falls komprimiert
            if backup_path.endswith('.gz'):
                with gzip.open(backup_path, 'rb') as f_in:
                    with open(test_db_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                shutil.copy2(backup_path, test_db_path)
            
            # Test-Verbindung
            conn = sqlite3.connect(test_db_path)
            cursor = conn.cursor()
            
            # Tabellen auflisten
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            conn.close()
            
            # Test-Datenbank löschen
            os.remove(test_db_path)
            
            logging.info(f"✅ Wiederherstellungstest erfolgreich: {len(tables)} Tabellen gefunden")
            return True
            
        except Exception as e:
            logging.error(f"❌ Wiederherstellungstest fehlgeschlagen: {e}")
            if os.path.exists(test_db_path):
                os.remove(test_db_path)
            return False

def main():
    """Hauptfunktion"""
    backup_system = BackupAutomation()
    
    # Tägliches Backup erstellen
    logging.info("🚀 Starte automatisiertes Backup")
    
    success = backup_system.create_backup('daily')
    
    if success:
        logging.info("✅ Backup erfolgreich abgeschlossen")
    else:
        logging.error("❌ Backup fehlgeschlagen")
    
    # Statistiken anzeigen
    backup_system.get_backup_stats()
    
    # Backups auflisten
    backup_system.list_backups()

if __name__ == "__main__":
    main()
