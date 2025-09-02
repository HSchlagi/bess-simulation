"""
API-Routen für BESS-Simulation
"""

from flask import Blueprint, request, jsonify, send_file
import os
import tempfile
from datetime import datetime

# Import der PDF-Export-Funktion
try:
    from pdf_exporter import BESSPDFExporter
    PDF_EXPORTER_AVAILABLE = True
except ImportError as e:
    print(f"Warnung: PDF-Exporter nicht verfügbar: {e}")
    PDF_EXPORTER_AVAILABLE = False

# Blueprint erstellen
api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/export/pdf', methods=['POST'])
def export_pdf():
    """API-Endpunkt für PDF-Export"""
    print(f"📥 PDF-Export-Request erhalten: {request.get_json()}")
    
    if not PDF_EXPORTER_AVAILABLE:
        print("❌ PDF-Exporter nicht verfügbar")
        return jsonify({'error': 'PDF-Export nicht verfügbar'}), 500
    
    try:
        data = request.get_json()
        project_id = data.get('project_id')
        simulation_data = data.get('simulation_data', {})
        dashboard_data = data.get('dashboard_data', {})
        export_type = data.get('export_type', 'simulation')
        
        print(f"🔍 Export-Daten: project_id={project_id}, export_type={export_type}")
        print(f"🔍 Simulationsdaten: {bool(simulation_data)}")
        print(f"🔍 Dashboard-Daten: {bool(dashboard_data)}")
        
        if not project_id:
            print("❌ Projekt-ID fehlt")
            return jsonify({'error': 'Projekt-ID fehlt'}), 400
        
        # Projekt-Daten laden
        from models import Project
        project = Project.query.get(project_id)
        
        if not project:
            return jsonify({'error': 'Projekt nicht gefunden'}), 404
        
        # Projekt-Daten vorbereiten
        project_data = {
            'id': project.id,
            'name': project.name,
            'location': project.location or 'Nicht angegeben',
            'bess_size': project.bess_size or 0,
            'bess_power': project.bess_power or 0,
            'pv_power': project.pv_power or 0,
            'hydro_power': project.hydro_power or 0
        }
        
        # PDF-Exporter initialisieren
        pdf_exporter = BESSPDFExporter()
        
        # PDF generieren basierend auf Export-Typ
        print(f"🔄 Starte PDF-Generierung für Typ: {export_type}")
        
        if export_type == 'combined':
            pdf_path = pdf_exporter.export_combined_pdf(simulation_data, dashboard_data, project_data)
        elif export_type == 'simulation':
            pdf_path = pdf_exporter.export_simulation_pdf(simulation_data, project_data)
        elif export_type == 'dashboard':
            pdf_path = pdf_exporter.export_dashboard_pdf(dashboard_data, project_data)
        else:
            print(f"❌ Unbekannter Export-Typ: {export_type}")
            return jsonify({'error': 'Unbekannter Export-Typ'}), 400
        
        if not pdf_path:
            print("❌ PDF-Pfad ist leer")
            return jsonify({'error': 'Fehler bei der PDF-Generierung'}), 500
        
        print(f"✅ PDF erfolgreich generiert: {pdf_path}")
        
        # PDF-Datei senden
        filename = f"BESS_{export_type.title()}_{project.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        print(f"📤 Sende PDF-Datei: {filename}")
        
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        print(f"❌ Fehler beim PDF-Export: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Fehler beim PDF-Export: {str(e)}'}), 500

@api_bp.route('/projects')
def get_projects():
    """Alle Projekte abrufen"""
    try:
        from models import Project
        projects = Project.query.all()
        
        projects_data = []
        for project in projects:
            projects_data.append({
                'id': project.id,
                'name': project.name,
                'location': project.location,
                'bess_size': project.bess_size,
                'bess_power': project.bess_power,
                'pv_power': project.pv_power,
                'hydro_power': project.hydro_power
            })
        
        return jsonify(projects_data)
        
    except Exception as e:
        return jsonify({'error': f'Fehler beim Laden der Projekte: {str(e)}'}), 500

@api_bp.route('/projects/<int:project_id>')
def get_project(project_id):
    """Ein spezifisches Projekt abrufen"""
    try:
        from models import Project
        project = Project.query.get(project_id)
        
        if not project:
            return jsonify({'error': 'Projekt nicht gefunden'}), 404
        
        project_data = {
            'id': project.id,
            'name': project.name,
            'location': project.location,
            'bess_size': project.bess_size,
            'bess_power': project.bess_power,
            'pv_power': project.pv_power,
            'hydro_power': project.hydro_power,
            'current_electricity_cost': project.current_electricity_cost,
            'daily_cycles': project.daily_cycles
        }
        
        return jsonify(project_data)
        
    except Exception as e:
        return jsonify({'error': f'Fehler beim Laden des Projekts: {str(e)}'}), 500
