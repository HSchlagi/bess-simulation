#!/usr/bin/env python3
"""
Enhanced ESG-Reporting System für BESS-Simulation
Erweiterte ESG-Reports mit Carbon Credits, Green Finance und automatischen Berichten
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List, Optional
from dataclasses import dataclass
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import schedule
import time
from jinja2 import Template

# Carbon Credit Trading System importieren
from carbon_credit_trading_system import CarbonCreditTradingSystem
from co2_tracking_system import CO2TrackingSystem

@dataclass
class ESGReport:
    """ESG-Report Datenstruktur"""
    project_id: int
    project_name: str
    report_type: str
    period_start: str
    period_end: str
    environmental_score: float
    social_score: float
    governance_score: float
    overall_esg_score: float
    carbon_credits_generated: int
    carbon_credits_sold: int
    carbon_credits_revenue_eur: float
    green_finance_value_eur: float
    sustainability_rating: str
    compliance_status: str
    report_data: Dict

class EnhancedESGReportingSystem:
    """Erweitertes ESG-Reporting System mit Carbon Credits und Green Finance"""
    
    def __init__(self, db_path: str = "instance/bess.db"):
        self.db_path = db_path
        self.co2_system = CO2TrackingSystem(db_path)
        self.carbon_trading = CarbonCreditTradingSystem(db_path)
        
        # ESG-Report Templates
        self.report_templates = {
            'monthly': 'monthly_esg_report.html',
            'quarterly': 'quarterly_esg_report.html',
            'yearly': 'yearly_esg_report.html'
        }
        
        # E-Mail Konfiguration
        self.email_config = {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'username': '',  # TODO: Konfigurieren
            'password': '',  # TODO: Konfigurieren
            'from_email': 'esg-reports@bess-simulation.com'
        }
    
    def generate_comprehensive_esg_report(self, project_id: int, 
                                        report_type: str = 'monthly') -> ESGReport:
        """Generiert umfassenden ESG-Report mit Carbon Credits und Green Finance"""
        
        # Projekt-Details abrufen
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM project WHERE id = ?', (project_id,))
        project_result = cursor.fetchone()
        project_name = project_result[0] if project_result else f"Projekt {project_id}"
        conn.close()
        
        # Zeitraum bestimmen
        end_date = datetime.now().date()
        if report_type == 'monthly':
            start_date = end_date.replace(day=1)
        elif report_type == 'quarterly':
            quarter = (end_date.month - 1) // 3 + 1
            start_date = end_date.replace(month=(quarter - 1) * 3 + 1, day=1)
        elif report_type == 'yearly':
            start_date = end_date.replace(month=1, day=1)
        else:
            start_date = end_date - timedelta(days=30)
        
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        # 1. CO₂-Tracking Daten abrufen
        co2_metrics = self.co2_system.generate_sustainability_metrics(
            project_id, start_date_str, end_date_str, report_type
        )
        
        # 2. Carbon Credit Daten abrufen
        carbon_credit_revenue = self.carbon_trading.calculate_carbon_credit_revenue(
            project_id, start_date_str, end_date_str
        )
        
        # 3. Green Finance Portfolio abrufen
        green_finance_portfolio = self.carbon_trading.get_green_finance_portfolio(project_id)
        
        # 4. ESG Performance Tracking aktualisieren
        esg_performance = self.carbon_trading.update_esg_performance(
            project_id, start_date_str, end_date_str
        )
        
        # 5. Erweiterte ESG-Scores berechnen
        environmental_score = self._calculate_enhanced_environmental_score(
            co2_metrics, carbon_credit_revenue, esg_performance
        )
        
        social_score = self._calculate_enhanced_social_score(
            co2_metrics, green_finance_portfolio, esg_performance
        )
        
        governance_score = self._calculate_enhanced_governance_score(
            esg_performance, green_finance_portfolio
        )
        
        overall_esg_score = (
            environmental_score * 0.4 + 
            social_score * 0.3 + 
            governance_score * 0.3
        )
        
        # Sustainability Rating bestimmen
        sustainability_rating = self._determine_sustainability_rating(overall_esg_score)
        
        # Comprehensive Report Data
        report_data = {
            'co2_metrics': co2_metrics,
            'carbon_credit_revenue': carbon_credit_revenue,
            'green_finance_portfolio': green_finance_portfolio,
            'esg_performance': esg_performance,
            'environmental_breakdown': self._get_environmental_breakdown(co2_metrics, carbon_credit_revenue),
            'social_breakdown': self._get_social_breakdown(co2_metrics, green_finance_portfolio),
            'governance_breakdown': self._get_governance_breakdown(esg_performance),
            'recommendations': self._generate_recommendations(overall_esg_score, esg_performance)
        }
        
        esg_report = ESGReport(
            project_id=project_id,
            project_name=project_name,
            report_type=report_type,
            period_start=start_date_str,
            period_end=end_date_str,
            environmental_score=round(environmental_score, 1),
            social_score=round(social_score, 1),
            governance_score=round(governance_score, 1),
            overall_esg_score=round(overall_esg_score, 1),
            carbon_credits_generated=esg_performance['carbon_credits_generated'],
            carbon_credits_sold=esg_performance['carbon_credits_sold'],
            carbon_credits_revenue_eur=carbon_credit_revenue['actual_revenue_eur'],
            green_finance_value_eur=green_finance_portfolio['total_value_eur'],
            sustainability_rating=sustainability_rating,
            compliance_status=esg_performance['compliance_status'],
            report_data=report_data
        )
        
        return esg_report
    
    def _calculate_enhanced_environmental_score(self, co2_metrics: Dict, 
                                              carbon_credit_revenue: Dict,
                                              esg_performance: Dict) -> float:
        """Berechnet erweiterten Environmental Score"""
        
        # Basis CO₂-Score (0-60 Punkte)
        co2_saved_kg = co2_metrics.get('co2_saved_total_kg', 0)
        co2_score = min(60, max(0, (co2_saved_kg / 1000) * 10))  # 1 tCO₂ = 10 Punkte, max 60
        
        # Erneuerbare Energie Score (0-20 Punkte)
        renewable_share = co2_metrics.get('renewable_share_percent', 0)
        renewable_score = min(20, max(0, renewable_share * 0.2))  # 100% = 20 Punkte
        
        # Carbon Credit Aktivität Score (0-20 Punkte)
        carbon_credit_score = 0
        if carbon_credit_revenue['actual_revenue_eur'] > 0:
            carbon_credit_score = min(20, max(0, 
                (carbon_credit_revenue['revenue_utilization_percent'] / 100) * 20
            ))
        
        return co2_score + renewable_score + carbon_credit_score
    
    def _calculate_enhanced_social_score(self, co2_metrics: Dict,
                                       green_finance_portfolio: Dict,
                                       esg_performance: Dict) -> float:
        """Berechnet erweiterten Social Score"""
        
        # Energieeffizienz Score (0-40 Punkte)
        efficiency = co2_metrics.get('energy_efficiency_percent', 0)
        efficiency_score = min(40, max(0, efficiency * 0.4))  # 100% = 40 Punkte
        
        # Kosteneinsparungen Score (0-30 Punkte)
        cost_savings = co2_metrics.get('cost_savings_eur', 0)
        cost_savings_score = min(30, max(0, (cost_savings / 1000) * 10))  # 1k€ = 10 Punkte, max 30
        
        # Green Finance Engagement Score (0-30 Punkte)
        green_finance_score = 0
        if green_finance_portfolio['total_value_eur'] > 0:
            green_finance_score = min(30, max(0, 
                (green_finance_portfolio['total_value_eur'] / 10000) * 30
            ))
        
        return efficiency_score + cost_savings_score + green_finance_score
    
    def _calculate_enhanced_governance_score(self, esg_performance: Dict,
                                           green_finance_portfolio: Dict) -> float:
        """Berechnet erweiterten Governance Score"""
        
        # Basis Governance Score (0-50 Punkte)
        base_governance = 50
        
        # Compliance Score (0-30 Punkte)
        compliance_score = 30 if esg_performance['compliance_status'] == 'compliant' else 0
        
        # Portfolio Management Score (0-20 Punkte)
        portfolio_score = 0
        if green_finance_portfolio['total_value_eur'] > 0:
            # Positive Performance = +20, Negative = -10, Neutral = 0
            if green_finance_portfolio['performance_percent'] > 5:
                portfolio_score = 20
            elif green_finance_portfolio['performance_percent'] < -5:
                portfolio_score = -10
            else:
                portfolio_score = 10
        
        return base_governance + compliance_score + max(0, portfolio_score)
    
    def _determine_sustainability_rating(self, overall_score: float) -> str:
        """Bestimmt Sustainability Rating basierend auf ESG-Score"""
        if overall_score >= 95:
            return 'AAA+'
        elif overall_score >= 90:
            return 'AAA'
        elif overall_score >= 85:
            return 'AA+'
        elif overall_score >= 80:
            return 'AA'
        elif overall_score >= 75:
            return 'AA-'
        elif overall_score >= 70:
            return 'A+'
        elif overall_score >= 65:
            return 'A'
        elif overall_score >= 60:
            return 'A-'
        elif overall_score >= 55:
            return 'BBB+'
        elif overall_score >= 50:
            return 'BBB'
        elif overall_score >= 45:
            return 'BBB-'
        elif overall_score >= 40:
            return 'BB+'
        elif overall_score >= 35:
            return 'BB'
        elif overall_score >= 30:
            return 'BB-'
        elif overall_score >= 25:
            return 'B+'
        elif overall_score >= 20:
            return 'B'
        else:
            return 'B-'
    
    def _get_environmental_breakdown(self, co2_metrics: Dict, carbon_credit_revenue: Dict) -> Dict:
        """Erstellt Environmental Score Aufschlüsselung"""
        return {
            'co2_reduction_score': min(60, max(0, (co2_metrics.get('co2_saved_total_kg', 0) / 1000) * 10)),
            'renewable_energy_score': min(20, max(0, co2_metrics.get('renewable_share_percent', 0) * 0.2)),
            'carbon_credit_score': min(20, max(0, (carbon_credit_revenue.get('revenue_utilization_percent', 0) / 100) * 20)),
            'co2_saved_kg': co2_metrics.get('co2_saved_total_kg', 0),
            'renewable_share_percent': co2_metrics.get('renewable_share_percent', 0),
            'carbon_credit_revenue_eur': carbon_credit_revenue.get('actual_revenue_eur', 0)
        }
    
    def _get_social_breakdown(self, co2_metrics: Dict, green_finance_portfolio: Dict) -> Dict:
        """Erstellt Social Score Aufschlüsselung"""
        return {
            'efficiency_score': min(40, max(0, co2_metrics.get('energy_efficiency_percent', 0) * 0.4)),
            'cost_savings_score': min(30, max(0, (co2_metrics.get('cost_savings_eur', 0) / 1000) * 10)),
            'green_finance_score': min(30, max(0, (green_finance_portfolio.get('total_value_eur', 0) / 10000) * 30)),
            'efficiency_percent': co2_metrics.get('energy_efficiency_percent', 0),
            'cost_savings_eur': co2_metrics.get('cost_savings_eur', 0),
            'green_finance_value_eur': green_finance_portfolio.get('total_value_eur', 0)
        }
    
    def _get_governance_breakdown(self, esg_performance: Dict) -> Dict:
        """Erstellt Governance Score Aufschlüsselung"""
        return {
            'base_governance_score': 50,
            'compliance_score': 30 if esg_performance.get('compliance_status') == 'compliant' else 0,
            'portfolio_management_score': 20,  # Vereinfacht
            'compliance_status': esg_performance.get('compliance_status', 'unknown'),
            'sustainability_rating': esg_performance.get('sustainability_rating', 'B')
        }
    
    def _generate_recommendations(self, overall_score: float, esg_performance: Dict) -> List[str]:
        """Generiert Empfehlungen basierend auf ESG-Performance"""
        recommendations = []
        
        if overall_score < 70:
            recommendations.extend([
                "Erhöhen Sie die CO₂-Einsparungen durch optimierte BESS-Nutzung",
                "Verbessern Sie die Energieeffizienz des Systems",
                "Erwägen Sie zusätzliche erneuerbare Energiequellen"
            ])
        
        if esg_performance.get('carbon_credits_sold', 0) == 0:
            recommendations.append("Beginnen Sie mit dem Verkauf von Carbon Credits für zusätzliche Erlöse")
        
        if esg_performance.get('green_finance_value_eur', 0) == 0:
            recommendations.append("Erwägen Sie Green Finance Investitionen für bessere ESG-Scores")
        
        if overall_score >= 85:
            recommendations.append("Hervorragende ESG-Performance! Halten Sie das hohe Niveau bei")
        
        return recommendations
    
    def generate_html_report(self, esg_report: ESGReport) -> str:
        """Generiert HTML-Report aus ESG-Report"""
        
        html_template = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ESG-Report: {{ project_name }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
        .container { background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; margin-bottom: 30px; border-bottom: 3px solid #2ecc71; padding-bottom: 20px; }
        .score-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
        .score-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }
        .score-value { font-size: 2.5em; font-weight: bold; margin-bottom: 10px; }
        .score-label { font-size: 1.1em; opacity: 0.9; }
        .section { margin: 30px 0; }
        .section h3 { color: #2c3e50; border-left: 4px solid #3498db; padding-left: 15px; }
        .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin: 15px 0; }
        .metric-card { background: #ecf0f1; padding: 15px; border-radius: 8px; border-left: 4px solid #3498db; }
        .metric-value { font-size: 1.5em; font-weight: bold; color: #2c3e50; }
        .metric-label { color: #7f8c8d; font-size: 0.9em; }
        .recommendations { background: #e8f5e8; padding: 20px; border-radius: 8px; border-left: 4px solid #27ae60; }
        .recommendations ul { margin: 10px 0; padding-left: 20px; }
        .recommendations li { margin: 5px 0; color: #2c3e50; }
        .footer { text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #bdc3c7; color: #7f8c8d; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌱 ESG-Report: {{ project_name }}</h1>
            <p><strong>Berichtszeitraum:</strong> {{ period_start }} bis {{ period_end }}</p>
            <p><strong>Berichtstyp:</strong> {{ report_type.title() }}</p>
            <p><strong>Sustainability Rating:</strong> <span style="font-size: 1.5em; color: #27ae60;">{{ sustainability_rating }}</span></p>
        </div>

        <div class="score-grid">
            <div class="score-card">
                <div class="score-value">{{ environmental_score }}</div>
                <div class="score-label">Environmental</div>
            </div>
            <div class="score-card">
                <div class="score-value">{{ social_score }}</div>
                <div class="score-label">Social</div>
            </div>
            <div class="score-card">
                <div class="score-value">{{ governance_score }}</div>
                <div class="score-label">Governance</div>
            </div>
            <div class="score-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                <div class="score-value">{{ overall_esg_score }}</div>
                <div class="score-label">Overall ESG</div>
            </div>
        </div>

        <div class="section">
            <h3>📊 Umwelt-Metriken</h3>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{{ "%.1f"|format(report_data.environmental_breakdown.co2_saved_kg / 1000) }} t</div>
                    <div class="metric-label">CO₂-Einsparungen</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{{ "%.1f"|format(report_data.environmental_breakdown.renewable_share_percent) }}%</div>
                    <div class="metric-label">Erneuerbare Energie</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{{ "%.0f"|format(report_data.environmental_breakdown.carbon_credit_revenue_eur) }} €</div>
                    <div class="metric-label">Carbon Credit Erlöse</div>
                </div>
            </div>
        </div>

        <div class="section">
            <h3>👥 Sozial-Metriken</h3>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{{ "%.1f"|format(report_data.social_breakdown.efficiency_percent) }}%</div>
                    <div class="metric-label">Energieeffizienz</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{{ "%.0f"|format(report_data.social_breakdown.cost_savings_eur) }} €</div>
                    <div class="metric-label">Kosteneinsparungen</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{{ "%.0f"|format(report_data.social_breakdown.green_finance_value_eur) }} €</div>
                    <div class="metric-label">Green Finance Portfolio</div>
                </div>
            </div>
        </div>

        <div class="section">
            <h3>⚖️ Governance-Metriken</h3>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{{ report_data.governance_breakdown.compliance_status.title() }}</div>
                    <div class="metric-label">Compliance Status</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{{ report_data.governance_breakdown.sustainability_rating }}</div>
                    <div class="metric-label">Sustainability Rating</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{{ carbon_credits_generated }}</div>
                    <div class="metric-label">Carbon Credits Generiert</div>
                </div>
            </div>
        </div>

        <div class="section">
            <h3>💡 Empfehlungen</h3>
            <div class="recommendations">
                <ul>
                {% for recommendation in report_data.recommendations %}
                    <li>{{ recommendation }}</li>
                {% endfor %}
                </ul>
            </div>
        </div>

        <div class="footer">
            <p>Generiert am {{ "now"|strftime('%d.%m.%Y %H:%M') }} | BESS-Simulation ESG-Reporting System</p>
        </div>
    </div>
</body>
</html>
        """
        
        template = Template(html_template)
        return template.render(
            project_name=esg_report.project_name,
            period_start=esg_report.period_start,
            period_end=esg_report.period_end,
            report_type=esg_report.report_type,
            sustainability_rating=esg_report.sustainability_rating,
            environmental_score=esg_report.environmental_score,
            social_score=esg_report.social_score,
            governance_score=esg_report.governance_score,
            overall_esg_score=esg_report.overall_esg_score,
            carbon_credits_generated=esg_report.carbon_credits_generated,
            report_data=esg_report.report_data
        )
    
    def save_report_to_file(self, esg_report: ESGReport, file_path: str):
        """Speichert ESG-Report als HTML-Datei"""
        html_content = self.generate_html_report(esg_report)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ ESG-Report gespeichert: {file_path}")
    
    def send_email_report(self, esg_report: ESGReport, recipient_email: str, 
                         attachment_path: Optional[str] = None):
        """Sendet ESG-Report per E-Mail"""
        
        if not self.email_config['username'] or not self.email_config['password']:
            print("❌ E-Mail-Konfiguration nicht vollständig")
            return False
        
        try:
            # E-Mail erstellen
            msg = MIMEMultipart()
            msg['From'] = self.email_config['from_email']
            msg['To'] = recipient_email
            msg['Subject'] = f"ESG-Report {esg_report.project_name} - {esg_report.period_start} bis {esg_report.period_end}"
            
            # E-Mail Body
            body = f"""
Hallo,

anbei finden Sie den ESG-Report für {esg_report.project_name}.

**Zusammenfassung:**
- ESG-Score: {esg_report.overall_esg_score}/100
- Sustainability Rating: {esg_report.sustainability_rating}
- CO₂-Einsparungen: {esg_report.report_data['co2_metrics']['co2_saved_total_kg']/1000:.1f} tCO₂
- Carbon Credit Erlöse: {esg_report.carbon_credits_revenue_eur:.0f} €

Mit freundlichen Grüßen,
BESS-Simulation ESG-Reporting System
            """
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # HTML-Anhang hinzufügen falls vorhanden
            if attachment_path and os.path.exists(attachment_path):
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
            
            print(f"✅ ESG-Report per E-Mail gesendet an: {recipient_email}")
            return True
            
        except Exception as e:
            print(f"❌ Fehler beim Senden der E-Mail: {e}")
            return False
    
    def setup_automatic_reporting(self, project_id: int, report_type: str, 
                                recipient_email: str, schedule_time: str = "09:00"):
        """Richtet automatische ESG-Reports ein"""
        
        def generate_and_send_report():
            try:
                print(f"🔄 Generiere automatischen {report_type} ESG-Report für Projekt {project_id}")
                
                # ESG-Report generieren
                esg_report = self.generate_comprehensive_esg_report(project_id, report_type)
                
                # Report als HTML speichern
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"esg_report_{esg_report.project_name}_{timestamp}.html"
                filepath = os.path.join('reports', filename)
                
                os.makedirs('reports', exist_ok=True)
                self.save_report_to_file(esg_report, filepath)
                
                # Report per E-Mail senden
                self.send_email_report(esg_report, recipient_email, filepath)
                
                print(f"✅ Automatischer ESG-Report erfolgreich generiert und versendet")
                
            except Exception as e:
                print(f"❌ Fehler beim automatischen ESG-Report: {e}")
        
        # Schedule einrichten
        if report_type == 'monthly':
            schedule.every().month.do(generate_and_send_report)
        elif report_type == 'quarterly':
            schedule.every().quarter.do(generate_and_send_report)
        elif report_type == 'yearly':
            schedule.every().year.do(generate_and_send_report)
        else:
            schedule.every().day.at(schedule_time).do(generate_and_send_report)
        
        print(f"✅ Automatische {report_type} ESG-Reports eingerichtet für Projekt {project_id}")
        print(f"📧 E-Mail-Adresse: {recipient_email}")
        print(f"⏰ Zeitplan: {schedule_time}")

def main():
    """Hauptfunktion für Enhanced ESG-Reporting System"""
    print("🌱 Enhanced ESG-Reporting System für BESS-Simulation")
    print("=" * 60)
    
    # Enhanced ESG-Reporting System initialisieren
    esg_system = EnhancedESGReportingSystem()
    
    print("✅ Enhanced ESG-Reporting System erfolgreich initialisiert")
    print("📊 Features:")
    print("   - Umfassende ESG-Reports mit Carbon Credits")
    print("   - Green Finance Integration")
    print("   - HTML-Report Generierung")
    print("   - Automatische E-Mail-Reports")
    print("   - Sustainability Rating System")
    print("   - Empfehlungs-Engine")

if __name__ == '__main__':
    main()
