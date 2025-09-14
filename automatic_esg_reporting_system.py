#!/usr/bin/env python3
"""
Automatic ESG Reporting System für BESS-Simulation
Automatische Generierung und Versendung von ESG-Berichten
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import json
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import schedule
import time
import threading
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging
from jinja2 import Template

# Import der bestehenden Systeme
from enhanced_esg_reporting_system import EnhancedESGReportingSystem
from carbon_credit_trading_system import CarbonCreditTradingSystem
from green_finance_integration import GreenFinanceIntegration

@dataclass
class ESGReportSchedule:
    """ESG-Report Zeitplan Datenstruktur"""
    id: Optional[int]
    project_id: int
    report_type: str  # 'daily', 'weekly', 'monthly', 'quarterly', 'yearly'
    schedule_time: str  # HH:MM Format
    recipient_email: str
    is_active: bool
    last_sent: Optional[datetime]
    next_scheduled: datetime
    created_at: datetime

class AutomaticESGReportingSystem:
    """Automatisches ESG-Reporting System"""
    
    def __init__(self, db_path: str = "instance/bess.db"):
        self.db_path = db_path
        self.esg_system = EnhancedESGReportingSystem(db_path)
        self.carbon_trading = CarbonCreditTradingSystem(db_path)
        self.green_finance = GreenFinanceIntegration(db_path)
        
        # E-Mail Konfiguration
        self.email_config = {
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', 587)),
            'username': os.getenv('SMTP_USERNAME', ''),
            'password': os.getenv('SMTP_PASSWORD', ''),
            'from_email': os.getenv('FROM_EMAIL', 'esg-reports@bess-simulation.com')
        }
        
        # Logging Setup
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/automatic_esg_reporting.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Scheduler Thread
        self.scheduler_thread = None
        self.is_running = False
        
        # Report Templates
        self.email_templates = {
            'daily': self._get_daily_email_template(),
            'weekly': self._get_weekly_email_template(),
            'monthly': self._get_monthly_email_template(),
            'quarterly': self._get_quarterly_email_template(),
            'yearly': self._get_yearly_email_template()
        }
    
    def create_automatic_reporting_tables(self):
        """Erstellt Tabellen für automatisches ESG-Reporting"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # ESG Report Schedules Tabelle
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS esg_report_schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            report_type VARCHAR(20) NOT NULL,
            schedule_time VARCHAR(5) NOT NULL, -- HH:MM
            recipient_email VARCHAR(255) NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            last_sent TIMESTAMP,
            next_scheduled TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES project (id)
        )
        ''')
        
        # ESG Report History Tabelle
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS esg_report_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            schedule_id INTEGER NOT NULL,
            project_id INTEGER NOT NULL,
            report_type VARCHAR(20) NOT NULL,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            recipient_email VARCHAR(255) NOT NULL,
            status VARCHAR(20) DEFAULT 'sent', -- 'sent', 'failed', 'pending'
            error_message TEXT,
            report_data TEXT, -- JSON
            FOREIGN KEY (schedule_id) REFERENCES esg_report_schedules (id),
            FOREIGN KEY (project_id) REFERENCES project (id)
        )
        ''')
        
        # ESG Report Notifications Tabelle
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS esg_report_notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            notification_type VARCHAR(50) NOT NULL, -- 'threshold_alert', 'performance_alert', 'milestone'
            threshold_value REAL,
            current_value REAL,
            message TEXT NOT NULL,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(20) DEFAULT 'sent',
            FOREIGN KEY (project_id) REFERENCES project (id)
        )
        ''')
        
        # Indizes erstellen
        indices = [
            "CREATE INDEX IF NOT EXISTS idx_esg_schedules_project ON esg_report_schedules(project_id, is_active)",
            "CREATE INDEX IF NOT EXISTS idx_esg_schedules_next ON esg_report_schedules(next_scheduled, is_active)",
            "CREATE INDEX IF NOT EXISTS idx_esg_history_project ON esg_report_history(project_id, sent_at)",
            "CREATE INDEX IF NOT EXISTS idx_esg_notifications_project ON esg_report_notifications(project_id, sent_at)"
        ]
        
        for index_sql in indices:
            cursor.execute(index_sql)
        
        conn.commit()
        conn.close()
        self.logger.info("✅ Automatic ESG Reporting Tabellen erfolgreich erstellt")
    
    def schedule_esg_report(self, project_id: int, report_type: str, 
                          schedule_time: str, recipient_email: str) -> bool:
        """Plant ESG-Report Zeitplan"""
        try:
            # Nächste Ausführungszeit berechnen
            next_scheduled = self._calculate_next_scheduled_time(report_type, schedule_time)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO esg_report_schedules 
            (project_id, report_type, schedule_time, recipient_email, next_scheduled)
            VALUES (?, ?, ?, ?, ?)
            ''', (project_id, report_type, schedule_time, recipient_email, next_scheduled))
            
            schedule_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            self.logger.info(f"✅ ESG-Report Zeitplan erstellt: Projekt {project_id}, {report_type} um {schedule_time}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Erstellen des ESG-Report Zeitplans: {e}")
            return False
    
    def _calculate_next_scheduled_time(self, report_type: str, schedule_time: str) -> datetime:
        """Berechnet nächste geplante Ausführungszeit"""
        now = datetime.now()
        hour, minute = map(int, schedule_time.split(':'))
        
        if report_type == 'daily':
            next_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_time <= now:
                next_time += timedelta(days=1)
                
        elif report_type == 'weekly':
            # Montag um die gegebene Zeit
            days_ahead = 0 - now.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            next_time = now + timedelta(days=days_ahead)
            next_time = next_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
        elif report_type == 'monthly':
            # Erster Tag des nächsten Monats
            if now.month == 12:
                next_month = now.replace(year=now.year + 1, month=1, day=1)
            else:
                next_month = now.replace(month=now.month + 1, day=1)
            next_time = next_month.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
        elif report_type == 'quarterly':
            # Erster Tag des nächsten Quartals
            current_quarter = (now.month - 1) // 3 + 1
            if current_quarter == 4:
                next_quarter_month = 1
                next_year = now.year + 1
            else:
                next_quarter_month = current_quarter * 3 + 1
                next_year = now.year
            next_time = now.replace(year=next_year, month=next_quarter_month, day=1, 
                                  hour=hour, minute=minute, second=0, microsecond=0)
            
        elif report_type == 'yearly':
            # 1. Januar des nächsten Jahres
            next_time = now.replace(year=now.year + 1, month=1, day=1, 
                                  hour=hour, minute=minute, second=0, microsecond=0)
        
        return next_time
    
    def generate_and_send_esg_report(self, schedule_id: int) -> bool:
        """Generiert und sendet ESG-Report"""
        try:
            # Schedule-Details abrufen
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT project_id, report_type, recipient_email 
            FROM esg_report_schedules WHERE id = ?
            ''', (schedule_id,))
            
            schedule_data = cursor.fetchone()
            if not schedule_data:
                self.logger.error(f"❌ Schedule {schedule_id} nicht gefunden")
                return False
            
            project_id, report_type, recipient_email = schedule_data
            
            # ESG-Report generieren
            self.logger.info(f"🔄 Generiere {report_type} ESG-Report für Projekt {project_id}")
            esg_report = self.esg_system.generate_comprehensive_esg_report(project_id, report_type)
            
            # HTML-Report generieren
            html_content = self.esg_system.generate_html_report(esg_report)
            
            # Report als Datei speichern
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"esg_report_{esg_report.project_name}_{report_type}_{timestamp}.html"
            filepath = os.path.join('reports', filename)
            
            os.makedirs('reports', exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # E-Mail senden
            success = self._send_esg_report_email(esg_report, recipient_email, filepath)
            
            # Report History speichern
            cursor.execute('''
            INSERT INTO esg_report_history 
            (schedule_id, project_id, report_type, recipient_email, status, report_data)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                schedule_id, project_id, report_type, recipient_email,
                'sent' if success else 'failed',
                json.dumps({
                    'esg_score': esg_report.overall_esg_score,
                    'environmental_score': esg_report.environmental_score,
                    'social_score': esg_report.social_score,
                    'governance_score': esg_report.governance_score,
                    'sustainability_rating': esg_report.sustainability_rating
                })
            ))
            
            # Next Scheduled Time aktualisieren
            if success:
                next_scheduled = self._calculate_next_scheduled_time(report_type, 
                    cursor.execute('SELECT schedule_time FROM esg_report_schedules WHERE id = ?', (schedule_id,)).fetchone()[0])
                cursor.execute('''
                UPDATE esg_report_schedules 
                SET last_sent = CURRENT_TIMESTAMP, next_scheduled = ?
                WHERE id = ?
                ''', (next_scheduled, schedule_id))
            
            conn.commit()
            conn.close()
            
            if success:
                self.logger.info(f"✅ ESG-Report erfolgreich gesendet an {recipient_email}")
            else:
                self.logger.error(f"❌ Fehler beim Senden des ESG-Reports an {recipient_email}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Generieren/Senden des ESG-Reports: {e}")
            return False
    
    def _send_esg_report_email(self, esg_report, recipient_email: str, 
                              attachment_path: str) -> bool:
        """Sendet ESG-Report per E-Mail"""
        try:
            if not self.email_config['username'] or not self.email_config['password']:
                self.logger.warning("⚠️ E-Mail-Konfiguration nicht vollständig")
                return False
            
            # E-Mail Template auswählen
            template = self.email_templates.get(esg_report.report_type, self.email_templates['monthly'])
            
            # E-Mail erstellen
            msg = MIMEMultipart()
            msg['From'] = self.email_config['from_email']
            msg['To'] = recipient_email
            msg['Subject'] = template['subject'].format(
                project_name=esg_report.project_name,
                report_type=esg_report.report_type.title(),
                esg_score=esg_report.overall_esg_score
            )
            
            # E-Mail Body
            body = template['body'].format(
                project_name=esg_report.project_name,
                report_type=esg_report.report_type,
                period_start=esg_report.period_start,
                period_end=esg_report.period_end,
                overall_esg_score=esg_report.overall_esg_score,
                environmental_score=esg_report.environmental_score,
                social_score=esg_report.social_score,
                governance_score=esg_report.governance_score,
                sustainability_rating=esg_report.sustainability_rating,
                carbon_credits_generated=esg_report.carbon_credits_generated,
                carbon_credits_sold=esg_report.carbon_credits_sold,
                carbon_credits_revenue_eur=esg_report.carbon_credits_revenue_eur,
                green_finance_value_eur=esg_report.green_finance_value_eur
            )
            
            msg.attach(MIMEText(body, 'html', 'utf-8'))
            
            # HTML-Anhang hinzufügen
            if os.path.exists(attachment_path):
                with open(attachment_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {os.path.basename(attachment_path)}'
                )
                msg.attach(part)
            
            # E-Mail senden
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['username'], self.email_config['password'])
            text = msg.as_string()
            server.sendmail(self.email_config['from_email'], recipient_email, text)
            server.quit()
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Senden der E-Mail: {e}")
            return False
    
    def _get_daily_email_template(self) -> Dict:
        """Tägliches E-Mail Template"""
        return {
            'subject': '📊 Täglicher ESG-Report: {project_name} - ESG Score: {esg_score}',
            'body': '''
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">
                        🌱 Täglicher ESG-Report
                    </h2>
                    
                    <p>Hallo,</p>
                    
                    <p>hier ist Ihr täglicher ESG-Report für <strong>{project_name}</strong>:</p>
                    
                    <div style="background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="color: #2c3e50; margin-top: 0;">📈 ESG-Übersicht</h3>
                        <ul>
                            <li><strong>Overall ESG Score:</strong> {overall_esg_score}/100</li>
                            <li><strong>Environmental Score:</strong> {environmental_score}/100</li>
                            <li><strong>Social Score:</strong> {social_score}/100</li>
                            <li><strong>Governance Score:</strong> {governance_score}/100</li>
                            <li><strong>Sustainability Rating:</strong> {sustainability_rating}</li>
                        </ul>
                    </div>
                    
                    <div style="background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="color: #27ae60; margin-top: 0;">💰 Erlöse</h3>
                        <ul>
                            <li><strong>Carbon Credits Generiert:</strong> {carbon_credits_generated}</li>
                            <li><strong>Carbon Credits Verkauft:</strong> {carbon_credits_sold}</li>
                            <li><strong>Carbon Credit Erlöse:</strong> {carbon_credits_revenue_eur:,.0f} EUR</li>
                            <li><strong>Green Finance Portfolio:</strong> {green_finance_value_eur:,.0f} EUR</li>
                        </ul>
                    </div>
                    
                    <p>Den vollständigen Report finden Sie im Anhang.</p>
                    
                    <p>Mit freundlichen Grüßen,<br>
                    BESS-Simulation ESG-Reporting System</p>
                </div>
            </body>
            </html>
            '''
        }
    
    def _get_weekly_email_template(self) -> Dict:
        """Wöchentliches E-Mail Template"""
        return {
            'subject': '📊 Wöchentlicher ESG-Report: {project_name} - ESG Score: {esg_score}',
            'body': '''
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">
                        📅 Wöchentlicher ESG-Report
                    </h2>
                    
                    <p>Hallo,</p>
                    
                    <p>hier ist Ihr wöchentlicher ESG-Report für <strong>{project_name}</strong> 
                    für die Woche vom {period_start} bis {period_end}:</p>
                    
                    <div style="background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="color: #2c3e50; margin-top: 0;">📈 ESG-Performance</h3>
                        <ul>
                            <li><strong>Overall ESG Score:</strong> {overall_esg_score}/100</li>
                            <li><strong>Environmental Score:</strong> {environmental_score}/100</li>
                            <li><strong>Social Score:</strong> {social_score}/100</li>
                            <li><strong>Governance Score:</strong> {governance_score}/100</li>
                            <li><strong>Sustainability Rating:</strong> {sustainability_rating}</li>
                        </ul>
                    </div>
                    
                    <div style="background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="color: #27ae60; margin-top: 0;">💰 Wöchentliche Erlöse</h3>
                        <ul>
                            <li><strong>Carbon Credits Generiert:</strong> {carbon_credits_generated}</li>
                            <li><strong>Carbon Credits Verkauft:</strong> {carbon_credits_sold}</li>
                            <li><strong>Carbon Credit Erlöse:</strong> {carbon_credits_revenue_eur:,.0f} EUR</li>
                            <li><strong>Green Finance Portfolio:</strong> {green_finance_value_eur:,.0f} EUR</li>
                        </ul>
                    </div>
                    
                    <p>Den vollständigen Report finden Sie im Anhang.</p>
                    
                    <p>Mit freundlichen Grüßen,<br>
                    BESS-Simulation ESG-Reporting System</p>
                </div>
            </body>
            </html>
            '''
        }
    
    def _get_monthly_email_template(self) -> Dict:
        """Monatliches E-Mail Template"""
        return {
            'subject': '📊 Monatlicher ESG-Report: {project_name} - ESG Score: {esg_score}',
            'body': '''
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">
                        📆 Monatlicher ESG-Report
                    </h2>
                    
                    <p>Hallo,</p>
                    
                    <p>hier ist Ihr monatlicher ESG-Report für <strong>{project_name}</strong> 
                    für den Monat {period_start} bis {period_end}:</p>
                    
                    <div style="background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="color: #2c3e50; margin-top: 0;">📈 ESG-Performance</h3>
                        <ul>
                            <li><strong>Overall ESG Score:</strong> {overall_esg_score}/100</li>
                            <li><strong>Environmental Score:</strong> {environmental_score}/100</li>
                            <li><strong>Social Score:</strong> {social_score}/100</li>
                            <li><strong>Governance Score:</strong> {governance_score}/100</li>
                            <li><strong>Sustainability Rating:</strong> {sustainability_rating}</li>
                        </ul>
                    </div>
                    
                    <div style="background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="color: #27ae60; margin-top: 0;">💰 Monatliche Erlöse</h3>
                        <ul>
                            <li><strong>Carbon Credits Generiert:</strong> {carbon_credits_generated}</li>
                            <li><strong>Carbon Credits Verkauft:</strong> {carbon_credits_sold}</li>
                            <li><strong>Carbon Credit Erlöse:</strong> {carbon_credits_revenue_eur:,.0f} EUR</li>
                            <li><strong>Green Finance Portfolio:</strong> {green_finance_value_eur:,.0f} EUR</li>
                        </ul>
                    </div>
                    
                    <p>Den vollständigen Report finden Sie im Anhang.</p>
                    
                    <p>Mit freundlichen Grüßen,<br>
                    BESS-Simulation ESG-Reporting System</p>
                </div>
            </body>
            </html>
            '''
        }
    
    def _get_quarterly_email_template(self) -> Dict:
        """Quartalsweise E-Mail Template"""
        return {
            'subject': '📊 Quartalsbericht ESG: {project_name} - ESG Score: {esg_score}',
            'body': '''
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">
                        📊 Quartalsbericht ESG
                    </h2>
                    
                    <p>Hallo,</p>
                    
                    <p>hier ist Ihr Quartalsbericht für <strong>{project_name}</strong> 
                    für das Quartal {period_start} bis {period_end}:</p>
                    
                    <div style="background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="color: #2c3e50; margin-top: 0;">📈 ESG-Performance</h3>
                        <ul>
                            <li><strong>Overall ESG Score:</strong> {overall_esg_score}/100</li>
                            <li><strong>Environmental Score:</strong> {environmental_score}/100</li>
                            <li><strong>Social Score:</strong> {social_score}/100</li>
                            <li><strong>Governance Score:</strong> {governance_score}/100</li>
                            <li><strong>Sustainability Rating:</strong> {sustainability_rating}</li>
                        </ul>
                    </div>
                    
                    <div style="background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="color: #27ae60; margin-top: 0;">💰 Quartals-Erlöse</h3>
                        <ul>
                            <li><strong>Carbon Credits Generiert:</strong> {carbon_credits_generated}</li>
                            <li><strong>Carbon Credits Verkauft:</strong> {carbon_credits_sold}</li>
                            <li><strong>Carbon Credit Erlöse:</strong> {carbon_credits_revenue_eur:,.0f} EUR</li>
                            <li><strong>Green Finance Portfolio:</strong> {green_finance_value_eur:,.0f} EUR</li>
                        </ul>
                    </div>
                    
                    <p>Den vollständigen Report finden Sie im Anhang.</p>
                    
                    <p>Mit freundlichen Grüßen,<br>
                    BESS-Simulation ESG-Reporting System</p>
                </div>
            </body>
            </html>
            '''
        }
    
    def _get_yearly_email_template(self) -> Dict:
        """Jährliches E-Mail Template"""
        return {
            'subject': '📊 Jahresbericht ESG: {project_name} - ESG Score: {esg_score}',
            'body': '''
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">
                        📊 Jahresbericht ESG
                    </h2>
                    
                    <p>Hallo,</p>
                    
                    <p>hier ist Ihr Jahresbericht für <strong>{project_name}</strong> 
                    für das Jahr {period_start} bis {period_end}:</p>
                    
                    <div style="background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="color: #2c3e50; margin-top: 0;">📈 ESG-Performance</h3>
                        <ul>
                            <li><strong>Overall ESG Score:</strong> {overall_esg_score}/100</li>
                            <li><strong>Environmental Score:</strong> {environmental_score}/100</li>
                            <li><strong>Social Score:</strong> {social_score}/100</li>
                            <li><strong>Governance Score:</strong> {governance_score}/100</li>
                            <li><strong>Sustainability Rating:</strong> {sustainability_rating}</li>
                        </ul>
                    </div>
                    
                    <div style="background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="color: #27ae60; margin-top: 0;">💰 Jahres-Erlöse</h3>
                        <ul>
                            <li><strong>Carbon Credits Generiert:</strong> {carbon_credits_generated}</li>
                            <li><strong>Carbon Credits Verkauft:</strong> {carbon_credits_sold}</li>
                            <li><strong>Carbon Credit Erlöse:</strong> {carbon_credits_revenue_eur:,.0f} EUR</li>
                            <li><strong>Green Finance Portfolio:</strong> {green_finance_value_eur:,.0f} EUR</li>
                        </ul>
                    </div>
                    
                    <p>Den vollständigen Report finden Sie im Anhang.</p>
                    
                    <p>Mit freundlichen Grüßen,<br>
                    BESS-Simulation ESG-Reporting System</p>
                </div>
            </body>
            </html>
            '''
        }
    
    def setup_automatic_scheduler(self):
        """Richtet automatischen Scheduler ein"""
        try:
            # Alle aktiven Schedules abrufen
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT id, project_id, report_type, schedule_time, recipient_email
            FROM esg_report_schedules WHERE is_active = TRUE
            ''')
            
            schedules = cursor.fetchall()
            conn.close()
            
            # Schedule für jeden Report einrichten
            for schedule_data in schedules:
                schedule_id, project_id, report_type, schedule_time, recipient_email = schedule_data
                
                # Schedule-Funktion erstellen
                def create_schedule_function(sched_id):
                    return lambda: self.generate_and_send_esg_report(sched_id)
                
                # Schedule einrichten
                if report_type == 'daily':
                    schedule.every().day.at(schedule_time).do(create_schedule_function(schedule_id))
                elif report_type == 'weekly':
                    schedule.every().monday.at(schedule_time).do(create_schedule_function(schedule_id))
                elif report_type == 'monthly':
                    schedule.every().month.do(create_schedule_function(schedule_id))
                elif report_type == 'quarterly':
                    schedule.every().quarter.do(create_schedule_function(schedule_id))
                elif report_type == 'yearly':
                    schedule.every().year.do(create_schedule_function(schedule_id))
                
                self.logger.info(f"✅ Schedule eingerichtet: {report_type} um {schedule_time} für Projekt {project_id}")
            
            # Scheduler Thread starten
            if not self.is_running:
                self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
                self.scheduler_thread.start()
                self.is_running = True
                self.logger.info("✅ Automatic ESG Reporting Scheduler gestartet")
            
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Einrichten des Schedulers: {e}")
    
    def _run_scheduler(self):
        """Führt den Scheduler aus"""
        self.logger.info("🔄 ESG Reporting Scheduler läuft...")
        
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Alle 60 Sekunden prüfen
            except Exception as e:
                self.logger.error(f"❌ Fehler im Scheduler: {e}")
                time.sleep(60)
    
    def stop_scheduler(self):
        """Stoppt den Scheduler"""
        self.is_running = False
        self.logger.info("⏹️ ESG Reporting Scheduler gestoppt")
    
    def get_report_history(self, project_id: int, limit: int = 10) -> List[Dict]:
        """Ruft Report-Historie ab"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = '''
            SELECT h.sent_at, h.report_type, h.recipient_email, h.status, h.report_data
            FROM esg_report_history h
            WHERE h.project_id = ?
            ORDER BY h.sent_at DESC
            LIMIT ?
            '''
            
            df = pd.read_sql_query(query, conn, params=(project_id, limit))
            conn.close()
            
            return df.to_dict('records')
            
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Abrufen der Report-Historie: {e}")
            return []
    
    def get_active_schedules(self, project_id: Optional[int] = None) -> List[Dict]:
        """Ruft aktive Schedules ab"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            if project_id:
                query = '''
                SELECT id, project_id, report_type, schedule_time, recipient_email, 
                       last_sent, next_scheduled, created_at
                FROM esg_report_schedules 
                WHERE is_active = TRUE AND project_id = ?
                ORDER BY next_scheduled
                '''
                df = pd.read_sql_query(query, conn, params=(project_id,))
            else:
                query = '''
                SELECT id, project_id, report_type, schedule_time, recipient_email, 
                       last_sent, next_scheduled, created_at
                FROM esg_report_schedules 
                WHERE is_active = TRUE
                ORDER BY next_scheduled
                '''
                df = pd.read_sql_query(query, conn)
            
            conn.close()
            return df.to_dict('records')
            
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Abrufen der aktiven Schedules: {e}")
            return []

def main():
    """Hauptfunktion für Automatic ESG Reporting System"""
    print("🤖 Automatic ESG Reporting System für BESS-Simulation")
    print("=" * 60)
    
    # System initialisieren
    reporting_system = AutomaticESGReportingSystem()
    
    # Tabellen erstellen
    reporting_system.create_automatic_reporting_tables()
    
    print("✅ Automatic ESG Reporting System erfolgreich initialisiert")
    print("📊 Features:")
    print("   - Automatische ESG-Report Generierung")
    print("   - Flexible Zeitplanung (täglich, wöchentlich, monatlich, etc.)")
    print("   - E-Mail-Versand mit HTML-Reports")
    print("   - Report-Historie Tracking")
    print("   - Scheduler-System")
    print("   - Benutzerdefinierte E-Mail Templates")
    print("📧 E-Mail Templates verfügbar:")
    for report_type in ['daily', 'weekly', 'monthly', 'quarterly', 'yearly']:
        print(f"   - {report_type.title()} Reports")

if __name__ == '__main__':
    main()
