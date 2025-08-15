"""
BESS-Simulation Authentication Routes
====================================

Flask-Routen für Benutzeranmeldung, Registrierung und Abmeldung.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from auth_module import bess_auth, login_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Anmeldeseite"""
    # Wenn bereits angemeldet, zum Dashboard weiterleiten
    if bess_auth.is_authenticated():
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        # Validierung
        if not email or not password:
            flash('Bitte füllen Sie alle Felder aus.', 'error')
            return render_template('auth/login.html')
        
        # Anmeldung versuchen
        success, message = bess_auth.login(email, password)
        
        if success:
            flash(message, 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash(message, 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registrierungsseite"""
    # Wenn bereits angemeldet, zum Dashboard weiterleiten
    if bess_auth.is_authenticated():
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validierung
        if not email or not password or not confirm_password:
            flash('Bitte füllen Sie alle Felder aus.', 'error')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Passwörter stimmen nicht überein.', 'error')
            return render_template('auth/register.html')
        
        if len(password) < 6:
            flash('Passwort muss mindestens 6 Zeichen lang sein.', 'error')
            return render_template('auth/register.html')
        
        # Registrierung versuchen
        success, message = bess_auth.register(email, password)
        
        if success:
            flash(message, 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(message, 'error')
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Abmeldung"""
    bess_auth.logout()
    flash('Sie wurden erfolgreich abgemeldet.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
@login_required
def profile():
    """Benutzerprofil"""
    user = bess_auth.get_current_user()
    return render_template('auth/profile.html', user=user)
