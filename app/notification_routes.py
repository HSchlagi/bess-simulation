#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BESS-Simulation: Benachrichtigungs-Routes
Integration in die bestehende Flask-App
"""

import json
import logging
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, session, render_template, flash, redirect, url_for
from flask_socketio import emit, join_room, leave_room
from functools import wraps
import sqlite3
import os

# Logging konfigurieren
logger = logging.getLogger(__name__)

# Blueprint erstellen
notification_bp = Blueprint('notifications', __name__, url_prefix='/notifications')

def login_required(f):
    """Decorator für Login-Erforderlichkeit"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Nicht angemeldet'}), 401
        return f(*args, **kwargs)
    return decorated_function

def get_db_connection():
    """Datenbankverbindung abrufen"""
    conn = sqlite3.connect('instance/bess.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_user_email(user_id):
    """E-Mail-Adresse des Benutzers abrufen"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT email FROM user WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result['email'] if result else None
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der E-Mail-Adresse: {e}")
        return None

def send_notification_email(user_id, subject, message, notification_type='info'):
    """E-Mail-Benachrichtigung senden"""
    try:
        # E-Mail-Adresse des Benutzers abrufen
        user_email = get_user_email(user_id)
        if not user_email:
            logger.warning(f"Keine E-Mail-Adresse für Benutzer {user_id} gefunden")
            return False
        
        # E-Mail-Service importieren und verwenden
        from .email_service import email_service
        
        # HTML-Body erstellen
        html_body = f"""
        <!DOCTYPE html>
        <html lang="de">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>BESS-Simulation Benachrichtigung</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #3B82F6; color: white; padding: 20px; border-radius: 8px 8px 0 0; text-align: center; }}
                .content {{ background-color: #f5f5f5; padding: 20px; border-radius: 0 0 8px 8px; }}
                .footer {{ color: #666; font-size: 12px; margin-top: 30px; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔔 BESS-Simulation Benachrichtigung</h1>
            </div>
            <div class="content">
                <p>{message}</p>
            </div>
            <div class="footer">
                Diese E-Mail wurde automatisch von der BESS-Simulation generiert.
            </div>
        </body>
        </html>
        """
        
        # E-Mail senden
        success = email_service.send_notification(
            to_email=user_email,
            subject=subject,
            body=message,
            html_body=html_body
        )
        
        if success:
            logger.info(f"E-Mail-Benachrichtigung erfolgreich gesendet an {user_email}")
        else:
            logger.error(f"Fehler beim Senden der E-Mail-Benachrichtigung an {user_email}")
        
        return success
        
    except Exception as e:
        logger.error(f"Fehler beim Senden der E-Mail-Benachrichtigung: {e}")
        return False

@notification_bp.route('/')
@login_required
def notification_center():
    """Benachrichtigungs-Center anzeigen"""
    return render_template('notifications/center.html')

@notification_bp.route('/api/list')
@login_required
def get_notifications():
    """Benachrichtigungen abrufen"""
    try:
        user_id = session['user_id']
        limit = request.args.get('limit', 50, type=int)
        unread_only = request.args.get('unread_only', False, type=bool)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Benachrichtigungen abrufen
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
        
        # Ungelesene Anzahl
        cursor.execute('''
            SELECT COUNT(*) FROM notifications 
            WHERE user_id = ? AND read = FALSE 
            AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
        ''', (user_id,))
        unread_count = cursor.fetchone()[0]
        
        conn.close()
        
        # Daten formatieren
        notifications_data = []
        for n in notifications:
            notifications_data.append({
                'id': n['id'],
                'type': n['type'],
                'priority': n['priority'],
                'title': n['title'],
                'message': n['message'],
                'data': json.loads(n['data']) if n['data'] else {},
                'read': bool(n['read']),
                'created_at': n['created_at'],
                'sent_at': n['sent_at']
            })
        
        return jsonify({
            'success': True,
            'notifications': notifications_data,
            'unread_count': unread_count
        })
        
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Benachrichtigungen: {e}")
        return jsonify({'error': 'Fehler beim Abrufen der Benachrichtigungen'}), 500

@notification_bp.route('/api/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """Benachrichtigung als gelesen markieren"""
    try:
        user_id = session['user_id']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE notifications 
            SET read = TRUE 
            WHERE id = ? AND user_id = ?
        ''', (notification_id, user_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Benachrichtigung nicht gefunden'}), 404
            
    except Exception as e:
        logger.error(f"Fehler beim Markieren der Benachrichtigung: {e}")
        return jsonify({'error': 'Fehler beim Markieren der Benachrichtigung'}), 500

@notification_bp.route('/api/mark-all-read', methods=['POST'])
@login_required
def mark_all_read():
    """Alle Benachrichtigungen als gelesen markieren"""
    try:
        user_id = session['user_id']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE notifications 
            SET read = TRUE 
            WHERE user_id = ? AND read = FALSE
        ''', (user_id,))
        
        updated_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'updated_count': updated_count
        })
        
    except Exception as e:
        logger.error(f"Fehler beim Markieren aller Benachrichtigungen: {e}")
        return jsonify({'error': 'Fehler beim Markieren aller Benachrichtigungen'}), 500

@notification_bp.route('/settings')
@login_required
def notification_settings_page():
    """Benachrichtigungs-Einstellungen Seite"""
    return render_template('notifications/settings.html')

@notification_bp.route('/api/settings', methods=['GET', 'POST'])
@login_required
def notification_settings():
    """Benachrichtigungs-Einstellungen"""
    try:
        user_id = session['user_id']
        
        if request.method == 'GET':
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM notification_settings WHERE user_id = ?
            ''', (user_id,))
            settings = cursor.fetchone()
            conn.close()
            
            if settings:
                return jsonify({
                    'success': True,
                    'settings': {
                        'email_enabled': bool(settings['email_enabled']),
                        'push_enabled': bool(settings['push_enabled']),
                        'in_app_enabled': bool(settings['in_app_enabled']),
                        'email_frequency': settings['email_frequency'],
                        'quiet_hours_start': settings['quiet_hours_start'],
                        'quiet_hours_end': settings['quiet_hours_end'],
                        'notification_types': json.loads(settings['notification_types']) if settings['notification_types'] else []
                    }
                })
            else:
                # Standard-Einstellungen
                return jsonify({
                    'success': True,
                    'settings': {
                        'email_enabled': True,
                        'push_enabled': True,
                        'in_app_enabled': True,
                        'email_frequency': 'immediate',
                        'quiet_hours_start': None,
                        'quiet_hours_end': None,
                        'notification_types': []
                    }
                })
        
        else:  # POST
            data = request.get_json()
            
            conn = get_db_connection()
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
            
            flash('Benachrichtigungs-Einstellungen erfolgreich gespeichert!', 'success')
            return jsonify({'success': True})
            
    except Exception as e:
        logger.error(f"Fehler bei Benachrichtigungs-Einstellungen: {e}")
        return jsonify({'error': 'Fehler bei Benachrichtigungs-Einstellungen'}), 500

@notification_bp.route('/api/create', methods=['POST'])
@login_required
def create_notification():
    """Neue Benachrichtigung erstellen (für Tests)"""
    try:
        data = request.get_json()
        user_id = session['user_id']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Benachrichtigung erstellen
        cursor.execute('''
            INSERT INTO notifications 
            (user_id, type, priority, title, message, data, channels, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            data.get('type', 'system_alert'),
            data.get('priority', 'medium'),
            data.get('title', 'Test-Benachrichtigung'),
            data.get('message', 'Dies ist eine Test-Benachrichtigung'),
            json.dumps(data.get('data', {})),
            json.dumps(data.get('channels', ['in_app'])),
            datetime.now() + timedelta(hours=24)
        ))
        
        notification_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'notification_id': notification_id
        })
        
    except Exception as e:
        logger.error(f"Fehler beim Erstellen der Benachrichtigung: {e}")
        return jsonify({'error': 'Fehler beim Erstellen der Benachrichtigung'}), 500

@notification_bp.route('/api/unread-count')
@login_required
def get_unread_count():
    """Anzahl ungelesener Benachrichtigungen"""
    try:
        user_id = session['user_id']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM notifications 
            WHERE user_id = ? AND read = FALSE 
            AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
        ''', (user_id,))
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return jsonify({
            'success': True,
            'unread_count': count
        })
        
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der ungelesenen Anzahl: {e}")
        return jsonify({'error': 'Fehler beim Abrufen der ungelesenen Anzahl'}), 500

# WebSocket-Events für Real-time Updates
def register_notification_socketio(socketio):
    """WebSocket-Events für Benachrichtigungen registrieren"""
    
    @socketio.on('join_notifications')
    def on_join_notifications():
        """Benutzer zu Benachrichtigungs-Raum hinzufügen"""
        user_id = session.get('user_id')
        if user_id:
            join_room(f'user_{user_id}_notifications')
            emit('joined_notifications', {'room': f'user_{user_id}_notifications'})
            logger.info(f"Benutzer {user_id} ist Benachrichtigungs-Raum beigetreten")
    
    @socketio.on('leave_notifications')
    def on_leave_notifications():
        """Benutzer aus Benachrichtigungs-Raum entfernen"""
        user_id = session.get('user_id')
        if user_id:
            leave_room(f'user_{user_id}_notifications')
            emit('left_notifications', {'room': f'user_{user_id}_notifications'})
            logger.info(f"Benutzer {user_id} hat Benachrichtigungs-Raum verlassen")
    
    @socketio.on('request_notifications')
    def on_request_notifications():
        """Benachrichtigungen anfordern"""
        user_id = session.get('user_id')
        if user_id:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM notifications 
                    WHERE user_id = ? AND read = FALSE 
                    AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
                    ORDER BY created_at DESC LIMIT 10
                ''', (user_id,))
                
                notifications = cursor.fetchall()
                conn.close()
                
                notifications_data = []
                for n in notifications:
                    notifications_data.append({
                        'id': n['id'],
                        'type': n['type'],
                        'priority': n['priority'],
                        'title': n['title'],
                        'message': n['message'],
                        'data': json.loads(n['data']) if n['data'] else {},
                        'created_at': n['created_at']
                    })
                
                emit('notifications_update', {
                    'notifications': notifications_data,
                    'count': len(notifications_data)
                })
                
            except Exception as e:
                logger.error(f"Fehler beim Abrufen der Benachrichtigungen via WebSocket: {e}")
                emit('error', {'message': 'Fehler beim Abrufen der Benachrichtigungen'})

# Hilfsfunktionen für andere Module
def create_notification(user_id: int, notification_type: str, title: str, message: str, 
                       priority: str = 'medium', data: dict = None, channels: list = None):
    """Hilfsfunktion zum Erstellen von Benachrichtigungen"""
    try:
        if channels is None:
            channels = ['in_app', 'email']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO notifications 
            (user_id, type, priority, title, message, data, channels, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            notification_type,
            priority,
            title,
            message,
            json.dumps(data) if data else None,
            json.dumps(channels),
            datetime.now() + timedelta(hours=24)
        ))
        
        notification_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"Benachrichtigung {notification_id} für Benutzer {user_id} erstellt")
        return notification_id
        
    except Exception as e:
        logger.error(f"Fehler beim Erstellen der Benachrichtigung: {e}")
        return None

def send_simulation_complete_notification(user_id: int, project_name: str, results: dict):
    """Benachrichtigung für abgeschlossene Simulation"""
    title = f"🎉 Simulation abgeschlossen - {project_name}"
    message = f"Ihre BESS-Simulation für '{project_name}' wurde erfolgreich abgeschlossen."
    
    data = {
        'project_name': project_name,
        'total_capacity': results.get('total_capacity', 'N/A'),
        'profitability': results.get('profitability', 'N/A'),
        'co2_savings': results.get('co2_savings', 'N/A'),
        'dashboard_url': f"/dashboard?project={results.get('project_id', '')}"
    }
    
    return create_notification(
        user_id=user_id,
        notification_type='simulation_complete',
        title=title,
        message=message,
        priority='high',
        data=data,
        channels=['in_app', 'email']
    )

def send_system_alert_notification(user_id: int, alert_message: str, priority: str = 'medium'):
    """System-Alert Benachrichtigung"""
    title = "⚠️ System-Alert"
    message = alert_message
    
    return create_notification(
        user_id=user_id,
        notification_type='system_alert',
        title=title,
        message=message,
        priority=priority,
        channels=['in_app', 'email']
    )

def send_welcome_notification(user_id: int, user_name: str):
    """Willkommens-Benachrichtigung für neue Benutzer"""
    title = "👋 Willkommen bei der BESS-Simulation!"
    message = f"Willkommen {user_name}! Sie können jetzt BESS-Projekte erstellen und Simulationen durchführen."
    
    data = {
        'user_name': user_name,
        'dashboard_url': '/dashboard'
    }
    
    return create_notification(
        user_id=user_id,
        notification_type='user_welcome',
        title=title,
        message=message,
        priority='medium',
        data=data,
        channels=['in_app', 'email']
    )

@notification_bp.route('/api/test-email', methods=['POST'])
@login_required
def test_email_notification():
    """Test-E-Mail-Benachrichtigung senden"""
    try:
        data = request.get_json()
        user_id = session['user_id']
        
        subject = data.get('subject', '🔔 Test-Benachrichtigung - BESS-Simulation')
        message = data.get('message', 'Dies ist eine Test-E-Mail-Benachrichtigung von der BESS-Simulation.')
        
        # E-Mail senden
        success = send_notification_email(user_id, subject, message)
        
        if success:
            return jsonify({
                'success': True, 
                'message': 'Test-E-Mail erfolgreich gesendet',
                'user_email': get_user_email(user_id)
            })
        else:
            return jsonify({
                'success': False, 
                'message': 'Fehler beim Senden der Test-E-Mail'
            }), 500
        
    except Exception as e:
        logger.error(f"Fehler beim Senden der Test-E-Mail: {e}")
        return jsonify({'error': 'Fehler beim Senden der Test-E-Mail'}), 500
