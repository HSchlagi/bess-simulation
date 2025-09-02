"""
Export-Routen für BESS-Simulation
Flask-Routen für PDF, Excel, CSV und Batch-Export
"""

from flask import Blueprint, render_template, request, jsonify, send_file, flash, redirect, url_for, session
import os
import tempfile
from datetime import datetime
from werkzeug.utils import secure_filename

# Import der Export-Funktionen
try:
    from export_functions import BESSExporter, PDF_AVAILABLE, EXCEL_AVAILABLE
except ImportError as e:
    print(f"Warnung: Export-Funktionen nicht verfügbar: {e}")
    BESSExporter = None

# Blueprint erstellen
export_bp = Blueprint('export', __name__, url_prefix='/export')

@export_bp.route('/')
def export_center():
    """Export-Zentrum - Übersicht aller Export-Optionen"""
    return render_template('export/export_center.html')

@export_bp.route('/project/<int:project_id>/pdf')
def export_project_pdf(project_id):
    """Exportiert ein Projekt als PDF"""
    if not BESSExporter:
        flash('PDF-Export nicht verfügbar. Bitte installieren Sie reportlab.', 'error')
        return redirect(url_for('main.projects'))
    
    if not PDF_AVAILABLE:
        flash('PDF-Export nicht verfügbar. Bitte installieren Sie reportlab: pip install reportlab', 'error')
        return redirect(url_for('main.projects'))
    
    try:
        # Projekt-Daten laden (hier müssen Sie Ihre Datenbankabfrage anpassen)
        from models import Project
        project = Project.query.get_or_404(project_id)
        
        # Projekt-Daten als Dictionary vorbereiten
        project_data = {
            'id': project.id,
            'name': project.name,
            'location': project.location,
            'bess_size': project.bess_size or 0,
            'bess_power': project.bess_power or 0,
            'pv_power': project.pv_power or 0,
            'hydro_power': project.hydro_power or 0,
            'current_electricity_cost': project.current_electricity_cost or 0,
            'battery_type': getattr(project, 'battery_type', 'Lithium-Ion'),
            'depth_of_discharge': getattr(project, 'depth_of_discharge', 80),
            'battery_lifetime': getattr(project, 'battery_lifetime', 10),
            'efficiency': getattr(project, 'efficiency', 90),
        }
        
        # PDF erstellen
        exporter = BESSExporter()
        pdf_path = exporter.export_project_pdf(project_data)
        
        # Datei zum Download senden
        filename = f"BESS_Projekt_{project.name}_{datetime.now().strftime('%Y%m%d')}.pdf"
        return send_file(pdf_path, as_attachment=True, download_name=filename)
        
    except Exception as e:
        flash(f'Fehler beim PDF-Export: {str(e)}', 'error')
        return redirect(url_for('main.projects'))

@export_bp.route('/project/<int:project_id>/excel')
def export_project_excel(project_id):
    """Exportiert ein Projekt als Excel-Datei"""
    if not BESSExporter:
        flash('Excel-Export nicht verfügbar.', 'error')
        return redirect(url_for('main.projects'))
    
    if not EXCEL_AVAILABLE:
        flash('Excel-Export nicht verfügbar. Bitte installieren Sie openpyxl: pip install openpyxl', 'error')
        return redirect(url_for('main.projects'))
    
    try:
        # Projekt-Daten laden
        from models import Project
        project = Project.query.get_or_404(project_id)
        
        # Simulationsdaten vorbereiten (hier können Sie echte Simulationsdaten laden)
        simulation_data = {
            'project': {
                'id': project.id,
                'name': project.name,
                'location': project.location,
                'bess_size': project.bess_size or 0,
                'bess_power': project.bess_power or 0,
                'pv_power': project.pv_power or 0,
                'hydro_power': project.hydro_power or 0,
                'current_electricity_cost': project.current_electricity_cost or 0,
            },
            'time_series': [
                # Beispiel-Zeitreihendaten
                {
                    'date': '2024-01-01',
                    'time': '00:00',
                    'load': 100.0,
                    'pv_generation': 0.0,
                    'battery_charge': 0.0,
                    'battery_discharge': 50.0,
                    'grid_import': 50.0,
                    'grid_export': 0.0
                },
                {
                    'date': '2024-01-01',
                    'time': '12:00',
                    'load': 150.0,
                    'pv_generation': 200.0,
                    'battery_charge': 50.0,
                    'battery_discharge': 0.0,
                    'grid_import': 0.0,
                    'grid_export': 100.0
                }
            ],
            'economic_analysis': {
                'total_cost': 50000.0,
                'annual_savings': 15000.0,
                'payback_period': 3.33,
                'roi': 30.0,
                'npv': 25000.0,
                'irr': 25.0
            }
        }
        
        # Excel erstellen
        exporter = BESSExporter()
        excel_path = exporter.export_simulation_excel(simulation_data)
        
        # Datei zum Download senden
        filename = f"BESS_Simulation_{project.name}_{datetime.now().strftime('%Y%m%d')}.xlsx"
        return send_file(excel_path, as_attachment=True, download_name=filename)
        
    except Exception as e:
        flash(f'Fehler beim Excel-Export: {str(e)}', 'error')
        return redirect(url_for('main.projects'))

@export_bp.route('/project/<int:project_id>/csv')
def export_project_csv(project_id):
    """Exportiert ein Projekt als CSV-Datei"""
    if not BESSExporter:
        flash('CSV-Export nicht verfügbar.', 'error')
        return redirect(url_for('main.projects'))
    
    try:
        # Projekt-Daten laden
        from models import Project
        project = Project.query.get_or_404(project_id)
        
        # Projekt-Daten als Liste vorbereiten
        project_data = [{
            'id': project.id,
            'name': project.name,
            'location': project.location,
            'bess_size_kwh': project.bess_size or 0,
            'bess_power_kw': project.bess_power or 0,
            'pv_power_kw': project.pv_power or 0,
            'hydro_power_kw': project.hydro_power or 0,
            'electricity_cost_eur_per_kwh': project.current_electricity_cost or 0,
            'created_at': project.created_at.isoformat() if project.created_at else '',
        }]
        
        # CSV erstellen
        exporter = BESSExporter()
        csv_path = exporter.export_data_csv(project_data)
        
        # Datei zum Download senden
        filename = f"BESS_Projekt_{project.name}_{datetime.now().strftime('%Y%m%d')}.csv"
        return send_file(csv_path, as_attachment=True, download_name=filename)
        
    except Exception as e:
        flash(f'Fehler beim CSV-Export: {str(e)}', 'error')
        return redirect(url_for('main.projects'))

@export_bp.route('/batch', methods=['GET', 'POST'])
def batch_export():
    """Batch-Export für mehrere Projekte"""
    if not BESSExporter:
        flash('Batch-Export nicht verfügbar.', 'error')
        return redirect(url_for('main.projects'))
    
    if request.method == 'POST':
        try:
            # Ausgewählte Projekte und Formate
            selected_projects = request.form.getlist('projects')
            export_formats = request.form.getlist('formats')
            
            if not selected_projects:
                flash('Bitte wählen Sie mindestens ein Projekt aus.', 'error')
                return redirect(url_for('export.batch_export'))
            
            if not export_formats:
                flash('Bitte wählen Sie mindestens ein Export-Format aus.', 'error')
                return redirect(url_for('export.batch_export'))
            
            # Projekte laden
            from models import Project
            projects = []
            for project_id in selected_projects:
                project = Project.query.get(project_id)
                if project:
                    project_data = {
                        'id': project.id,
                        'name': project.name,
                        'location': project.location,
                        'bess_size': project.bess_size or 0,
                        'bess_power': project.bess_power or 0,
                        'pv_power': project.pv_power or 0,
                        'hydro_power': project.hydro_power or 0,
                        'current_electricity_cost': project.current_electricity_cost or 0,
                    }
                    projects.append(project_data)
            
            # Batch-Export durchführen
            exporter = BESSExporter()
            zip_path = exporter.batch_export_projects(projects, export_formats)
            
            # ZIP-Datei zum Download senden
            filename = f"BESS_Batch_Export_{datetime.now().strftime('%Y%m%d_%H%M')}.zip"
            return send_file(zip_path, as_attachment=True, download_name=filename)
            
        except Exception as e:
            flash(f'Fehler beim Batch-Export: {str(e)}', 'error')
            return redirect(url_for('export.batch_export'))
    
    # GET-Request: Formular anzeigen
    try:
        from models import Project
        projects = Project.query.all()
        return render_template('export/batch_export.html', projects=projects)
    except Exception as e:
        flash(f'Fehler beim Laden der Projekte: {str(e)}', 'error')
        return redirect(url_for('main.projects'))

@export_bp.route('/bess-combined')
def bess_combined_export():
    """Kombinierter Export aller BESS-Analysen"""
    return render_template('export/bess_combined_export.html')

@export_bp.route('/bess-simulation/<int:project_id>')
def export_bess_simulation(project_id):
    """Exportiert BESS-Simulation für ein spezifisches Projekt"""
    try:
        # Projekt-Daten laden
        from models import Project
        project = Project.query.get_or_404(project_id)
        
        # Hier würden die Simulationsdaten geladen werden
        # Für den Moment verwenden wir Beispieldaten
        simulation_data = {
            'project': project,
            'use_cases': {
                'UC1': {'name': 'Verbrauch ohne Eigenerzeugung', 'revenue': 25000, 'costs': 18000},
                'UC2': {'name': 'Verbrauch + PV (1,95 MWp)', 'revenue': 35000, 'costs': 20000},
                'UC3': {'name': 'Verbrauch + PV + Wasserkraft', 'revenue': 45000, 'costs': 22000}
            },
            'ten_year_analysis': {
                'total_revenues': 380000,
                'total_net_cashflow': 180000,
                'npv': 120000,
                'irr': 15.5
            }
        }
        
        return render_template('export/bess_simulation_export.html', 
                             project=project, 
                             simulation_data=simulation_data)
        
    except Exception as e:
        flash(f'Fehler beim Laden der BESS-Simulation: {str(e)}', 'error')
        return redirect(url_for('export.export_center'))

@export_bp.route('/bess-dashboard/<int:project_id>')
def export_bess_dashboard(project_id):
    """Exportiert BESS-Dashboard für ein spezifisches Projekt"""
    try:
        # Projekt-Daten laden
        from models import Project
        project = Project.query.get_or_404(project_id)
        
        # Dashboard-Daten vorbereiten
        dashboard_data = {
            'project': project,
            'metrics': {
                'eigenverbrauchsquote': 45.2,
                'co2_savings': 1250,
                'netto_erloes': 45000,
                'bess_efficiency': 85.5,
                'spot_revenue': 28000,
                'regelreserve_revenue': 8500
            },
            'bess_modes': ['arbitrage', 'peak_shaving', 'frequency_regulation', 'backup']
        }
        
        return render_template('export/bess_dashboard_export.html', 
                             project=project, 
                             dashboard_data=dashboard_data)
        
    except Exception as e:
        flash(f'Fehler beim Laden des BESS-Dashboards: {str(e)}', 'error')
        return redirect(url_for('export.export_center'))

@export_bp.route('/templates')
def export_templates():
    """Export-Templates verwalten"""
    if not BESSExporter:
        flash('Export-Templates nicht verfügbar.', 'error')
        return redirect(url_for('export.export_center'))
    
    try:
        exporter = BESSExporter()
        templates = []
        
        # Verfügbare Templates auflisten
        if os.path.exists(exporter.templates_dir):
            for filename in os.listdir(exporter.templates_dir):
                if filename.endswith('.json'):
                    template_name = filename[:-5]  # .json entfernen
                    try:
                        template_data = exporter.load_export_template(template_name)
                        templates.append({
                            'name': template_name,
                            'display_name': template_data.get('name', template_name),
                            'sections': template_data.get('sections', []),
                            'language': template_data.get('language', 'de')
                        })
                    except Exception as e:
                        print(f"Fehler beim Laden von Template {template_name}: {e}")
        
        return render_template('export/templates.html', templates=templates)
        
    except Exception as e:
        flash(f'Fehler beim Laden der Templates: {str(e)}', 'error')
        return redirect(url_for('export.export_center'))

@export_bp.route('/api/export-status')
def export_status():
    """API-Endpunkt für Export-Status"""
    status = {
        'pdf_available': PDF_AVAILABLE if BESSExporter else False,
        'excel_available': EXCEL_AVAILABLE if BESSExporter else False,
        'csv_available': True,  # CSV ist immer verfügbar
        'templates_available': BESSExporter is not None
    }
    return jsonify(status)

@export_bp.route('/help')
def export_help():
    """Export-Hilfe-Seite"""
    return render_template('export/help.html')
