#!/usr/bin/env python3
"""
Admin-Routen für BESS-Simulation
================================

Administrative Funktionen für Benutzer-Verwaltung und System-Management
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from models import User, Role, UserProject, Project, Customer
from permissions import admin_required, permission_required, get_current_user, can_manage_users
from app import db
import json
from datetime import datetime
import os

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@admin_required
def dashboard():
    """Admin-Dashboard Hauptseite"""
    try:
        # Statistiken sammeln
        stats = {
            'total_users': User.query.count(),
            'active_users': User.query.filter_by(is_active=True).count(),
            'total_projects': Project.query.count(),
            'total_simulations': 0  # TODO: Implementiere Simulation-Zählung
        }
        
        # System-Status
        system_status = {
            'last_backup': 'Heute 22:36',
            'disk_usage': '2.4 GB / 50 GB'
        }
        
        # Letzte Aktivitäten (Platzhalter)
        recent_activities = []
        
        return render_template('admin_dashboard.html', 
                             stats=stats, 
                             system_status=system_status,
                             recent_activities=recent_activities)
                             
    except Exception as e:
        flash(f"Fehler beim Laden des Admin-Dashboards: {e}", "error")
        return redirect(url_for("multi_user.dashboard"))

@admin_bp.route('/users')
@admin_required
def users():
    """Benutzer-Verwaltung"""
    try:
        users = User.query.all()
        roles = Role.query.all()
        
        return render_template('admin/users.html', users=users, roles=roles)
        
    except Exception as e:
        flash(f"Fehler beim Laden der Benutzer: {e}", "error")
        return redirect(url_for("multi_user.dashboard"))

@admin_bp.route('/users/new', methods=['GET', 'POST'])
@admin_required
def new_user():
    """Neuen Benutzer erstellen"""
    if request.method == 'POST':
        try:
            # Form-Daten verarbeiten
            email = request.form.get('email')
            username = request.form.get('username')
            password = request.form.get('password')
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            company = request.form.get('company')
            phone = request.form.get('phone')
            role_id = request.form.get('role_id')
            
            # Validierung
            if not email or not username or not password:
                flash("E-Mail, Benutzername und Passwort sind Pflichtfelder.", "error")
                return redirect(url_for("admin.new_user"))
            
            # Prüfe ob Benutzer bereits existiert
            if User.query.filter_by(email=email).first():
                flash("Ein Benutzer mit dieser E-Mail-Adresse existiert bereits.", "error")
                return redirect(url_for("admin.new_user"))
            
            if User.query.filter_by(username=username).first():
                flash("Ein Benutzer mit diesem Benutzernamen existiert bereits.", "error")
                return redirect(url_for("admin.new_user"))
            
            # Neuen Benutzer erstellen
            user = User(
                email=email,
                username=username,
                first_name=first_name,
                last_name=last_name,
                company=company,
                phone=phone,
                role_id=role_id if role_id else 1,  # Default-Rolle (ID 1) falls keine ausgewählt
                is_active='is_active' in request.form,
                is_verified='is_verified' in request.form
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            flash("Benutzer erfolgreich erstellt.", "success")
            return redirect(url_for("admin.users"))
            
        except Exception as e:
            flash(f"Fehler beim Erstellen des Benutzers: {e}", "error")
            return redirect(url_for("admin.new_user"))
    
    # GET-Request: Formular anzeigen
    roles = Role.query.all()
    return render_template('admin/new_user.html', roles=roles)

@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    """Benutzer bearbeiten"""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        try:
            # Form-Daten verarbeiten
            user.email = request.form.get('email')
            user.username = request.form.get('username')
            user.first_name = request.form.get('first_name')
            user.last_name = request.form.get('last_name')
            user.company = request.form.get('company')
            user.phone = request.form.get('phone')
            user.role_id = request.form.get('role_id')
            user.is_active = 'is_active' in request.form
            
            # Passwort ändern (falls angegeben)
            new_password = request.form.get('new_password')
            if new_password:
                user.set_password(new_password)
            
            db.session.commit()
            
            flash("Benutzer erfolgreich aktualisiert.", "success")
            return redirect(url_for("admin.users"))
            
        except Exception as e:
            flash(f"Fehler beim Aktualisieren des Benutzers: {e}", "error")
            return redirect(url_for("admin.edit_user", user_id=user_id))
    
    # GET-Request: Formular anzeigen
    roles = Role.query.all()
    return render_template('admin/edit_user.html', user=user, roles=roles)

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Benutzer löschen"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Verhindere Löschung des eigenen Accounts
        current_user = get_current_user()
        if user.id == current_user.id:
            flash("Sie können Ihren eigenen Account nicht löschen.", "error")
            return redirect(url_for("admin.users"))
        
        # Lösche Benutzer-Projekt-Zuweisungen
        UserProject.query.filter_by(user_id=user_id).delete()
        
        # Lösche Benutzer
        db.session.delete(user)
        db.session.commit()
        
        flash("Benutzer erfolgreich gelöscht.", "success")
        
    except Exception as e:
        flash(f"Fehler beim Löschen des Benutzers: {e}", "error")
    
    return redirect(url_for("admin.users"))

@admin_bp.route('/roles')
@admin_required
def roles():
    """Rollen-Verwaltung"""
    try:
        roles = Role.query.all()
        return render_template('admin/roles.html', roles=roles)
        
    except Exception as e:
        flash(f"Fehler beim Laden der Rollen: {e}", "error")
        return redirect(url_for("multi_user.dashboard"))

@admin_bp.route('/roles/<int:role_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_role(role_id):
    """Rolle bearbeiten"""
    role = Role.query.get_or_404(role_id)
    
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            description = request.form.get('description')
            permissions = request.form.getlist('permissions')
            
            if not name:
                flash("Rollenname ist erforderlich.", "error")
                return redirect(url_for("admin.edit_role", role_id=role_id))
            
            # Prüfe ob Name bereits von anderer Rolle verwendet wird
            existing_role = Role.query.filter_by(name=name).first()
            if existing_role and existing_role.id != role_id:
                flash("Eine Rolle mit diesem Namen existiert bereits.", "error")
                return redirect(url_for("admin.edit_role", role_id=role_id))
            
            # Rolle aktualisieren
            role.name = name
            role.description = description
            role.permissions = json.dumps(permissions)
            
            db.session.commit()
            
            flash("Rolle erfolgreich aktualisiert.", "success")
            return redirect(url_for("admin.roles"))
            
        except Exception as e:
            flash(f"Fehler beim Aktualisieren der Rolle: {e}", "error")
            return redirect(url_for("admin.edit_role", role_id=role_id))
    
    # GET-Request: Formular anzeigen
    from permissions import PERMISSIONS
    return render_template('admin/edit_role.html', role=role, permissions=PERMISSIONS)

@admin_bp.route('/roles/new', methods=['GET', 'POST'])
@admin_required
def new_role():
    """Neue Rolle erstellen"""
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            description = request.form.get('description')
            permissions = request.form.getlist('permissions')
            
            if not name:
                flash("Rollenname ist erforderlich.", "error")
                return redirect(url_for("admin.new_role"))
            
            # Prüfe ob Rolle bereits existiert
            if Role.query.filter_by(name=name).first():
                flash("Eine Rolle mit diesem Namen existiert bereits.", "error")
                return redirect(url_for("admin.new_role"))
            
            # Neue Rolle erstellen
            role = Role(
                name=name,
                description=description,
                permissions=json.dumps(permissions)
            )
            
            db.session.add(role)
            db.session.commit()
            
            flash("Rolle erfolgreich erstellt.", "success")
            return redirect(url_for("admin.roles"))
            
        except Exception as e:
            flash(f"Fehler beim Erstellen der Rolle: {e}", "error")
            return redirect(url_for("admin.new_role"))
    
    # GET-Request: Formular anzeigen
    from permissions import PERMISSIONS
    return render_template('admin/new_role.html', permissions=PERMISSIONS)

@admin_bp.route('/projects')
@admin_required
def projects():
    """Projekt-Berechtigungen verwalten"""
    try:
        projects = Project.query.all()
        users = User.query.all()
        
        # Projekt-Berechtigungen sammeln
        project_permissions = {}
        for project in projects:
            permissions = UserProject.query.filter_by(project_id=project.id).all()
            project_permissions[project.id] = permissions
        
        return render_template('admin/projects.html', 
                             projects=projects, 
                             users=users,
                             project_permissions=project_permissions)
        
    except Exception as e:
        flash(f"Fehler beim Laden der Projekt-Berechtigungen: {e}", "error")
        return redirect(url_for("admin.dashboard"))

@admin_bp.route('/projects/<int:project_id>/permissions', methods=['GET', 'POST'])
@admin_required
def project_permissions(project_id):
    """Projekt-Berechtigungen anzeigen und bearbeiten"""
    project = Project.query.get_or_404(project_id)
    
    if request.method == 'POST':
        try:
            # Bestehende Berechtigungen löschen
            UserProject.query.filter_by(project_id=project_id).delete()
            
            # Neue Berechtigungen hinzufügen
            user_ids = request.form.getlist('user_ids')
            permission_levels = request.form.getlist('permission_levels')
            
            for i, user_id in enumerate(user_ids):
                if user_id and permission_levels[i]:
                    user_project = UserProject(
                        user_id=user_id,
                        project_id=project_id,
                        permission_level=permission_levels[i]
                    )
                    db.session.add(user_project)
            
            db.session.commit()
            flash("Projekt-Berechtigungen erfolgreich aktualisiert.", "success")
            return redirect(url_for("admin.projects"))
            
        except Exception as e:
            flash(f"Fehler beim Aktualisieren der Projekt-Berechtigungen: {e}", "error")
    
    # GET-Request: Formular anzeigen
    users = User.query.all()
    current_permissions = UserProject.query.filter_by(project_id=project_id).all()
    
    return render_template('admin/project_permissions.html', 
                         project=project, 
                         users=users,
                         current_permissions=current_permissions)

@admin_bp.route('/system')
@admin_required
def system():
    """System-Einstellungen"""
    try:
        # System-Status sammeln
        system_status = {
            'last_backup': 'Heute 22:36',
            'disk_usage': '2.4 GB / 50 GB'
        }
        
        # System-Informationen sammeln
        system_info = {
            'database_size': '6.4 MB',
            'backup_count': len([f for f in os.listdir('backups') if f.endswith('.sql.gz')]) if os.path.exists('backups') else 0,
            'log_size': '2.1 MB',
            'uptime': '3 Tage, 12 Stunden'
        }
        
        return render_template('admin/system.html', system_status=system_status, system_info=system_info)
        
    except Exception as e:
        flash(f"Fehler beim Laden der System-Einstellungen: {e}", "error")
        return redirect(url_for("admin.dashboard"))

@admin_bp.route('/backup/now', methods=['POST'])
@admin_required
def backup_now():
    """Manuelles Backup erstellen"""
    try:
        # Backup-Script ausführen
        import subprocess
        result = subprocess.run(['python', 'backup_automation.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            flash("Backup erfolgreich erstellt.", "success")
        else:
            flash(f"Fehler beim Erstellen des Backups: {result.stderr}", "error")
            
    except Exception as e:
        flash(f"Fehler beim Erstellen des Backups: {e}", "error")
    
    return redirect(url_for("admin.system"))

@admin_bp.route('/logs')
@admin_required
def logs():
    """System-Logs anzeigen"""
    try:
        # Log-Dateien lesen
        log_files = ['backup.log', 'backup_automation.log']
        logs = {}
        
        for log_file in log_files:
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs[log_file] = f.read()
        
        return render_template('admin/logs.html', logs=logs)
        
    except Exception as e:
        flash(f"Fehler beim Laden der Logs: {e}", "error")
        return redirect(url_for("admin.dashboard"))

@admin_bp.route('/logs/clear', methods=['POST'])
@admin_required
def clear_logs():
    """Logs bereinigen"""
    try:
        log_files = ['backup.log', 'backup_automation.log']
        
        for log_file in log_files:
            if os.path.exists(log_file):
                # Log-Datei leeren
                with open(log_file, 'w', encoding='utf-8') as f:
                    f.write('')
        
        flash("Logs erfolgreich bereinigt.", "success")
        
    except Exception as e:
        flash(f"Fehler beim Bereinigen der Logs: {e}", "error")
    
    return redirect(url_for("admin.logs"))

# API-Endpoints für AJAX-Requests
@admin_bp.route('/api/users')
@admin_required
def api_users():
    """API für Benutzer-Liste"""
    try:
        users = User.query.all()
        user_list = []
        
        for user in users:
            user_list.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role.name if user.role else None,
                'is_active': user.is_active,
                'created_at': user.created_at.strftime('%d.%m.%Y') if user.created_at else None
            })
        
        return jsonify(user_list)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/stats')
@admin_required
def api_stats():
    """API für Admin-Statistiken"""
    try:
        stats = {
            'total_users': User.query.count(),
            'active_users': User.query.filter_by(is_active=True).count(),
            'total_projects': Project.query.count(),
            'total_customers': Customer.query.count(),
            'admin_users': User.query.join(Role).filter(Role.name == 'admin').count(),
            'user_users': User.query.join(Role).filter(Role.name == 'user').count(),
            'viewer_users': User.query.join(Role).filter(Role.name == 'viewer').count()
        }
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/performance')
@admin_required
def performance():
    """Performance-Dashboard"""
    try:
        return render_template('admin/performance.html')
    except Exception as e:
        flash(f"Fehler beim Laden des Performance-Dashboards: {e}", "error")
        return redirect(url_for("multi_user.dashboard"))
