"""
PDF-Export für BESS-Simulation
Verwendet reportlab für professionelle PDF-Erstellung
"""

from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import os
import tempfile
from datetime import datetime

class BESSPDFExporter:
    """PDF-Export für BESS-Simulation"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Benutzerdefinierte Styles für BESS-Export"""
        # Titel-Style
        self.title_style = ParagraphStyle(
            'BESSTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        # Untertitel-Style
        self.subtitle_style = ParagraphStyle(
            'BESSSubtitle',
            parent=self.styles['Heading2'],
            fontSize=18,
            spaceAfter=20,
            alignment=TA_LEFT,
            textColor=colors.darkgreen
        )
        
        # Überschrift-Style
        self.heading_style = ParagraphStyle(
            'BESSHeading',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceAfter=15,
            alignment=TA_LEFT,
            textColor=colors.darkblue
        )
        
        # Normaler Text
        self.normal_style = ParagraphStyle(
            'BESSNormal',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            alignment=TA_LEFT
        )
        
        # Tabellen-Header
        self.table_header_style = ParagraphStyle(
            'BESSTableHeader',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=8,
            alignment=TA_CENTER,
            textColor=colors.white,
            backColor=colors.darkblue
        )
    
    def export_simulation_pdf(self, simulation_data, project_data):
        """Exportiert BESS-Simulation als PDF"""
        try:
            # Temporäre PDF-Datei erstellen
            temp_dir = tempfile.gettempdir()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"BESS_Simulation_{project_data.get('name', 'Projekt')}_{timestamp}.pdf"
            pdf_path = os.path.join(temp_dir, filename)
            
            # PDF-Dokument erstellen
            doc = SimpleDocTemplate(pdf_path, pagesize=A4)
            story = []
            
            # Titel
            story.append(Paragraph("BESS-Simulation & Use Cases", self.title_style))
            story.append(Spacer(1, 20))
            
            # Projektinformationen
            story.append(Paragraph("Projektinformationen", self.subtitle_style))
            project_table_data = [
                ['Projektname', project_data.get('name', '-')],
                ['Standort', project_data.get('location', '-')],
                ['BESS-Größe', f"{project_data.get('bess_size', 0):.1f} kWh"],
                ['BESS-Leistung', f"{project_data.get('bess_power', 0):.1f} kW"],
                ['PV-Leistung', f"{project_data.get('pv_power', 0):.1f} kW"],
                ['Hydro-Leistung', f"{project_data.get('hydro_power', 0):.1f} kW"]
            ]
            
            project_table = Table(project_table_data, colWidths=[3*cm, 8*cm])
            project_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(project_table)
            story.append(Spacer(1, 20))
            
            # Use Case Analysen
            if 'use_cases' in simulation_data:
                story.append(Paragraph("Use Case Analysen", self.subtitle_style))
                
                uc_table_data = [['Use Case', 'Beschreibung', 'Erlös (€/a)', 'Kosten (€/a)', 'Netto (€/a)']]
                
                for uc_key, uc_data in simulation_data['use_cases'].items():
                    revenue = uc_data.get('revenue', 0)
                    costs = uc_data.get('costs', 0)
                    netto = revenue - costs
                    uc_table_data.append([
                        uc_key,
                        uc_data.get('name', ''),
                        f"{revenue:,.0f}",
                        f"{costs:,.0f}",
                        f"{netto:,.0f}"
                    ])
                
                uc_table = Table(uc_table_data, colWidths=[1.5*cm, 4*cm, 2*cm, 2*cm, 2*cm])
                uc_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('ALIGN', (1, 1), (1, -1), 'LEFT'),  # Beschreibung linksbündig
                ]))
                story.append(uc_table)
                story.append(Spacer(1, 20))
            
            # 10-Jahres-Analyse
            if 'ten_year_analysis' in simulation_data:
                story.append(Paragraph("10-Jahres-Wirtschaftlichkeitsanalyse", self.subtitle_style))
                
                analysis_data = simulation_data['ten_year_analysis']
                analysis_table_data = [
                    ['Kennzahl', 'Wert'],
                    ['Gesamterlöse (10 Jahre)', f"{analysis_data.get('total_revenues', 0):,.0f} €"],
                    ['Gesamt-Netto-Cashflow', f"{analysis_data.get('total_net_cashflow', 0):,.0f} €"],
                    ['NPV (Net Present Value)', f"{analysis_data.get('npv', 0):,.0f} €"],
                    ['IRR (Internal Rate of Return)', f"{analysis_data.get('irr', 0):.1f} %"]
                ]
                
                analysis_table = Table(analysis_table_data, colWidths=[6*cm, 6*cm])
                analysis_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(analysis_table)
                story.append(Spacer(1, 20))
            
            # Wirtschaftlichkeitsmetriken
            if 'economic_metrics' in simulation_data:
                story.append(Paragraph("Wirtschaftlichkeitsmetriken", self.subtitle_style))
                
                metrics_data = simulation_data['economic_metrics']
                metrics_table_data = [
                    ['Metrik', 'Wert'],
                    ['ROI', f"{metrics_data.get('roi', 0):.1f} %"],
                    ['Amortisation', f"{metrics_data.get('amortization', 0):.1f} Jahre"],
                    ['Investition', f"{metrics_data.get('investment', 0):,.0f} €"],
                    ['Net Cashflow', f"{metrics_data.get('net_cashflow', 0):,.0f} €/a"]
                ]
                
                metrics_table = Table(metrics_table_data, colWidths=[6*cm, 6*cm])
                metrics_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(metrics_table)
                story.append(Spacer(1, 20))
            
            # Footer
            story.append(Paragraph(f"Erstellt am: {datetime.now().strftime('%d.%m.%Y um %H:%M Uhr')}", self.normal_style))
            story.append(Paragraph("BESS-Simulation Export", self.normal_style))
            
            # PDF erstellen
            doc.build(story)
            
            return pdf_path
            
        except Exception as e:
            print(f"Fehler beim PDF-Export: {e}")
            return None
    
    def export_dashboard_pdf(self, dashboard_data, project_data):
        """Exportiert BESS-Dashboard als PDF"""
        try:
            # Temporäre PDF-Datei erstellen
            temp_dir = tempfile.gettempdir()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"BESS_Dashboard_{project_data.get('name', 'Projekt')}_{timestamp}.pdf"
            pdf_path = os.path.join(temp_dir, filename)
            
            # PDF-Dokument erstellen
            doc = SimpleDocTemplate(pdf_path, pagesize=A4)
            story = []
            
            # Titel
            story.append(Paragraph("BESS Enhanced Dashboard", self.title_style))
            story.append(Spacer(1, 20))
            
            # Projektinformationen
            story.append(Paragraph("Projektinformationen", self.subtitle_style))
            project_table_data = [
                ['Projektname', project_data.get('name', '-')],
                ['Standort', project_data.get('location', '-')],
                ['BESS-Größe', f"{project_data.get('bess_size', 0):.1f} kWh"],
                ['BESS-Leistung', f"{project_data.get('bess_power', 0):.1f} kW"]
            ]
            
            project_table = Table(project_table_data, colWidths=[3*cm, 8*cm])
            project_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(project_table)
            story.append(Spacer(1, 20))
            
            # Dashboard-Kennzahlen
            if 'metrics' in dashboard_data:
                story.append(Paragraph("Dashboard-Kennzahlen", self.subtitle_style))
                
                metrics_data = dashboard_data['metrics']
                metrics_table_data = [
                    ['Kennzahl', 'Wert'],
                    ['Eigenverbrauchsquote', f"{metrics_data.get('eigenverbrauchsquote', 0):.1f} %"],
                    ['CO₂-Einsparung', f"{metrics_data.get('co2_savings', 0):,.0f} kg/a"],
                    ['Netto-Erlöse', f"{metrics_data.get('netto_erloes', 0):,.0f} €/a"],
                    ['BESS-Effizienz', f"{metrics_data.get('bess_efficiency', 0):.1f} %"],
                    ['Spot-Markt-Erlöse', f"{metrics_data.get('spot_revenue', 0):,.0f} €/a"],
                    ['Regelreserve-Erlöse', f"{metrics_data.get('regelreserve_revenue', 0):,.0f} €/a"]
                ]
                
                metrics_table = Table(metrics_table_data, colWidths=[6*cm, 6*cm])
                metrics_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(metrics_table)
                story.append(Spacer(1, 20))
            
            # BESS-Modi
            if 'bess_modes' in dashboard_data:
                story.append(Paragraph("BESS-Betriebsmodi", self.subtitle_style))
                
                modes_data = dashboard_data['bess_modes']
                modes_table_data = [['Betriebsmodus', 'Status']]
                
                for mode in modes_data:
                    modes_table_data.append([mode.replace('_', ' ').title(), 'Aktiv'])
                
                modes_table = Table(modes_table_data, colWidths=[6*cm, 6*cm])
                modes_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(modes_table)
                story.append(Spacer(1, 20))
            
            # Footer
            story.append(Paragraph(f"Erstellt am: {datetime.now().strftime('%d.%m.%Y um %H:%M Uhr')}", self.normal_style))
            story.append(Paragraph("BESS-Dashboard Export", self.normal_style))
            
            # PDF erstellen
            doc.build(story)
            
            return pdf_path
            
        except Exception as e:
            print(f"Fehler beim Dashboard-PDF-Export: {e}")
            return None
