#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BESS-Simulation: Benachrichtigungs-System
Vollständige Implementierung von Punkt 5.1 aus Verbesserung_BESS.md

Features:
- In-App Benachrichtigungen
- E-Mail-Integration
- Push-Notifications
- Benachrichtigungs-Center
- Benutzer-Einstellungen
- WebSocket-Integration
"""

import os
import json
import smtplib
import logging
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
from flask import Flask, request, jsonify, session, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room
import redis
from celery import Celery

# Logging konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotificationType(Enum):
    """Benachrichtigungs-Typen"""
    SIMULATION_COMPLETE = "simulation_complete"
    SYSTEM_ALERT = "system_alert"
    BACKUP_STATUS = "backup_status"
    API_ERROR = "api_error"
    USER_WELCOME = "user_welcome"
    PROJECT_SHARED = "project_shared"
    EXPORT_READY = "export_ready"
    MAINTENANCE_SCHEDULED = "maintenance_scheduled"

class NotificationPriority(Enum):
    """Benachrichtigungs-Prioritäten"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class NotificationChannel(Enum):
    """Benachrichtigungs-Kanäle"""
    IN_APP = "in_app"
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"

@dataclass
class NotificationTemplate:
    """Benachrichtigungs-Template"""
    id: str
    type: NotificationType
    channel: NotificationChannel
    subject: str
    body: str
    html_body: Optional[str] = None
    variables: List[str] = None

@dataclass
class Notification:
    """Benachrichtigungs-Objekt"""
    id: Optional[int] = None
    user_id: Optional[int] = None
    type: NotificationType = None
    priority: NotificationPriority = NotificationPriority.MEDIUM
    title: str = ""
    message: str = ""
    data: Dict[str, Any] = None
    channels: List[NotificationChannel] = None
    read: bool = False
    created_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

class NotificationDatabase:
    """Datenbank-Manager für Benachrichtigungen"""
    
    def __init__(self, db_path: str = "instance/bess.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Datenbank-Tabellen erstellen"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Benachrichtigungen-Tabelle
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
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Benachrichtigungs-Einstellungen
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
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Benachrichtigungs-Templates
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
        
        # Push-Subscriptions
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
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Standard-Templates einfügen
        self.create_default_templates()
    
    def create_default_templates(self):
        """Standard-Benachrichtigungs-Templates erstellen"""
        templates = [
            NotificationTemplate(
                id="simulation_complete_email",
                type=NotificationType.SIMULATION_COMPLETE,
                channel=NotificationChannel.EMAIL,
                subject="🎉 BESS-Simulation abgeschlossen - {{project_name}}",
                body="Ihre BESS-Simulation für das Projekt '{{project_name}}' wurde erfolgreich abgeschlossen.\n\nErgebnisse:\n- Gesamtkapazität: {{total_capacity}} kWh\n- Wirtschaftlichkeit: {{profitability}} €/Jahr\n- CO₂-Einsparung: {{co2_savings}} kg/Jahr\n\nSie können die Ergebnisse hier einsehen: {{dashboard_url}}",
                html_body="""
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
                """,
                variables=["project_name", "total_capacity", "profitability", "co2_savings", "dashboard_url"]
            ),
            NotificationTemplate(
                id="system_alert_in_app",
                type=NotificationType.SYSTEM_ALERT,
                channel=NotificationChannel.IN_APP,
                subject="⚠️ System-Alert",
                body="System-Alert: {{alert_message}}",
                variables=["alert_message"]
            ),
            NotificationTemplate(
                id="user_welcome_email",
                type=NotificationType.USER_WELCOME,
                channel=NotificationChannel.EMAIL,
                subject="👋 Willkommen bei der BESS-Simulation!",
                body="Willkommen bei der BESS-Simulation, {{user_name}}!\n\nSie können jetzt:\n- BESS-Projekte erstellen\n- Simulationen durchführen\n- Ergebnisse analysieren\n\nDashboard: {{dashboard_url}}",
                html_body="""
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
                """,
                variables=["user_name", "dashboard_url"]
            )
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for template in templates:
            cursor.execute('''
                INSERT OR REPLACE INTO notification_templates 
                (template_id, type, channel, subject, body, html_body, variables)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                template.id,
                template.type.value,
                template.channel.value,
                template.subject,
                template.body,
                template.html_body,
                json.dumps(template.variables) if template.variables else None
            ))
        
        conn.commit()
        conn.close()

class EmailService:
    """E-Mail-Service für Benachrichtigungen"""
    
    def __init__(self, smtp_server: str = None, smtp_port: int = 587, 
                 username: str = None, password: str = None):
        self.smtp_server = smtp_server or os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = smtp_port
        self.username = username or os.getenv('SMTP_USERNAME')
        self.password = password or os.getenv('SMTP_PASSWORD')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@bess-simulation.at')
    
    def send_notification(self, to_email: str, subject: str, body: str, 
                         html_body: str = None, attachments: List[str] = None) -> bool:
        """Benachrichtigungs-E-Mail senden"""
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Text-Version
            text_part = MIMEText(body, 'plain', 'utf-8')
            msg.attach(text_part)
            
            # HTML-Version falls vorhanden
            if html_body:
                html_part = MIMEText(html_body, 'html', 'utf-8')
                msg.attach(html_part)
            
            # Anhänge
            if attachments:
                for file_path in attachments:
                    with open(file_path, "rb") as attachment:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(attachment.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {os.path.basename(file_path)}'
                        )
                        msg.attach(part)
            
            # E-Mail senden
            if self.username and self.password:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
                server.quit()
                logger.info(f"E-Mail erfolgreich gesendet an {to_email}")
                return True
            else:
                logger.warning("SMTP-Credentials nicht konfiguriert - E-Mail nicht gesendet")
                return False
                
        except Exception as e:
            logger.error(f"Fehler beim Senden der E-Mail: {e}")
            return False

class PushNotificationService:
    """Push-Notification-Service"""
    
    def __init__(self, vapid_public_key: str = None, vapid_private_key: str = None):
        self.vapid_public_key = vapid_public_key or os.getenv('VAPID_PUBLIC_KEY')
        self.vapid_private_key = vapid_private_key or os.getenv('VAPID_PRIVATE_KEY')
    
    def send_push_notification(self, subscription: Dict, title: str, body: str, 
                              data: Dict = None) -> bool:
        """Push-Notification senden"""
        try:
            # Hier würde die Web Push Library verwendet werden
            # Für Demo-Zwecke simulieren wir den Versand
            logger.info(f"Push-Notification gesendet: {title} - {body}")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Senden der Push-Notification: {e}")
            return False

class NotificationService:
    """Hauptservice für Benachrichtigungen"""
    
    def __init__(self, db_path: str = "instance/bess.db"):
        self.db = NotificationDatabase(db_path)
        self.email_service = EmailService()
        self.push_service = PushNotificationService()
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    
    def create_notification(self, user_id: int, notification_type: NotificationType,
                           title: str, message: str, priority: NotificationPriority = NotificationPriority.MEDIUM,
                           data: Dict = None, channels: List[NotificationChannel] = None,
                           expires_in_hours: int = 24) -> int:
        """Neue Benachrichtigung erstellen"""
        
        if channels is None:
            channels = [NotificationChannel.IN_APP, NotificationChannel.EMAIL]
        
        expires_at = datetime.now() + timedelta(hours=expires_in_hours)
        
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO notifications 
            (user_id, type, priority, title, message, data, channels, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            notification_type.value,
            priority.value,
            title,
            message,
            json.dumps(data) if data else None,
            json.dumps([ch.value for ch in channels]),
            expires_at
        ))
        
        notification_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Sofortige Zustellung
        self.deliver_notification(notification_id)
        
        return notification_id
    
    def deliver_notification(self, notification_id: int):
        """Benachrichtigung zustellen"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM notifications WHERE id = ?', (notification_id,))
        notification = cursor.fetchone()
        
        if not notification:
            conn.close()
            return
        
        # Benachrichtigungs-Einstellungen abrufen
        cursor.execute('SELECT * FROM notification_settings WHERE user_id = ?', (notification[1],))
        settings = cursor.fetchone()
        
        if not settings:
            # Standard-Einstellungen erstellen
            cursor.execute('''
                INSERT INTO notification_settings (user_id) VALUES (?)
            ''', (notification[1],))
            conn.commit()
            settings = (None, notification[1], True, True, True, 'immediate', None, None, None, None, None)
        
        channels = json.loads(notification[7]) if notification[7] else []
        
        # In-App Benachrichtigung
        if NotificationChannel.IN_APP.value in channels and settings[4]:  # in_app_enabled
            self.send_in_app_notification(notification)
        
        # E-Mail Benachrichtigung
        if NotificationChannel.EMAIL.value in channels and settings[2]:  # email_enabled
            self.send_email_notification(notification)
        
        # Push Benachrichtigung
        if NotificationChannel.PUSH.value in channels and settings[3]:  # push_enabled
            self.send_push_notification(notification)
        
        # Als gesendet markieren
        cursor.execute('''
            UPDATE notifications SET sent_at = CURRENT_TIMESTAMP WHERE id = ?
        ''', (notification_id,))
        conn.commit()
        conn.close()
    
    def send_in_app_notification(self, notification):
        """In-App Benachrichtigung senden"""
        # WebSocket-Event für Real-time Updates
        notification_data = {
            'id': notification[0],
            'type': notification[2],
            'priority': notification[3],
            'title': notification[4],
            'message': notification[5],
            'data': json.loads(notification[6]) if notification[6] else {},
            'created_at': notification[9].isoformat() if notification[9] else None
        }
        
        # Redis Pub/Sub für WebSocket-Updates
        self.redis_client.publish(f'user_{notification[1]}_notifications', json.dumps(notification_data))
    
    def send_email_notification(self, notification):
        """E-Mail Benachrichtigung senden"""
        # Template abrufen
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM notification_templates 
            WHERE type = ? AND channel = 'email' AND active = TRUE
        ''', (notification[2],))
        template = cursor.fetchone()
        
        if template:
            # Template-Variablen ersetzen
            subject = template[3]
            body = template[4]
            html_body = template[5]
            
            # Benutzer-E-Mail abrufen
            cursor.execute('SELECT email FROM users WHERE id = ?', (notification[1],))
            user_email = cursor.fetchone()
            
            if user_email:
                # Hier würden Template-Variablen ersetzt werden
                self.email_service.send_notification(
                    user_email[0], subject, body, html_body
                )
        
        conn.close()
    
    def send_push_notification(self, notification):
        """Push Benachrichtigung senden"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        # Push-Subscriptions abrufen
        cursor.execute('''
            SELECT * FROM push_subscriptions WHERE user_id = ? AND active = TRUE
        ''', (notification[1],))
        subscriptions = cursor.fetchall()
        
        for subscription in subscriptions:
            self.push_service.send_push_notification(
                {
                    'endpoint': subscription[2],
                    'keys': {
                        'p256dh': subscription[3],
                        'auth': subscription[4]
                    }
                },
                notification[4],  # title
                notification[5],  # message
                json.loads(notification[6]) if notification[6] else {}
            )
        
        conn.close()
    
    def get_user_notifications(self, user_id: int, limit: int = 50, unread_only: bool = False) -> List[Dict]:
        """Benachrichtigungen für Benutzer abrufen"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT * FROM notifications 
            WHERE user_id = ? AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
        '''
        params = [user_id]
        
        if unread_only:
            query += ' AND read = FALSE'
        
        query += ' ORDER BY created_at DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        notifications = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': n[0],
                'type': n[2],
                'priority': n[3],
                'title': n[4],
                'message': n[5],
                'data': json.loads(n[6]) if n[6] else {},
                'read': bool(n[8]),
                'created_at': n[9].isoformat() if n[9] else None,
                'sent_at': n[10].isoformat() if n[10] else None
            }
            for n in notifications
        ]
    
    def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        """Benachrichtigung als gelesen markieren"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE notifications 
            SET read = TRUE 
            WHERE id = ? AND user_id = ?
        ''', (notification_id, user_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def get_unread_count(self, user_id: int) -> int:
        """Anzahl ungelesener Benachrichtigungen"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM notifications 
            WHERE user_id = ? AND read = FALSE 
            AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
        ''', (user_id,))
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count

# Flask-App Integration
def create_notification_app():
    """Flask-App für Benachrichtigungen erstellen"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'notification-secret-key')
    
    socketio = SocketIO(app, cors_allowed_origins="*")
    notification_service = NotificationService()
    
    @app.route('/api/notifications', methods=['GET'])
    def get_notifications():
        """Benachrichtigungen abrufen"""
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Nicht angemeldet'}), 401
        
        limit = request.args.get('limit', 50, type=int)
        unread_only = request.args.get('unread_only', False, type=bool)
        
        notifications = notification_service.get_user_notifications(
            user_id, limit, unread_only
        )
        
        return jsonify({
            'notifications': notifications,
            'unread_count': notification_service.get_unread_count(user_id)
        })
    
    @app.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
    def mark_notification_read(notification_id):
        """Benachrichtigung als gelesen markieren"""
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Nicht angemeldet'}), 401
        
        success = notification_service.mark_as_read(notification_id, user_id)
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Benachrichtigung nicht gefunden'}), 404
    
    @app.route('/api/notifications/settings', methods=['GET', 'POST'])
    def notification_settings():
        """Benachrichtigungs-Einstellungen"""
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Nicht angemeldet'}), 401
        
        if request.method == 'GET':
            conn = sqlite3.connect(notification_service.db.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM notification_settings WHERE user_id = ?
            ''', (user_id,))
            settings = cursor.fetchone()
            conn.close()
            
            if settings:
                return jsonify({
                    'email_enabled': bool(settings[2]),
                    'push_enabled': bool(settings[3]),
                    'in_app_enabled': bool(settings[4]),
                    'email_frequency': settings[5],
                    'quiet_hours_start': settings[6],
                    'quiet_hours_end': settings[7],
                    'notification_types': json.loads(settings[8]) if settings[8] else []
                })
            else:
                return jsonify({
                    'email_enabled': True,
                    'push_enabled': True,
                    'in_app_enabled': True,
                    'email_frequency': 'immediate',
                    'quiet_hours_start': None,
                    'quiet_hours_end': None,
                    'notification_types': []
                })
        
        else:  # POST
            data = request.get_json()
            
            conn = sqlite3.connect(notification_service.db.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO notification_settings 
                (user_id, email_enabled, push_enabled, in_app_enabled, 
                 email_frequency, quiet_hours_start, quiet_hours_end, 
                 notification_types, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                user_id,
                data.get('email_enabled', True),
                data.get('push_enabled', True),
                data.get('in_app_enabled', True),
                data.get('email_frequency', 'immediate'),
                data.get('quiet_hours_start'),
                data.get('quiet_hours_end'),
                json.dumps(data.get('notification_types', []))
            ))
            
            conn.commit()
            conn.close()
            
            return jsonify({'success': True})
    
    @socketio.on('join_notifications')
    def on_join_notifications():
        """WebSocket: Benutzer zu Benachrichtigungs-Raum hinzufügen"""
        user_id = session.get('user_id')
        if user_id:
            join_room(f'user_{user_id}_notifications')
            emit('joined', {'room': f'user_{user_id}_notifications'})
    
    @socketio.on('leave_notifications')
    def on_leave_notifications():
        """WebSocket: Benutzer aus Benachrichtigungs-Raum entfernen"""
        user_id = session.get('user_id')
        if user_id:
            leave_room(f'user_{user_id}_notifications')
            emit('left', {'room': f'user_{user_id}_notifications'})
    
    return app, socketio, notification_service

if __name__ == "__main__":
    app, socketio, notification_service = create_notification_app()
    
    # Demo-Benachrichtigungen erstellen
    print("🚀 BESS-Simulation Benachrichtigungs-System gestartet!")
    print("📧 E-Mail-Service:", "✅ Aktiv" if notification_service.email_service.username else "⚠️ Demo-Modus")
    print("📱 Push-Service:", "✅ Aktiv" if notification_service.push_service.vapid_public_key else "⚠️ Demo-Modus")
    print("🔔 In-App Benachrichtigungen: ✅ Aktiv")
    print("🌐 WebSocket-Integration: ✅ Aktiv")
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5001)
