#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minimaler Server-Start für BESS-Simulation ohne problematische Module
"""

import os
import sys

# Windows-Konsole auf UTF-8 setzen
if sys.platform == 'win32':
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleOutputCP(65001)  # UTF-8
    except:
        pass
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# Flask App direkt erstellen ohne problematische Module
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# Basis-Konfiguration
app.config['SECRET_KEY'] = 'bess-simulation-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/bess.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Einfache Route zum Testen
@app.route('/')
def index():
    return """
    <h1>BESS-Simulation Server</h1>
    <p>Server läuft erfolgreich!</p>
    <ul>
        <li><a href="/dashboard">Dashboard</a></li>
        <li><a href="/admin/dashboard">Admin Panel</a></li>
        <li><a href="/export/">Export Zentrum</a></li>
    </ul>
    """

@app.route('/dashboard')
def dashboard():
    return "<h1>Dashboard</h1><p>Dashboard wird geladen...</p>"

@app.route('/admin/dashboard')
def admin_dashboard():
    return "<h1>Admin Dashboard</h1><p>Admin Panel wird geladen...</p>"

@app.route('/export/')
def export_center():
    return "<h1>Export Zentrum</h1><p>Export Funktionen werden geladen...</p>"

if __name__ == '__main__':
    print("=" * 60)
    print("BESS-Simulation Server (Minimal) wird gestartet...")
    print("Dashboard: http://127.0.0.1:5050/dashboard")
    print("Admin: http://127.0.0.1:5050/admin/dashboard")
    print("Export: http://127.0.0.1:5050/export/")
    print("=" * 60)
    print("Server läuft... Drücken Sie Ctrl+C zum Beenden")
    print("=" * 60)
    
    app.run(debug=True, host='127.0.0.1', port=5050, use_reloader=False)








