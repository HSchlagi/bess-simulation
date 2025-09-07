#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BESS-Simulation: E-Mail-Service
SMTP-Integration für Benachrichtigungen
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Dict, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class EmailService:
    """E-Mail-Service für Benachrichtigungen"""
    
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.username = os.getenv('SMTP_USERNAME')
        self.password = os.getenv('SMTP_PASSWORD')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@bess-simulation.at')
        self.from_name = os.getenv('FROM_NAME', 'BESS-Simulation')
        
        # Testen ob E-Mail konfiguriert ist
        self.is_configured = bool(self.username and self.password)
        
        if not self.is_configured:
            logger.warning("E-Mail-Service nicht konfiguriert - SMTP-Credentials fehlen")
    
    def send_notification(self, to_email: str, subject: str, body: str, 
                         html_body: str = None, attachments: List[str] = None) -> bool:
        """Benachrichtigungs-E-Mail senden"""
        
        if not self.is_configured:
            logger.info(f"E-Mail-Service nicht konfiguriert - Demo-Modus: {subject}")
            return True  # Demo-Modus: Erfolg simulieren
        
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
            
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
                    if os.path.exists(file_path):
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
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"E-Mail erfolgreich gesendet an {to_email}: {subject}")
            return True
                
        except Exception as e:
            logger.error(f"Fehler beim Senden der E-Mail an {to_email}: {e}")
            return False
    
    def send_simulation_complete_email(self, to_email: str, project_name: str, results: Dict) -> bool:
        """E-Mail für abgeschlossene Simulation"""
        
        subject = f"🎉 BESS-Simulation abgeschlossen - {project_name}"
        
        # Text-Version
        body = f"""Hallo,

Ihre BESS-Simulation für das Projekt '{project_name}' wurde erfolgreich abgeschlossen.

Ergebnisse:
- Gesamtkapazität: {results.get('total_capacity', 'N/A')} kWh
- Wirtschaftlichkeit: {results.get('profitability', 'N/A')} €/Jahr
- CO₂-Einsparung: {results.get('co2_savings', 'N/A')} kg/Jahr

Sie können die Ergebnisse hier einsehen: {results.get('dashboard_url', '/dashboard')}

Mit freundlichen Grüßen,
Ihr BESS-Simulation Team
"""
        
        # HTML-Version
        html_body = f"""
        <!DOCTYPE html>
        <html lang="de">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>BESS-Simulation abgeschlossen</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #2E7D32; color: white; padding: 20px; border-radius: 8px 8px 0 0; text-align: center; }}
                .content {{ background-color: #f5f5f5; padding: 20px; border-radius: 0 0 8px 8px; }}
                .results {{ background-color: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .button {{ background-color: #2E7D32; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; margin: 20px 0; }}
                .footer {{ color: #666; font-size: 12px; margin-top: 30px; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎉 BESS-Simulation abgeschlossen</h1>
            </div>
            <div class="content">
                <p>Hallo,</p>
                <p>Ihre BESS-Simulation für das Projekt <strong>{project_name}</strong> wurde erfolgreich abgeschlossen.</p>
                
                <div class="results">
                    <h3 style="color: #1976D2; margin-top: 0;">📊 Ergebnisse:</h3>
                    <ul>
                        <li><strong>Gesamtkapazität:</strong> {results.get('total_capacity', 'N/A')} kWh</li>
                        <li><strong>Wirtschaftlichkeit:</strong> {results.get('profitability', 'N/A')} €/Jahr</li>
                        <li><strong>CO₂-Einsparung:</strong> {results.get('co2_savings', 'N/A')} kg/Jahr</li>
                    </ul>
                </div>
                
                <div style="text-align: center;">
                    <a href="{results.get('dashboard_url', '/dashboard')}" class="button">Ergebnisse ansehen</a>
                </div>
                
                <p>Mit freundlichen Grüßen,<br>Ihr BESS-Simulation Team</p>
            </div>
            <div class="footer">
                Diese E-Mail wurde automatisch von der BESS-Simulation generiert.
            </div>
        </body>
        </html>
        """
        
        return self.send_notification(to_email, subject, body, html_body)
    
    def send_welcome_email(self, to_email: str, user_name: str) -> bool:
        """Willkommens-E-Mail für neue Benutzer"""
        
        subject = "👋 Willkommen bei der BESS-Simulation!"
        
        # Text-Version
        body = f"""Hallo {user_name},

herzlich willkommen bei der BESS-Simulation!

Sie können jetzt:
- BESS-Projekte erstellen
- Simulationen durchführen
- Ergebnisse analysieren
- ML & KI Features nutzen

Dashboard: /dashboard

Mit freundlichen Grüßen,
Ihr BESS-Simulation Team
"""
        
        # HTML-Version
        html_body = f"""
        <!DOCTYPE html>
        <html lang="de">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Willkommen bei der BESS-Simulation</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #2E7D32; color: white; padding: 20px; border-radius: 8px 8px 0 0; text-align: center; }}
                .content {{ background-color: #f5f5f5; padding: 20px; border-radius: 0 0 8px 8px; }}
                .features {{ background-color: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .button {{ background-color: #2E7D32; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; margin: 20px 0; }}
                .footer {{ color: #666; font-size: 12px; margin-top: 30px; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>👋 Willkommen bei der BESS-Simulation!</h1>
            </div>
            <div class="content">
                <p>Hallo <strong>{user_name}</strong>,</p>
                <p>herzlich willkommen bei der BESS-Simulation! Sie können jetzt:</p>
                
                <div class="features">
                    <ul>
                        <li>🔋 BESS-Projekte erstellen</li>
                        <li>📊 Simulationen durchführen</li>
                        <li>📈 Ergebnisse analysieren</li>
                        <li>🤖 ML & KI Features nutzen</li>
                    </ul>
                </div>
                
                <div style="text-align: center;">
                    <a href="/dashboard" class="button">Zum Dashboard</a>
                </div>
                
                <p>Mit freundlichen Grüßen,<br>Ihr BESS-Simulation Team</p>
            </div>
            <div class="footer">
                Diese E-Mail wurde automatisch von der BESS-Simulation generiert.
            </div>
        </body>
        </html>
        """
        
        return self.send_notification(to_email, subject, body, html_body)
    
    def send_system_alert_email(self, to_email: str, alert_message: str, priority: str = 'medium') -> bool:
        """System-Alert E-Mail"""
        
        priority_emojis = {
            'high': '🚨',
            'medium': '⚠️',
            'low': 'ℹ️'
        }
        
        emoji = priority_emojis.get(priority, '⚠️')
        subject = f"{emoji} System-Alert - BESS-Simulation"
        
        # Text-Version
        body = f"""Hallo,

es gibt einen System-Alert in der BESS-Simulation:

{alert_message}

Bitte überprüfen Sie das System.

Mit freundlichen Grüßen,
Ihr BESS-Simulation Team
"""
        
        # HTML-Version
        html_body = f"""
        <!DOCTYPE html>
        <html lang="de">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>System-Alert</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #EF4444; color: white; padding: 20px; border-radius: 8px 8px 0 0; text-align: center; }}
                .content {{ background-color: #f5f5f5; padding: 20px; border-radius: 0 0 8px 8px; }}
                .alert {{ background-color: #FEF2F2; border: 1px solid #FECACA; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .footer {{ color: #666; font-size: 12px; margin-top: 30px; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{emoji} System-Alert</h1>
            </div>
            <div class="content">
                <p>Hallo,</p>
                <p>es gibt einen System-Alert in der BESS-Simulation:</p>
                
                <div class="alert">
                    <p><strong>{alert_message}</strong></p>
                </div>
                
                <p>Bitte überprüfen Sie das System.</p>
                
                <p>Mit freundlichen Grüßen,<br>Ihr BESS-Simulation Team</p>
            </div>
            <div class="footer">
                Diese E-Mail wurde automatisch von der BESS-Simulation generiert.
            </div>
        </body>
        </html>
        """
        
        return self.send_notification(to_email, subject, body, html_body)
    
    def test_connection(self) -> Dict[str, any]:
        """SMTP-Verbindung testen"""
        
        if not self.is_configured:
            return {
                'success': False,
                'message': 'E-Mail-Service nicht konfiguriert',
                'configured': False
            }
        
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            server.quit()
            
            return {
                'success': True,
                'message': 'SMTP-Verbindung erfolgreich',
                'configured': True,
                'server': self.smtp_server,
                'port': self.smtp_port,
                'username': self.username
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'SMTP-Verbindung fehlgeschlagen: {e}',
                'configured': True,
                'error': str(e)
            }

# Globale Instanz
email_service = EmailService()

# Hilfsfunktionen
def send_notification_email(to_email: str, subject: str, body: str, html_body: str = None) -> bool:
    """Hilfsfunktion zum Senden von Benachrichtigungs-E-Mails"""
    return email_service.send_notification(to_email, subject, body, html_body)

def send_simulation_complete_email(to_email: str, project_name: str, results: Dict) -> bool:
    """Hilfsfunktion für Simulation-abgeschlossen E-Mails"""
    return email_service.send_simulation_complete_email(to_email, project_name, results)

def send_welcome_email(to_email: str, user_name: str) -> bool:
    """Hilfsfunktion für Willkommens-E-Mails"""
    return email_service.send_welcome_email(to_email, user_name)

def send_system_alert_email(to_email: str, alert_message: str, priority: str = 'medium') -> bool:
    """Hilfsfunktion für System-Alert E-Mails"""
    return email_service.send_system_alert_email(to_email, alert_message, priority)

def test_email_connection() -> Dict[str, any]:
    """Hilfsfunktion zum Testen der E-Mail-Verbindung"""
    return email_service.test_connection()
