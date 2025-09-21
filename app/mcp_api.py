#!/usr/bin/env python3
"""
MCP API Endpoints für GUI-Integration
Bietet REST-API für MCP-Tools über Flask
"""

from flask import Blueprint, request, jsonify
import json
import sys
import os

# BESS-Simulation Pfad hinzufügen
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# MCP-Tools importieren
try:
    from mcp_server import (
        prices_get_spotcurve, 
        prices_get_awattar, 
        bess_read_soc, 
        bess_set_mode, 
        sim_run_dispatch, 
        read_pv_load, 
        db_project
    )
    MCP_TOOLS_AVAILABLE = True
except ImportError as e:
    MCP_TOOLS_AVAILABLE = False
    print(f"Warnung: MCP-Tools nicht verfügbar: {e}")

# Blueprint erstellen
mcp_api = Blueprint('mcp_api', __name__, url_prefix='/api/mcp')

def _error_response(message, status_code=500):
    """Standardisierte Fehler-Antwort"""
    return jsonify({"error": message, "status": "error"}), status_code

def _success_response(data, message="Success"):
    """Standardisierte Erfolgs-Antwort"""
    return jsonify({"data": data, "status": "success", "message": message})

@mcp_api.route('/dispatch', methods=['POST'])
def api_dispatch():
    """API-Endpoint für Dispatch-Simulation"""
    if not MCP_TOOLS_AVAILABLE:
        return _error_response("MCP-Tools nicht verfügbar")
    
    try:
        data = request.get_json()
        if not data:
            return _error_response("Keine Daten empfangen", 400)
        
        # Parameter validieren
        required_params = ['capacity_mwh', 'price_spread_eur_mwh']
        for param in required_params:
            if param not in data:
                return _error_response(f"Parameter '{param}' fehlt", 400)
        
        # Dispatch-Simulation ausführen
        params_json = json.dumps(data)
        result = sim_run_dispatch(params_json)
        
        return _success_response(result, "Dispatch-Simulation erfolgreich")
        
    except Exception as e:
        return _error_response(f"Dispatch-Fehler: {str(e)}")

@mcp_api.route('/soc', methods=['GET'])
def api_soc():
    """API-Endpoint für SOC-Wert"""
    if not MCP_TOOLS_AVAILABLE:
        return _error_response("MCP-Tools nicht verfügbar")
    
    try:
        soc = bess_read_soc()
        return _success_response({"soc": soc}, f"SOC-Wert: {soc}%")
        
    except Exception as e:
        return _error_response(f"SOC-Fehler: {str(e)}")

@mcp_api.route('/spot-prices', methods=['GET'])
def api_spot_prices():
    """API-Endpoint für Spotpreise"""
    if not MCP_TOOLS_AVAILABLE:
        return _error_response("MCP-Tools nicht verfügbar")
    
    try:
        date = request.args.get('date')
        if not date:
            from datetime import datetime
            date = datetime.now().strftime("%Y-%m-%d")
        
        result = prices_get_spotcurve(date)
        return _success_response(result, f"Spotpreise für {date}")
        
    except Exception as e:
        return _error_response(f"Spotpreise-Fehler: {str(e)}")

@mcp_api.route('/awattar', methods=['GET'])
def api_awattar():
    """API-Endpoint für aWATTar-Preise"""
    if not MCP_TOOLS_AVAILABLE:
        return _error_response("MCP-Tools nicht verfügbar")
    
    try:
        day = request.args.get('day')
        country = request.args.get('country', 'AT')
        
        if not day:
            from datetime import datetime
            day = datetime.now().strftime("%Y-%m-%d")
        
        result = prices_get_awattar(day, country)
        return _success_response(result, f"aWATTar-Preise für {day}")
        
    except Exception as e:
        return _error_response(f"aWATTar-Fehler: {str(e)}")

@mcp_api.route('/pv-load', methods=['GET'])
def api_pv_load():
    """API-Endpoint für PV/Last-Daten"""
    if not MCP_TOOLS_AVAILABLE:
        return _error_response("MCP-Tools nicht verfügbar")
    
    try:
        day = request.args.get('day')
        if not day:
            from datetime import datetime
            day = datetime.now().strftime("%Y-%m-%d")
        
        result = read_pv_load(day)
        return _success_response(result, f"PV/Last-Daten für {day}")
        
    except Exception as e:
        return _error_response(f"PV/Last-Fehler: {str(e)}")

@mcp_api.route('/database', methods=['GET'])
def api_database():
    """API-Endpoint für Datenbank-Abfragen"""
    if not MCP_TOOLS_AVAILABLE:
        return _error_response("MCP-Tools nicht verfügbar")
    
    try:
        table = request.args.get('table', 'projects')
        limit = int(request.args.get('limit', 10))
        
        result = db_project(table, limit)
        return _success_response(result, f"Datenbank-Tabelle {table}")
        
    except Exception as e:
        return _error_response(f"Datenbank-Fehler: {str(e)}")

@mcp_api.route('/mode', methods=['POST'])
def api_set_mode():
    """API-Endpoint für BESS-Modus-Steuerung"""
    if not MCP_TOOLS_AVAILABLE:
        return _error_response("MCP-Tools nicht verfügbar")
    
    try:
        data = request.get_json()
        if not data or 'mode' not in data:
            return _error_response("Modus-Parameter fehlt", 400)
        
        mode = data['mode']
        if mode not in ['idle', 'charge', 'discharge']:
            return _error_response("Ungültiger Modus. Erlaubt: idle, charge, discharge", 400)
        
        result = bess_set_mode(mode)
        return _success_response({"mode": mode, "result": result}, f"Modus auf '{mode}' gesetzt")
        
    except Exception as e:
        return _error_response(f"Modus-Fehler: {str(e)}")

@mcp_api.route('/status', methods=['GET'])
def api_status():
    """API-Endpoint für System-Status"""
    try:
        status = {
            "mcp_tools": MCP_TOOLS_AVAILABLE,
            "database": True,  # Vereinfacht - könnte echte DB-Prüfung sein
            "dispatch_system": "demo_mode",  # Vereinfacht
            "timestamp": None
        }
        
        from datetime import datetime
        status["timestamp"] = datetime.now().isoformat()
        
        return _success_response(status, "System-Status")
        
    except Exception as e:
        return _error_response(f"Status-Fehler: {str(e)}")

# Demo-Endpoint für Tests
@mcp_api.route('/demo', methods=['GET'])
def api_demo():
    """Demo-Endpoint für Tests"""
    return _success_response({
        "message": "MCP API funktioniert!",
        "available_endpoints": [
            "POST /api/mcp/dispatch",
            "GET /api/mcp/soc", 
            "GET /api/mcp/spot-prices",
            "GET /api/mcp/awattar",
            "GET /api/mcp/pv-load",
            "GET /api/mcp/database",
            "POST /api/mcp/mode",
            "GET /api/mcp/status"
        ]
    }, "MCP API Demo")

