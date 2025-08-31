#!/usr/bin/env python3
"""
Lokales Authentifizierungs-System für BESS-Simulation
=====================================================

Ersetzt das Supabase-System für lokale Benutzer-Verwaltung
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import User, Role
from permissions import get_current_user
from app import db
from datetime import datetime

auth_local_bp = Blueprint('auth_local', __name__)

@auth_local_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Benutzer-Anmeldung"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash("Bitte geben Sie E-Mail und Passwort ein.", "error")
            return render_template('auth/login.html')
        
        try:
            # Benutzer in der Datenbank suchen
            user = User.query.filter_by(email=email).first()
            
            if user and user.check_password(password):
                if not user.is_active:
                    flash("Ihr Account ist deaktiviert. Bitte kontaktieren Sie den Administrator.", "error")
                    return render_template('auth/login.html')
                
                # Login erfolgreich - Session setzen
                session['user_id'] = user.id
                session['username'] = user.username
                session['email'] = user.email
                session['role'] = user.role.name if user.role else 'user'
                
                # Letzten Login aktualisieren
                user.last_login = datetime.utcnow()
                db.session.commit()
                
                flash(f"Willkommen zurück, {user.first_name or user.username}!", "success")
                return redirect(url_for("multi_user.dashboard"))
            else:
                flash("Ungültige E-Mail oder Passwort.", "error")
                
        except Exception as e:
            flash(f"Fehler bei der Anmeldung: {e}", "error")
    
    return render_template('auth/login.html')

@auth_local_bp.route('/logout')
def logout():
    """Benutzer-Abmeldung"""
    session.clear()
    flash("Sie wurden erfolgreich abgemeldet.", "success")
    return redirect(url_for("auth_local.login"))

@auth_local_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Benutzer-Registrierung (nur für Admins verfügbar)"""
    # Registrierung nur für Admins erlauben
    current_user = get_current_user()
    if not current_user or not current_user.is_admin():
        flash("Registrierung ist nur für Administratoren verfügbar.", "error")
        return redirect(url_for("auth_local.login"))
    
    if request.method == 'POST':
        try:
            # Form-Daten verarbeiten
            email = request.form.get('email')
            username = request.form.get('username')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            company = request.form.get('company')
            phone = request.form.get('phone')
            role_id = request.form.get('role_id')
            
            # Validierung
            if not all([email, username, password, confirm_password, role_id]):
                flash("Alle Pflichtfelder müssen ausgefüllt werden.", "error")
                return render_template('auth/register.html')
            
            if password != confirm_password:
                flash("Passwörter stimmen nicht überein.", "error")
                return render_template('auth/register.html')
            
            # Prüfe ob Benutzer bereits existiert
            if User.query.filter_by(email=email).first():
                flash("Ein Benutzer mit dieser E-Mail-Adresse existiert bereits.", "error")
                return render_template('auth/register.html')
            
            if User.query.filter_by(username=username).first():
                flash("Ein Benutzer mit diesem Benutzernamen existiert bereits.", "error")
                return render_template('auth/register.html')
            
            # Neuen Benutzer erstellen
            user = User(
                email=email,
                username=username,
                first_name=first_name,
                last_name=last_name,
                company=company,
                phone=phone,
                role_id=role_id,
                is_verified=True,
                is_active=True
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            flash("Benutzer erfolgreich registriert.", "success")
            return redirect(url_for("admin.users"))
            
        except Exception as e:
            flash(f"Fehler bei der Registrierung: {e}", "error")
            return render_template('auth/register.html')
    
    # GET-Request: Formular anzeigen
    roles = Role.query.all()
    return render_template('auth/register.html', roles=roles)

@auth_local_bp.route('/profile')
def profile():
    """Benutzer-Profil anzeigen"""
    user = get_current_user()
    if not user:
        flash("Bitte melden Sie sich an.", "warning")
        return redirect(url_for("auth_local.login"))
    
    return render_template('auth/profile.html', user=user)

@auth_local_bp.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    """Benutzer-Profil bearbeiten"""
    user = get_current_user()
    if not user:
        flash("Bitte melden Sie sich an.", "warning")
        return redirect(url_for("auth_local.login"))
    
    if request.method == 'POST':
        try:
            # Form-Daten verarbeiten
            user.first_name = request.form.get('first_name')
            user.last_name = request.form.get('last_name')
            user.company = request.form.get('company')
            user.phone = request.form.get('phone')
            
            # Passwort ändern (falls angegeben)
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            if new_password:
                if not current_password or not user.check_password(current_password):
                    flash("Aktuelles Passwort ist nicht korrekt.", "error")
                    return render_template('auth/edit_profile.html', user=user)
                
                if new_password != confirm_password:
                    flash("Neue Passwörter stimmen nicht überein.", "error")
                    return render_template('auth/edit_profile.html', user=user)
                
                user.set_password(new_password)
            
            db.session.commit()
            flash("Profil erfolgreich aktualisiert.", "success")
            return redirect(url_for("auth_local.profile"))
            
        except Exception as e:
            flash(f"Fehler beim Aktualisieren des Profils: {e}", "error")
    
    return render_template('auth/edit_profile.html', user=user)

@auth_local_bp.route('/change-password', methods=['GET', 'POST'])
def change_password():
    """Passwort ändern"""
    user = get_current_user()
    if not user:
        flash("Bitte melden Sie sich an.", "warning")
        return redirect(url_for("auth_local.login"))
    
    if request.method == 'POST':
        try:
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            # Validierung
            if not all([current_password, new_password, confirm_password]):
                flash("Alle Felder müssen ausgefüllt werden.", "error")
                return render_template('auth/change_password.html')
            
            if not user.check_password(current_password):
                flash("Aktuelles Passwort ist nicht korrekt.", "error")
                return render_template('auth/change_password.html')
            
            if new_password != confirm_password:
                flash("Neue Passwörter stimmen nicht überein.", "error")
                return render_template('auth/change_password.html')
            
            # Passwort ändern
            user.set_password(new_password)
            db.session.commit()
            
            flash("Passwort erfolgreich geändert.", "success")
            return redirect(url_for("auth_local.profile"))
            
        except Exception as e:
            flash(f"Fehler beim Ändern des Passworts: {e}", "error")
    
    return render_template('auth/change_password.html')
