#!/usr/bin/env python3
"""
HETZNER SERVER UPDATE - Migration-Skript
Führt alle notwendigen Datenbank-Migrationen für das Benachrichtigungs-System durch
"""

import sqlite3
import os
import sys
from datetime import datetime

def run_migration():
    """Führt die Benachrichtigungs-System Migration auf dem Hetzner-Server durch"""
    
    print("🚀 HETZNER SERVER UPDATE - Benachrichtigungs-System Migration")
    print("=" * 60)
    
    # Datenbankpfad prüfen
    db_path = '/opt/bess-simulation/instance/bess.db'
    if not os.path.exists(db_path):
        print(f"❌ Datenbank nicht gefunden: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("📋 Prüfe bestehende Tabellen...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%notification%'")
        existing_tables = [row[0] for row in cursor.fetchall()]
        print(f"✅ Gefundene Benachrichtigungs-Tabellen: {existing_tables}")
        
        # Benachrichtigungs-Tabellen erstellen (falls nicht vorhanden)
        if 'notifications' not in existing_tables:
            print("📋 Erstelle notifications-Tabelle...")
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                type VARCHAR(50) NOT NULL,
                priority VARCHAR(20) DEFAULT 'medium',
                title VARCHAR(255) NOT NULL,
                message TEXT NOT NULL,
                data TEXT,
                channels TEXT,
                read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sent_at TIMESTAMP,
                expires_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user (id)
            )
            ''')
        
        if 'notification_settings' not in existing_tables:
            print("⚙️ Erstelle notification_settings-Tabelle...")
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS notification_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                email_enabled BOOLEAN DEFAULT TRUE,
                push_enabled BOOLEAN DEFAULT FALSE,
                in_app_enabled BOOLEAN DEFAULT TRUE,
                email_frequency VARCHAR(20) DEFAULT 'immediate',
                quiet_hours_start TIME,
                quiet_hours_end TIME,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user (id)
            )
            ''')
        
        if 'notification_templates' not in existing_tables:
            print("📝 Erstelle notification_templates-Tabelle...")
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS notification_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL UNIQUE,
                type VARCHAR(50) NOT NULL,
                subject_template TEXT NOT NULL,
                message_template TEXT NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
        
        # Standard-Templates einfügen
        print("📄 Füge Standard-Templates ein...")
        templates = [
            ('simulation_complete', 'success', 'Simulation abgeschlossen', 'Ihre BESS-Simulation wurde erfolgreich abgeschlossen.'),
            ('system_alert', 'warning', 'System-Warnung', 'Es wurde eine System-Warnung erkannt.'),
            ('welcome', 'info', 'Willkommen bei BESS Simulation', 'Willkommen im BESS-Simulation System!')
        ]
        
        for name, type_, subject, message in templates:
            cursor.execute('''
            INSERT OR IGNORE INTO notification_templates (name, type, subject_template, message_template)
            VALUES (?, ?, ?, ?)
            ''', (name, type_, subject, message))
        
        # Indizes erstellen
        print("🔍 Erstelle Performance-Indizes...")
        indices = [
            "CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(read)",
            "CREATE INDEX IF NOT EXISTS idx_notifications_type ON notifications(type)",
            "CREATE INDEX IF NOT EXISTS idx_notification_settings_user_id ON notification_settings(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_notification_templates_name ON notification_templates(name)",
            "CREATE INDEX IF NOT EXISTS idx_notification_templates_type ON notification_templates(type)"
        ]
        
        for index_sql in indices:
            cursor.execute(index_sql)
        
        # Standard-Einstellungen für bestehende Benutzer
        print("👥 Erstelle Standard-Einstellungen für bestehende Benutzer...")
        try:
            cursor.execute("SELECT id FROM user")
            user_ids = [row[0] for row in cursor.fetchall()]
            
            for user_id in user_ids:
                cursor.execute('''
                INSERT OR IGNORE INTO notification_settings (user_id, email_enabled, push_enabled, in_app_enabled)
                VALUES (?, TRUE, FALSE, TRUE)
                ''', (user_id,))
            
            print(f"✅ {len(user_ids)} Benutzer mit Standard-Einstellungen konfiguriert")
        except sqlite3.OperationalError as e:
            print(f"⚠️  user-Tabelle noch nicht vorhanden - Standard-Einstellungen werden bei der ersten Benutzer-Registrierung erstellt")
        
        conn.commit()
        print("✅ Benachrichtigungs-System Migration erfolgreich abgeschlossen!")
        
        # Test der Migration
        print("\n🧪 Teste Migration...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%notification%'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"✅ {len(tables)} Benachrichtigungs-Tabellen gefunden: {tables}")
        
        cursor.execute("SELECT COUNT(*) FROM notification_templates")
        template_count = cursor.fetchone()[0]
        print(f"✅ {template_count} Benachrichtigungs-Templates vorhanden")
        
        cursor.execute("SELECT COUNT(*) FROM notification_settings")
        settings_count = cursor.fetchone()[0]
        print(f"✅ {settings_count} Benutzer-Einstellungen konfiguriert")
        
        conn.close()
        
        print("\n🎯 Nächste Schritte:")
        print("1. Server neu starten: sudo systemctl restart bess")
        print("2. Benachrichtigungs-Center testen: /notifications")
        print("3. E-Mail-Einstellungen konfigurieren (optional)")
        print("4. Push-Notifications aktivieren (optional)")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler bei der Migration: {e}")
        return False

if __name__ == '__main__':
    success = run_migration()
    sys.exit(0 if success else 1)
