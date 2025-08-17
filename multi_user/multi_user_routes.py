from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from multi_user.supabase_multi_user import SupabaseMultiUser
import uuid

# Blueprint erstellen
multi_user_bp = Blueprint('multi_user', __name__, url_prefix='/multi-user')

# Supabase Multi-User Instanz
supabase_multi = SupabaseMultiUser()

@multi_user_bp.route('/dashboard')
def dashboard():
    """Multi-User Dashboard"""
    # Für Demo-Zwecke verwenden wir eine Mock-User-ID
    # In der echten Implementierung würde diese aus der Supabase Session kommen
    user_id = session.get('user_id', str(uuid.uuid4()))
    
    try:
        projects = supabase_multi.get_user_projects(user_id)
        project_count = len(projects)
        
        # Zähle Simulationsergebnisse
        simulation_count = 0
        for project in projects:
            simulations = supabase_multi.get_simulation_results(project['id'], user_id)
            simulation_count += len(simulations)
        
        return render_template('multi_user/dashboard.html', 
                             project_count=project_count,
                             simulation_count=simulation_count,
                             recent_projects=projects[:5])
    except Exception as e:
        flash(f"Fehler beim Laden des Dashboards: {e}", "error")
        return render_template('multi_user/dashboard.html', 
                             project_count=0,
                             simulation_count=0,
                             recent_projects=[])

@multi_user_bp.route('/projects')
def projects():
    """Liste aller Projekte des Benutzers"""
    user_id = session.get('user_id', str(uuid.uuid4()))
    
    try:
        projects = supabase_multi.get_user_projects(user_id)
        return render_template('multi_user/projects.html', projects=projects)
    except Exception as e:
        flash(f"Fehler beim Laden der Projekte: {e}", "error")
        return render_template('multi_user/projects.html', projects=[])

@multi_user_bp.route('/projects/new', methods=['GET', 'POST'])
def new_project():
    """Neues Projekt erstellen"""
    if request.method == 'POST':
        user_id = session.get('user_id', str(uuid.uuid4()))
        
        project_data = {
            'name': request.form.get('name', ''),
            'description': request.form.get('description', ''),
            'bess_capacity_kwh': float(request.form.get('bess_capacity_kwh', 0)),
            'bess_power_kw': float(request.form.get('bess_power_kw', 0)),
            'solar_capacity_kw': float(request.form.get('solar_capacity_kw', 0)),
            'hydro_capacity_kw': float(request.form.get('hydro_capacity_kw', 0)),
            'investment_cost_per_kwh': float(request.form.get('investment_cost_per_kwh', 0)),
            'electricity_cost_per_kwh': float(request.form.get('electricity_cost_per_kwh', 0))
        }
        
        success, message, project_id = supabase_multi.create_project(user_id, project_data)
        
        if success:
            flash("Projekt erfolgreich erstellt!", "success")
            return redirect(url_for('multi_user.view_project', project_id=project_id))
        else:
            flash(f"Fehler beim Erstellen des Projekts: {message}", "error")
    
    return render_template('multi_user/new_project.html')

@multi_user_bp.route('/projects/<project_id>')
def view_project(project_id):
    """Projekt anzeigen"""
    user_id = session.get('user_id', str(uuid.uuid4()))
    
    try:
        project = supabase_multi.get_project_by_id(project_id, user_id)
        if not project:
            flash("Projekt nicht gefunden!", "error")
            return redirect(url_for('multi_user.projects'))
        
        simulations = supabase_multi.get_simulation_results(project_id, user_id)
        
        return render_template('multi_user/view_project.html', 
                             project=project, 
                             simulations=simulations)
    except Exception as e:
        flash(f"Fehler beim Laden des Projekts: {e}", "error")
        return redirect(url_for('multi_user.projects'))

@multi_user_bp.route('/projects/<project_id>/edit', methods=['GET', 'POST'])
def edit_project(project_id):
    """Projekt bearbeiten"""
    user_id = session.get('user_id', str(uuid.uuid4()))
    
    try:
        project = supabase_multi.get_project_by_id(project_id, user_id)
        if not project:
            flash("Projekt nicht gefunden!", "error")
            return redirect(url_for('multi_user.projects'))
        
        if request.method == 'POST':
            project_data = {
                'name': request.form.get('name', ''),
                'description': request.form.get('description', ''),
                'bess_capacity_kwh': float(request.form.get('bess_capacity_kwh', 0)),
                'bess_power_kw': float(request.form.get('bess_power_kw', 0)),
                'solar_capacity_kw': float(request.form.get('solar_capacity_kw', 0)),
                'hydro_capacity_kw': float(request.form.get('hydro_capacity_kw', 0)),
                'investment_cost_per_kwh': float(request.form.get('investment_cost_per_kwh', 0)),
                'electricity_cost_per_kwh': float(request.form.get('electricity_cost_per_kwh', 0))
            }
            
            success, message = supabase_multi.update_project(project_id, user_id, project_data)
            
            if success:
                flash("Projekt erfolgreich aktualisiert!", "success")
                return redirect(url_for('multi_user.view_project', project_id=project_id))
            else:
                flash(f"Fehler beim Aktualisieren des Projekts: {message}", "error")
        
        return render_template('multi_user/edit_project.html', project=project)
    except Exception as e:
        flash(f"Fehler beim Laden des Projekts: {e}", "error")
        return redirect(url_for('multi_user.projects'))

@multi_user_bp.route('/projects/<project_id>/delete', methods=['POST'])
def delete_project(project_id):
    """Projekt löschen"""
    user_id = session.get('user_id', str(uuid.uuid4()))
    
    try:
        success, message = supabase_multi.delete_project(project_id, user_id)
        
        if success:
            flash("Projekt erfolgreich gelöscht!", "success")
        else:
            flash(f"Fehler beim Löschen des Projekts: {message}", "error")
    except Exception as e:
        flash(f"Fehler beim Löschen des Projekts: {e}", "error")
    
    return redirect(url_for('multi_user.projects'))

@multi_user_bp.route('/customers')
def customers():
    """Liste aller Kunden des Benutzers (Platzhalter)"""
    return render_template('multi_user/customers.html', customers=[])

@multi_user_bp.route('/customers/new', methods=['GET', 'POST'])
def new_customer():
    """Neuen Kunden erstellen (Platzhalter)"""
    if request.method == 'POST':
        flash("Kunden-Funktionalität wird noch implementiert!", "info")
        return redirect(url_for('multi_user.customers'))
    
    return render_template('multi_user/new_customer.html')

@multi_user_bp.route('/projects/<project_id>/load-profiles')
def load_profiles(project_id):
    """Lastprofile eines Projekts anzeigen (Platzhalter)"""
    user_id = session.get('user_id', str(uuid.uuid4()))
    
    try:
        project = supabase_multi.get_project_by_id(project_id, user_id)
        if not project:
            flash("Projekt nicht gefunden!", "error")
            return redirect(url_for('multi_user.projects'))
        
        return render_template('multi_user/load_profiles.html', 
                             project=project, 
                             load_profiles=[])
    except Exception as e:
        flash(f"Fehler beim Laden der Lastprofile: {e}", "error")
        return redirect(url_for('multi_user.projects'))

@multi_user_bp.route('/projects/<project_id>/load-profiles/new', methods=['GET', 'POST'])
def new_load_profile(project_id):
    """Neues Lastprofil erstellen (Platzhalter)"""
    user_id = session.get('user_id', str(uuid.uuid4()))
    
    try:
        project = supabase_multi.get_project_by_id(project_id, user_id)
        if not project:
            flash("Projekt nicht gefunden!", "error")
            return redirect(url_for('multi_user.projects'))
        
        if request.method == 'POST':
            flash("Lastprofil-Funktionalität wird noch implementiert!", "info")
            return redirect(url_for('multi_user.load_profiles', project_id=project_id))
        
        return render_template('multi_user/new_load_profile.html', project=project)
    except Exception as e:
        flash(f"Fehler beim Laden des Projekts: {e}", "error")
        return redirect(url_for('multi_user.projects'))

@multi_user_bp.route('/projects/<project_id>/simulate', methods=['GET', 'POST'])
def simulate_project(project_id):
    """Projekt simulieren (Platzhalter)"""
    user_id = session.get('user_id', str(uuid.uuid4()))
    
    try:
        project = supabase_multi.get_project_by_id(project_id, user_id)
        if not project:
            flash("Projekt nicht gefunden!", "error")
            return redirect(url_for('multi_user.projects'))
        
        if request.method == 'POST':
            # Dummy-Simulation für Demo-Zwecke
            simulation_data = {
                'total_cost': 50000.0,
                'total_savings': 15000.0,
                'payback_period_years': 3.33,
                'simulation_details': {
                    'bess_utilization': 85.5,
                    'peak_shaving_efficiency': 92.3,
                    'energy_savings_kwh': 15000
                }
            }
            
            success, message, result_id = supabase_multi.save_simulation_result(
                user_id, project_id, simulation_data
            )
            
            if success:
                flash("Simulation erfolgreich durchgeführt und gespeichert!", "success")
            else:
                flash(f"Fehler bei der Simulation: {message}", "error")
            
            return redirect(url_for('multi_user.view_project', project_id=project_id))
        
        return render_template('multi_user/simulate_project.html', project=project)
    except Exception as e:
        flash(f"Fehler beim Laden des Projekts: {e}", "error")
        return redirect(url_for('multi_user.projects'))

# API Endpoints
@multi_user_bp.route('/api/projects', methods=['GET', 'POST'])
def api_projects():
    """API für Projekte"""
    user_id = session.get('user_id', str(uuid.uuid4()))
    
    if request.method == 'GET':
        try:
            projects = supabase_multi.get_user_projects(user_id)
            return jsonify({'success': True, 'data': projects})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            project_data = request.get_json()
            success, message, project_id = supabase_multi.create_project(user_id, project_data)
            
            if success:
                return jsonify({'success': True, 'project_id': project_id, 'message': message})
            else:
                return jsonify({'success': False, 'error': message}), 400
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

@multi_user_bp.route('/api/simulation-results/<project_id>', methods=['GET'])
def api_simulation_results(project_id):
    """API für Simulationsergebnisse"""
    user_id = session.get('user_id', str(uuid.uuid4()))
    
    try:
        results = supabase_multi.get_simulation_results(project_id, user_id)
        return jsonify({'success': True, 'data': results})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
