#!/usr/bin/env python3
"""
Berechtigungs-System für BESS-Simulation
========================================

Definiert Berechtigungen und Decorators für die Benutzer-Rollen
"""

from functools import wraps
from flask import session, redirect, url_for, flash, request, abort
from models import User, Role, UserProject
from app import db

def get_current_user():
    """Gibt den aktuell angemeldeten Benutzer zurück"""
    if 'user_id' not in session:
        return None
    
    try:
        return User.query.get(session['user_id'])
    except:
        return None

def login_required(f):
    """Decorator für Routen, die eine Anmeldung erfordern"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            flash("Bitte melden Sie sich an, um diese Seite zu sehen.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function

def permission_required(permission):
    """Decorator für Routen, die eine bestimmte Berechtigung erfordern"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if not user:
                flash("Bitte melden Sie sich an, um diese Seite zu sehen.", "warning")
                return redirect(url_for("auth.login"))
            
            if not user.has_permission(permission):
                flash("Sie haben keine Berechtigung für diese Aktion.", "error")
                return redirect(url_for("main.dashboard"))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """Decorator für Routen, die Admin-Berechtigung erfordern"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            flash("Bitte melden Sie sich an, um diese Seite zu sehen.", "warning")
            return redirect(url_for("auth.login"))
        
        if not user.is_admin():
            flash("Sie haben keine Administrator-Berechtigung.", "error")
            return redirect(url_for("main.dashboard"))
        
        return f(*args, **kwargs)
    return decorated_function

def project_permission_required(permission_level='read'):
    """Decorator für Routen, die Projekt-spezifische Berechtigungen erfordern"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if not user:
                flash("Bitte melden Sie sich an, um diese Seite zu sehen.", "warning")
                return redirect(url_for("auth.login"))
            
            # Admin hat immer Zugriff
            if user.is_admin():
                return f(*args, **kwargs)
            
            # Projekt-ID aus URL-Parametern oder Request-Daten extrahieren
            project_id = kwargs.get('project_id')
            if not project_id:
                # Versuche aus Form-Daten zu extrahieren
                project_id = request.form.get('project_id') or request.args.get('project_id')
            
            if not project_id:
                flash("Projekt-ID nicht gefunden.", "error")
                return redirect(url_for("main.projects"))
            
            # Prüfe Projekt-Berechtigung
            if not has_project_permission(user.id, project_id, permission_level):
                flash("Sie haben keine Berechtigung für dieses Projekt.", "error")
                return redirect(url_for("main.projects"))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def has_project_permission(user_id, project_id, permission_level='read'):
    """Prüft ob ein Benutzer eine bestimmte Berechtigung für ein Projekt hat"""
    try:
        # Admin hat immer alle Berechtigungen
        user = User.query.get(user_id)
        if user and user.is_admin():
            return True
        
        # Prüfe spezifische Projekt-Berechtigung
        user_project = UserProject.query.filter_by(
            user_id=user_id, 
            project_id=project_id
        ).first()
        
        if not user_project:
            return False
        
        # Berechtigungs-Hierarchie
        permission_hierarchy = {
            'read': 1,
            'write': 2,
            'admin': 3
        }
        
        required_level = permission_hierarchy.get(permission_level, 1)
        user_level = permission_hierarchy.get(user_project.permission_level, 0)
        
        return user_level >= required_level
        
    except Exception as e:
        print(f"Fehler beim Prüfen der Projekt-Berechtigung: {e}")
        return False

def get_user_projects(user_id):
    """Gibt alle Projekte zurück, auf die ein Benutzer Zugriff hat"""
    try:
        user = User.query.get(user_id)
        if not user:
            return []
        
        # Admin sieht alle Projekte
        if user.is_admin():
            from models import Project
            return Project.query.all()
        
        # Normale Benutzer sehen nur ihre zugewiesenen Projekte
        user_projects = UserProject.query.filter_by(user_id=user_id).all()
        project_ids = [up.project_id for up in user_projects]
        
        from models import Project
        return Project.query.filter(Project.id.in_(project_ids)).all()
        
    except Exception as e:
        print(f"Fehler beim Laden der Benutzer-Projekte: {e}")
        return []

def can_create_project(user_id):
    """Prüft ob ein Benutzer Projekte erstellen kann"""
    user = User.query.get(user_id)
    if not user:
        return False
    
    return user.has_permission('project_create')

def can_edit_project(user_id, project_id):
    """Prüft ob ein Benutzer ein Projekt bearbeiten kann"""
    user = User.query.get(user_id)
    if not user:
        return False
    
    # Admin kann alles bearbeiten
    if user.is_admin():
        return True
    
    # Prüfe Projekt-spezifische Berechtigung
    return has_project_permission(user_id, project_id, 'write')

def can_delete_project(user_id, project_id):
    """Prüft ob ein Benutzer ein Projekt löschen kann"""
    user = User.query.get(user_id)
    if not user:
        return False
    
    # Admin kann alles löschen
    if user.is_admin():
        return True
    
    # Prüfe Projekt-spezifische Berechtigung
    return has_project_permission(user_id, project_id, 'admin')

def can_manage_users(user_id):
    """Prüft ob ein Benutzer andere Benutzer verwalten kann"""
    user = User.query.get(user_id)
    if not user:
        return False
    
    return user.has_permission('user_manage')

def can_access_admin_panel(user_id):
    """Prüft ob ein Benutzer das Admin-Panel aufrufen kann"""
    user = User.query.get(user_id)
    if not user:
        return False
    
    return user.has_permission('system_admin')

# Berechtigungs-Konstanten
PERMISSIONS = {
    # Projekt-Berechtigungen
    'project_create': 'Projekte erstellen',
    'project_read': 'Projekte anzeigen',
    'project_update': 'Projekte bearbeiten',
    'project_delete': 'Projekte löschen',
    
    # Kunden-Berechtigungen
    'customer_create': 'Kunden erstellen',
    'customer_read': 'Kunden anzeigen',
    'customer_update': 'Kunden bearbeiten',
    'customer_delete': 'Kunden löschen',
    
    # Benutzer-Berechtigungen
    'user_create': 'Benutzer erstellen',
    'user_read': 'Benutzer anzeigen',
    'user_update': 'Benutzer bearbeiten',
    'user_delete': 'Benutzer löschen',
    'user_manage': 'Benutzer verwalten',
    
    # Rollen-Berechtigungen
    'role_create': 'Rollen erstellen',
    'role_read': 'Rollen anzeigen',
    'role_update': 'Rollen bearbeiten',
    'role_delete': 'Rollen löschen',
    
    # System-Berechtigungen
    'system_admin': 'System-Administration',
    'backup_manage': 'Backup-Verwaltung',
    'dashboard_admin': 'Admin-Dashboard',
    'dashboard_user': 'Benutzer-Dashboard',
    'dashboard_viewer': 'Viewer-Dashboard',
    
    # Simulation-Berechtigungen
    'simulation_run': 'Simulationen ausführen'
}

# Standard-Rollen-Definitionen
ROLE_DEFINITIONS = {
    'admin': {
        'name': 'Administrator',
        'description': 'Vollzugriff auf alle Funktionen des Systems',
        'permissions': [
            'project_create', 'project_read', 'project_update', 'project_delete',
            'customer_create', 'customer_read', 'customer_update', 'customer_delete',
            'user_create', 'user_read', 'user_update', 'user_delete', 'user_manage',
            'role_create', 'role_read', 'role_update', 'role_delete',
            'system_admin', 'backup_manage', 'dashboard_admin',
            'simulation_run'
        ]
    },
    'user': {
        'name': 'Benutzer',
        'description': 'Standard-Benutzer mit Projekt- und Kundenverwaltung',
        'permissions': [
            'project_create', 'project_read', 'project_update',
            'customer_create', 'customer_read', 'customer_update',
            'dashboard_user', 'simulation_run'
        ]
    },
    'viewer': {
        'name': 'Betrachter',
        'description': 'Nur-Lese-Zugriff auf Projekte und Kunden',
        'permissions': [
            'project_read', 'customer_read', 'dashboard_viewer'
        ]
    }
}
