#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BESS-Simulation: Benachrichtigungs-System Migration
Erstellt die notwendigen Datenbank-Tabellen für das Benachrichtigungs-System
"""

import sqlite3
import json
import os
from datetime import datetime

def migrate_notification_system():
    """Benachrichtigungs-System Datenbank-Migration"""
    
    db_path = 'instance/bess.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Datenbank nicht gefunden: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🚀 Starte Benachrichtigungs-System Migration...")
        
        # 1. Benachrichtigungen-Tabelle erstellen
        print("📋 Erstelle notifications-Tabelle...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
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
        
        # 2. Benachrichtigungs-Einstellungen-Tabelle erstellen
        print("⚙️ Erstelle notification_settings-Tabelle...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notification_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                email_enabled BOOLEAN DEFAULT TRUE,
                push_enabled BOOLEAN DEFAULT TRUE,
                in_app_enabled BOOLEAN DEFAULT TRUE,
                email_frequency VARCHAR(20) DEFAULT 'immediate',
                quiet_hours_start TIME,
                quiet_hours_end TIME,
                notification_types TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user (id)
            )
        ''')
        
        # 3. Benachrichtigungs-Templates-Tabelle erstellen
        print("📝 Erstelle notification_templates-Tabelle...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notification_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id VARCHAR(100) UNIQUE,
                type VARCHAR(50) NOT NULL,
                channel VARCHAR(20) NOT NULL,
                subject VARCHAR(255),
                body TEXT NOT NULL,
                html_body TEXT,
                variables TEXT,
                active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 4. Push-Subscriptions-Tabelle erstellen
        print("📱 Erstelle push_subscriptions-Tabelle...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS push_subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                endpoint TEXT NOT NULL,
                p256dh_key TEXT,
                auth_key TEXT,
                user_agent TEXT,
                active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user (id)
            )
        ''')
        
        # 5. Standard-Templates einfügen
        print("📄 Füge Standard-Templates ein...")
        templates = [
            {
                'template_id': 'simulation_complete_email',
                'type': 'simulation_complete',
                'channel': 'email',
                'subject': '🎉 BESS-Simulation abgeschlossen - {{project_name}}',
                'body': 'Ihre BESS-Simulation für das Projekt \'{{project_name}}\' wurde erfolgreich abgeschlossen.\n\nErgebnisse:\n- Gesamtkapazität: {{total_capacity}} kWh\n- Wirtschaftlichkeit: {{profitability}} €/Jahr\n- CO₂-Einsparung: {{co2_savings}} kg/Jahr\n\nSie können die Ergebnisse hier einsehen: {{dashboard_url}}',
                'html_body': '''
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #2E7D32;">🎉 BESS-Simulation abgeschlossen</h2>
                    <p>Ihre BESS-Simulation für das Projekt <strong>{{project_name}}</strong> wurde erfolgreich abgeschlossen.</p>
                    
                    <div style="background-color: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="color: #1976D2; margin-top: 0;">📊 Ergebnisse:</h3>
                        <ul>
                            <li><strong>Gesamtkapazität:</strong> {{total_capacity}} kWh</li>
                            <li><strong>Wirtschaftlichkeit:</strong> {{profitability}} €/Jahr</li>
                            <li><strong>CO₂-Einsparung:</strong> {{co2_savings}} kg/Jahr</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{{dashboard_url}}" style="background-color: #2E7D32; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">Ergebnisse ansehen</a>
                    </div>
                    
                    <p style="color: #666; font-size: 12px; margin-top: 30px;">
                        Diese E-Mail wurde automatisch von der BESS-Simulation generiert.
                    </p>
                </div>
                ''',
                'variables': json.dumps(['project_name', 'total_capacity', 'profitability', 'co2_savings', 'dashboard_url'])
            },
            {
                'template_id': 'system_alert_in_app',
                'type': 'system_alert',
                'channel': 'in_app',
                'subject': '⚠️ System-Alert',
                'body': 'System-Alert: {{alert_message}}',
                'html_body': None,
                'variables': json.dumps(['alert_message'])
            },
            {
                'template_id': 'user_welcome_email',
                'type': 'user_welcome',
                'channel': 'email',
                'subject': '👋 Willkommen bei der BESS-Simulation!',
                'body': 'Willkommen bei der BESS-Simulation, {{user_name}}!\n\nSie können jetzt:\n- BESS-Projekte erstellen\n- Simulationen durchführen\n- Ergebnisse analysieren\n\nDashboard: {{dashboard_url}}',
                'html_body': '''
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #2E7D32;">👋 Willkommen bei der BESS-Simulation!</h2>
                    <p>Hallo <strong>{{user_name}}</strong>,</p>
                    <p>herzlich willkommen bei der BESS-Simulation! Sie können jetzt:</p>
                    
                    <ul>
                        <li>🔋 BESS-Projekte erstellen</li>
                        <li>📊 Simulationen durchführen</li>
                        <li>📈 Ergebnisse analysieren</li>
                        <li>🤖 ML & KI Features nutzen</li>
                    </ul>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{{dashboard_url}}" style="background-color: #2E7D32; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">Zum Dashboard</a>
                    </div>
                </div>
                ''',
                'variables': json.dumps(['user_name', 'dashboard_url'])
            }
        ]
        
        for template in templates:
            cursor.execute('''
                INSERT OR REPLACE INTO notification_templates 
                (template_id, type, channel, subject, body, html_body, variables)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                template['template_id'],
                template['type'],
                template['channel'],
                template['subject'],
                template['body'],
                template['html_body'],
                template['variables']
            ))
        
        # 6. Indizes erstellen für bessere Performance
        print("🔍 Erstelle Indizes...")
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_notifications_type ON notifications(type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(read)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_notification_settings_user_id ON notification_settings(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_push_subscriptions_user_id ON push_subscriptions(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_push_subscriptions_active ON push_subscriptions(active)')
        
        # 7. Standard-Einstellungen für bestehende Benutzer erstellen
        print("👥 Erstelle Standard-Einstellungen für bestehende Benutzer...")
        try:
            cursor.execute('SELECT id FROM users')
            users = cursor.fetchall()
            
            for user in users:
                cursor.execute('''
                    INSERT OR IGNORE INTO notification_settings 
                    (user_id, email_enabled, push_enabled, in_app_enabled, email_frequency, notification_types)
                    VALUES (?, TRUE, TRUE, TRUE, 'immediate', ?)
                ''', (user[0], json.dumps(['simulation_complete', 'system_alert', 'user_welcome'])))
        except sqlite3.OperationalError:
            print("⚠️  users-Tabelle noch nicht vorhanden - Standard-Einstellungen werden bei der ersten Benutzer-Registrierung erstellt")
            users = []
        
        conn.commit()
        conn.close()
        
        print("✅ Benachrichtigungs-System Migration erfolgreich abgeschlossen!")
        print(f"📊 {len(users)} Benutzer mit Standard-Einstellungen konfiguriert")
        print(f"📄 {len(templates)} Standard-Templates erstellt")
        print("🔍 7 Performance-Indizes erstellt")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler bei der Migration: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

def test_notification_system():
    """Testet das Benachrichtigungs-System"""
    
    db_path = 'instance/bess.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🧪 Teste Benachrichtigungs-System...")
        
        # Test 1: Tabellen existieren
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'notification%'")
        tables = cursor.fetchall()
        print(f"✅ {len(tables)} Benachrichtigungs-Tabellen gefunden: {[t[0] for t in tables]}")
        
        # Test 2: Templates vorhanden
        cursor.execute("SELECT COUNT(*) FROM notification_templates")
        template_count = cursor.fetchone()[0]
        print(f"✅ {template_count} Benachrichtigungs-Templates vorhanden")
        
        # Test 3: Benutzer-Einstellungen
        cursor.execute("SELECT COUNT(*) FROM notification_settings")
        settings_count = cursor.fetchone()[0]
        print(f"✅ {settings_count} Benutzer-Einstellungen konfiguriert")
        
        # Test 4: Test-Benachrichtigung erstellen
        cursor.execute("SELECT id FROM users LIMIT 1")
        user = cursor.fetchone()
        
        if user:
            cursor.execute('''
                INSERT INTO notifications 
                (user_id, type, priority, title, message, data, channels, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user[0],
                'system_alert',
                'medium',
                '🧪 Test-Benachrichtigung',
                'Dies ist eine Test-Benachrichtigung für das Benachrichtigungs-System.',
                json.dumps({'test': True, 'timestamp': datetime.now().isoformat()}),
                json.dumps(['in_app']),
                datetime.now().replace(hour=23, minute=59, second=59)
            ))
            
            notification_id = cursor.lastrowid
            conn.commit()
            
            print(f"✅ Test-Benachrichtigung erstellt (ID: {notification_id})")
            
            # Test-Benachrichtigung wieder löschen
            cursor.execute("DELETE FROM notifications WHERE id = ?", (notification_id,))
            conn.commit()
            print("✅ Test-Benachrichtigung wieder gelöscht")
        
        conn.close()
        print("🎉 Alle Tests erfolgreich!")
        return True
        
    except Exception as e:
        print(f"❌ Test fehlgeschlagen: {e}")
        if conn:
            conn.close()
        return False

if __name__ == "__main__":
    print("🚀 BESS-Simulation: Benachrichtigungs-System Migration")
    print("=" * 60)
    
    # Migration durchführen
    if migrate_notification_system():
        print("\n" + "=" * 60)
        # Tests durchführen
        test_notification_system()
    else:
        print("❌ Migration fehlgeschlagen!")
    
    print("\n🎯 Nächste Schritte:")
    print("1. Server neu starten")
    print("2. Benachrichtigungs-Center testen: /notifications")
    print("3. E-Mail-Einstellungen konfigurieren (optional)")
    print("4. Push-Notifications aktivieren (optional)")
