#!/usr/bin/env python3
"""
Climate Impact Dashboard API Routes
API-Endpunkte für Climate Impact Dashboard und CO₂-Zertifikate
"""

from flask import Blueprint, jsonify, request, send_file, render_template
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List, Optional
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

# Blueprint erstellen
climate_bp = Blueprint('climate', __name__)

# Carbon Credit Trading System importieren (optional)
try:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from carbon_credit_trading_system import CarbonCreditTradingSystem
    CARBON_CREDITS_AVAILABLE = True
except ImportError:
    CARBON_CREDITS_AVAILABLE = False
    print("⚠️  Carbon Credit Trading System nicht verfügbar - aiohttp fehlt")
# Weitere Systeme importieren (optional)
try:
    from enhanced_esg_reporting_system import EnhancedESGReportingSystem
    from green_finance_integration import GreenFinanceIntegration
    from co2_tracking_system import CO2TrackingSystem
    ADDITIONAL_SYSTEMS_AVAILABLE = True
except ImportError:
    ADDITIONAL_SYSTEMS_AVAILABLE = False
    print("⚠️  Zusätzliche Systeme nicht verfügbar")

# Systeme initialisieren (optional)
carbon_trading = None
esg_system = None
green_finance = None

if CARBON_CREDITS_AVAILABLE:
    carbon_trading = CarbonCreditTradingSystem()

if ADDITIONAL_SYSTEMS_AVAILABLE:
    esg_system = EnhancedESGReportingSystem()
    green_finance = GreenFinanceIntegration()
# CO2-System initialisieren (optional)
co2_system = None
if ADDITIONAL_SYSTEMS_AVAILABLE:
    try:
        co2_system = CO2TrackingSystem()
    except Exception as e:
        print(f"⚠️  CO2-System nicht verfügbar: {e}")

@climate_bp.route('/api/climate/co2-data/<int:project_id>')
def get_co2_data(project_id):
    """Ruft CO₂-Daten für ein Projekt ab"""
    try:
        conn = sqlite3.connect('instance/bess.db')
        
        # Prüfen ob CO₂-Tabelle existiert
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='co2_balance'")
        if not cursor.fetchone():
            # Demo-Daten zurückgeben
            return jsonify({
                'success': True,
                'data': {
                    'total_co2_saved': 1250.5,
                    'total_co2_emitted': 89.2,
                    'net_co2_balance': 1161.3,
                    'monthly_trend': [
                        {'month': 'Jan', 'saved': 95.2, 'emitted': 7.1},
                        {'month': 'Feb', 'saved': 108.7, 'emitted': 8.3},
                        {'month': 'Mär', 'saved': 142.3, 'emitted': 9.8},
                        {'month': 'Apr', 'saved': 156.8, 'emitted': 11.2},
                        {'month': 'Mai', 'saved': 178.9, 'emitted': 12.4},
                        {'month': 'Jun', 'saved': 195.6, 'emitted': 13.7},
                        {'month': 'Jul', 'saved': 201.3, 'emitted': 14.2},
                        {'month': 'Aug', 'saved': 189.4, 'emitted': 13.9},
                        {'month': 'Sep', 'saved': 167.2, 'emitted': 12.1},
                        {'month': 'Okt', 'saved': 134.8, 'emitted': 10.5},
                        {'month': 'Nov', 'saved': 98.7, 'emitted': 8.9},
                        {'month': 'Dez', 'saved': 82.1, 'emitted': 7.2}
                    ],
                    'efficiency': 92.8
                }
            })
        
        # CO₂-Balance Daten für die letzten 12 Monate
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=365)
        
        query = '''
        SELECT 
            date,
            SUM(co2_saved_kg) as daily_co2_saved,
            SUM(co2_emitted_kg) as daily_co2_emitted,
            SUM(net_co2_balance_kg) as daily_net_balance,
            AVG(efficiency_percent) as avg_efficiency
        FROM co2_balance 
        WHERE project_id = ? AND date BETWEEN ? AND ?
        GROUP BY date
        ORDER BY date
        '''
        
        df = pd.read_sql_query(query, conn, params=(project_id, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
        
        # Monatliche Aggregation
        monthly_data = []
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            df['month'] = df['date'].dt.to_period('M')
            
            monthly_agg = df.groupby('month').agg({
                'daily_co2_saved': 'sum',
                'daily_co2_emitted': 'sum',
                'daily_net_balance': 'sum',
                'avg_efficiency': 'mean'
            }).reset_index()
            
            monthly_data = [
                {
                    'month': str(month),
                    'co2_saved_kg': float(row['daily_co2_saved']),
                    'co2_emitted_kg': float(row['daily_co2_emitted']),
                    'net_co2_balance_kg': float(row['daily_net_balance']),
                    'efficiency_percent': float(row['avg_efficiency'])
                }
                for month, row in monthly_agg.iterrows()
            ]
        
        # Gesamtstatistiken
        total_co2_saved = df['daily_co2_saved'].sum() if not df.empty else 0
        total_co2_emitted = df['daily_co2_emitted'].sum() if not df.empty else 0
        net_co2_balance = df['daily_net_balance'].sum() if not df.empty else 0
        avg_efficiency = df['avg_efficiency'].mean() if not df.empty else 0
        
        # Nachhaltigkeits-Metriken
        sustainability_metrics = co2_system.generate_sustainability_metrics(
            project_id, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), 'yearly'
        )
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'total_co2_saved_kg': float(total_co2_saved),
                'total_co2_emitted_kg': float(total_co2_emitted),
                'net_co2_balance_kg': float(net_co2_balance),
                'avg_efficiency_percent': float(avg_efficiency),
                'monthly_data': monthly_data,
                'sustainability_metrics': sustainability_metrics,
                'renewable_share_percent': sustainability_metrics.get('renewable_share_percent', 0),
                'cost_savings_eur': sustainability_metrics.get('cost_savings_eur', 0),
                'energy_efficiency_percent': sustainability_metrics.get('energy_efficiency_percent', 0)
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@climate_bp.route('/api/climate/carbon-credits/<int:project_id>')
def get_carbon_credits_data(project_id):
    """Ruft Carbon Credit Daten für ein Projekt ab"""
    try:
        # Verfügbare Credits
        available_credits = carbon_trading.get_available_credits(project_id)
        
        # Carbon Credit Erlöse für das letzte Jahr
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=365)
        
        credit_revenue = carbon_trading.calculate_carbon_credit_revenue(
            project_id, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
        )
        
        # Gesamtstatistiken
        total_credits_generated = len(available_credits)
        total_credits_sold = sum(1 for credit in available_credits if credit.get('status') == 'sold')
        total_credits_available = sum(1 for credit in available_credits if credit.get('status') == 'available')
        
        return jsonify({
            'success': True,
            'data': {
                'credits_generated': total_credits_generated,
                'credits_sold': total_credits_sold,
                'credits_available': total_credits_available,
                'total_revenue_eur': credit_revenue.get('actual_revenue_eur', 0),
                'potential_revenue_eur': credit_revenue.get('potential_revenue_eur', 0),
                'revenue_utilization_percent': credit_revenue.get('revenue_utilization_percent', 0),
                'available_credits': available_credits[:10]  # Erste 10 anzeigen
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@climate_bp.route('/api/climate/green-finance/<int:project_id>')
def get_green_finance_data(project_id):
    """Ruft Green Finance Daten für ein Projekt ab"""
    try:
        # Portfolio Performance
        portfolio_performance = green_finance.calculate_portfolio_performance(project_id)
        
        # Verfügbare Green Bonds
        available_bonds = green_finance.get_available_green_bonds()
        
        # ESG-Beitrag
        esg_contribution = green_finance.calculate_green_finance_contribution_to_esg(project_id)
        
        return jsonify({
            'success': True,
            'data': {
                'total_portfolio_value_eur': portfolio_performance.get('total_portfolio_value_eur', 0),
                'total_invested_eur': portfolio_performance.get('total_invested_eur', 0),
                'total_returns_eur': portfolio_performance.get('total_returns_eur', 0),
                'total_returns_percent': portfolio_performance.get('total_returns_percent', 0),
                'annualized_return_percent': portfolio_performance.get('annualized_return_percent', 0),
                'esg_weighted_return_percent': portfolio_performance.get('esg_weighted_return_percent', 0),
                'carbon_impact_total_tonnes_co2': portfolio_performance.get('carbon_impact_total_tonnes_co2', 0),
                'green_alignment_score': portfolio_performance.get('green_alignment_score', 0),
                'risk_score': portfolio_performance.get('risk_score', 0),
                'product_count': portfolio_performance.get('product_count', 0),
                'average_esg_score': portfolio_performance.get('average_esg_score', 0),
                'available_bonds': available_bonds[:5],  # Erste 5 anzeigen
                'esg_contribution': esg_contribution
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@climate_bp.route('/api/climate/esg-data/<int:project_id>')
def get_esg_data(project_id):
    """Ruft ESG-Daten für ein Projekt ab"""
    try:
        # Umfassenden ESG-Report generieren
        esg_report = esg_system.generate_comprehensive_esg_report(project_id, 'monthly')
        
        return jsonify({
            'success': True,
            'data': {
                'overall_esg_score': esg_report.overall_esg_score,
                'environmental_score': esg_report.environmental_score,
                'social_score': esg_report.social_score,
                'governance_score': esg_report.governance_score,
                'sustainability_rating': esg_report.sustainability_rating,
                'compliance_status': esg_report.compliance_status,
                'carbon_credits_generated': esg_report.carbon_credits_generated,
                'carbon_credits_sold': esg_report.carbon_credits_sold,
                'carbon_credits_revenue_eur': esg_report.carbon_credits_revenue_eur,
                'green_finance_value_eur': esg_report.green_finance_value_eur,
                'report_data': esg_report.report_data
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@climate_bp.route('/api/climate/generate-carbon-credits/<int:project_id>', methods=['POST'])
def generate_carbon_credits(project_id):
    """Generiert Carbon Credits aus CO₂-Einsparungen"""
    try:
        data = request.get_json()
        credit_type = data.get('credit_type', 'VER')
        
        # CO₂-Einsparungen für das letzte Jahr berechnen
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=365)
        
        conn = sqlite3.connect('instance/bess.db')
        query = '''
        SELECT SUM(co2_saved_kg) as total_co2_saved
        FROM co2_balance 
        WHERE project_id = ? AND date BETWEEN ? AND ?
        '''
        
        df = pd.read_sql_query(query, conn, params=(project_id, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
        conn.close()
        
        co2_saved_kg = df.iloc[0]['total_co2_saved'] if not df.empty else 0
        
        if co2_saved_kg <= 0:
            return jsonify({'success': False, 'error': 'Keine CO₂-Einsparungen gefunden'}), 400
        
        # Carbon Credit generieren
        credit = carbon_trading.generate_carbon_credits_from_co2_reduction(
            project_id, co2_saved_kg, credit_type
        )
        
        # Credit speichern
        credit_id = carbon_trading.save_carbon_credit(credit)
        
        return jsonify({
            'success': True,
            'data': {
                'credit_id': credit_id,
                'volume_tonnes_co2': credit.volume_tonnes_co2,
                'price_eur_per_tonne': credit.price_eur_per_tonne,
                'total_value_eur': credit.volume_tonnes_co2 * credit.price_eur_per_tonne,
                'credit_type': credit.credit_type,
                'certification_standard': credit.certification_standard
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@climate_bp.route('/api/climate/purchase-green-bond/<int:project_id>', methods=['POST'])
def purchase_green_bond(project_id):
    """Kauft Green Bond für ein Projekt"""
    try:
        data = request.get_json()
        bond_name = data.get('bond_name')
        volume_eur = data.get('volume_eur', 0)
        
        if not bond_name or volume_eur <= 0:
            return jsonify({'success': False, 'error': 'Ungültige Bond-Daten'}), 400
        
        # Verfügbare Bonds abrufen
        available_bonds = green_finance.get_available_green_bonds()
        selected_bond = next((bond for bond in available_bonds if bond['name'] == bond_name), None)
        
        if not selected_bond:
            return jsonify({'success': False, 'error': 'Bond nicht gefunden'}), 404
        
        # Bond kaufen
        result = green_finance.purchase_green_bond(project_id, selected_bond, volume_eur)
        
        if result['success']:
            return jsonify({
                'success': True,
                'data': result
            })
        else:
            return jsonify({'success': False, 'error': result['error']}), 400
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@climate_bp.route('/api/climate/export-report/<int:project_id>', methods=['POST'])
def export_climate_report(project_id):
    """Exportiert Climate Impact Report als PDF"""
    try:
        # Daten sammeln
        co2_response = get_co2_data(project_id)
        carbon_response = get_carbon_credits_data(project_id)
        finance_response = get_green_finance_data(project_id)
        esg_response = get_esg_data(project_id)
        
        if not all([co2_response[0].get_json()['success'] for co2_response in [co2_response]]):
            return jsonify({'success': False, 'error': 'Fehler beim Laden der Daten'}), 500
        
        co2_data = co2_response[0].get_json()['data']
        carbon_data = carbon_response[0].get_json()['data']
        finance_data = finance_response[0].get_json()['data']
        esg_data = esg_response[0].get_json()['data']
        
        # PDF generieren
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Titel
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1
        )
        story.append(Paragraph("Climate Impact Report", title_style))
        story.append(Spacer(1, 20))
        
        # Projekt-Info
        story.append(Paragraph(f"Projekt ID: {project_id}", styles['Normal']))
        story.append(Paragraph(f"Generiert am: {datetime.now().strftime('%d.%m.%Y %H:%M')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # CO₂-Zusammenfassung
        story.append(Paragraph("CO₂-Einsparungen", styles['Heading2']))
        co2_table_data = [
            ['Metrik', 'Wert'],
            ['Gesamt CO₂-Einsparungen', f"{co2_data['total_co2_saved_kg']/1000:.1f} tCO₂"],
            ['Netto CO₂-Bilanz', f"{co2_data['net_co2_balance_kg']/1000:.1f} tCO₂"],
            ['Durchschnittliche Effizienz', f"{co2_data['avg_efficiency_percent']:.1f}%"],
            ['Anteil erneuerbare Energie', f"{co2_data['renewable_share_percent']:.1f}%"]
        ]
        
        co2_table = Table(co2_table_data)
        co2_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(co2_table)
        story.append(Spacer(1, 20))
        
        # Carbon Credits
        story.append(Paragraph("Carbon Credits", styles['Heading2']))
        carbon_table_data = [
            ['Metrik', 'Wert'],
            ['Generierte Credits', str(carbon_data['credits_generated'])],
            ['Verkaufte Credits', str(carbon_data['credits_sold'])],
            ['Verfügbare Credits', str(carbon_data['credits_available'])],
            ['Erlöse', f"{carbon_data['total_revenue_eur']:,.0f} EUR"]
        ]
        
        carbon_table = Table(carbon_table_data)
        carbon_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(carbon_table)
        story.append(Spacer(1, 20))
        
        # Green Finance
        story.append(Paragraph("Green Finance Portfolio", styles['Heading2']))
        finance_table_data = [
            ['Metrik', 'Wert'],
            ['Portfolio-Wert', f"{finance_data['total_portfolio_value_eur']:,.0f} EUR"],
            ['Investiert', f"{finance_data['total_invested_eur']:,.0f} EUR"],
            ['Rendite', f"{finance_data['total_returns_percent']:.1f}%"],
            ['Anzahl Produkte', str(finance_data['product_count'])]
        ]
        
        finance_table = Table(finance_table_data)
        finance_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(finance_table)
        story.append(Spacer(1, 20))
        
        # ESG-Scores
        story.append(Paragraph("ESG-Bewertung", styles['Heading2']))
        esg_table_data = [
            ['Metrik', 'Score'],
            ['Overall ESG Score', f"{esg_data['overall_esg_score']:.1f}/100"],
            ['Environmental Score', f"{esg_data['environmental_score']:.1f}/100"],
            ['Social Score', f"{esg_data['social_score']:.1f}/100"],
            ['Governance Score', f"{esg_data['governance_score']:.1f}/100"],
            ['Sustainability Rating', esg_data['sustainability_rating']]
        ]
        
        esg_table = Table(esg_table_data)
        esg_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(esg_table)
        
        # PDF erstellen
        doc.build(story)
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'climate_report_project_{project_id}_{datetime.now().strftime("%Y%m%d")}.pdf',
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@climate_bp.route('/climate-dashboard')
def climate_dashboard():
    """Zeigt das Climate Impact Dashboard"""
    return render_template('climate_impact_dashboard.html')

# Blueprint registrieren
def register_climate_routes(app):
    """Registriert Climate Routes in der Flask App"""
    app.register_blueprint(climate_bp, url_prefix='/climate')

# Blueprint für direkte Registrierung verfügbar machen
__all__ = ['climate_bp', 'register_climate_routes']
