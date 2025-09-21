#!/usr/bin/env python3
"""
MCP Dispatch Adapter für BESS-Simulation
Intelligente Brücke zwischen MCP-Server und echter BESS-Simulation

Features:
- Nahtlose Integration mit advanced_dispatch_system.py
- Parameter-Mapping für MCP-Tools
- KPI-Extraktion für Cursor AI
- Fehlerbehandlung und Logging
"""

import sys
import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

# BESS-Simulation Module importieren
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from advanced_dispatch_system import (
        AdvancedDispatchSystem, 
        DispatchParameters,
        MarketType,
        GridServiceType
    )
    from models import Project, BatteryConfig
    from economic_analysis_enhanced import EconomicAnalysisEnhanced
    DISPATCH_SYSTEM_AVAILABLE = True
except ImportError as e:
    DISPATCH_SYSTEM_AVAILABLE = False
    print(f"Warnung: BESS-Simulation Module nicht verfügbar: {e}")

# Logging konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPDispatchAdapter:
    """Intelligenter Adapter für MCP-Dispatch-Integration"""
    
    def __init__(self, db_path: str = "instance/bess.db"):
        self.db_path = db_path
        self.dispatch_system = None
        
        if DISPATCH_SYSTEM_AVAILABLE:
            try:
                self.dispatch_system = AdvancedDispatchSystem()
                logger.info("Advanced Dispatch System erfolgreich initialisiert")
            except Exception as e:
                logger.error(f"Fehler beim Initialisieren des Dispatch Systems: {e}")
    
    def _get_project_data(self, project_id: int = 1) -> Optional[Dict[str, Any]]:
        """Lade Projekt-Daten aus der Datenbank"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Projekt-Daten laden
            cursor.execute("""
                SELECT p.*, bc.* FROM projects p
                LEFT JOIN battery_configs bc ON p.id = bc.project_id
                WHERE p.id = ?
            """, (project_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
                
            project_data = dict(row)
            conn.close()
            return project_data
            
        except Exception as e:
            logger.error(f"Fehler beim Laden der Projekt-Daten: {e}")
            return None
    
    def _map_mcp_params_to_dispatch(self, mcp_params: Dict[str, Any]) -> Dict[str, Any]:
        """Mappe MCP-Parameter auf Dispatch-System Parameter"""
        
        # Standard-Werte aus Projekt-Daten
        project_data = self._get_project_data()
        if not project_data:
            project_data = {}
        
        # Parameter-Mapping
        dispatch_params = {
            # Batterie-Konfiguration
            "capacity_mwh": mcp_params.get("capacity_mwh", project_data.get("capacity_mwh", 0.2)),
            "power_mw": mcp_params.get("power_mw", project_data.get("power_mw", 0.1)),
            "efficiency": mcp_params.get("efficiency", project_data.get("efficiency", 0.9)),
            "cycles_limit_per_day": mcp_params.get("cycles_limit_per_day", 2.0),
            
            # Wirtschaftliche Parameter
            "price_spread_eur_mwh": mcp_params.get("price_spread_eur_mwh", 80),
            "investment_cost_eur_mwh": mcp_params.get("investment_cost_eur_mwh", 300000),
            "om_cost_eur_mwh_year": mcp_params.get("om_cost_eur_mwh_year", 15000),
            
            # Markt-Parameter
            "market_type": mcp_params.get("market_type", "spot"),
            "grid_services_enabled": mcp_params.get("grid_services_enabled", True),
            
            # Zeitraum
            "start_date": mcp_params.get("start_date", datetime.now().strftime("%Y-%m-%d")),
            "end_date": mcp_params.get("end_date", (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")),
        }
        
        return dispatch_params
    
    def _extract_kpis(self, dispatch_result: Any) -> Dict[str, Any]:
        """Extrahiere KPIs aus Dispatch-Ergebnis"""
        
        kpis = {
            "profit_eur": 0.0,
            "cycles_per_day": 0.0,
            "autarky_pct": 0.0,
            "revenue_eur": 0.0,
            "costs_eur": 0.0,
            "roi_pct": 0.0,
            "payback_years": 0.0,
            "status": "success"
        }
        
        try:
            if hasattr(dispatch_result, 'to_dict'):
                result_dict = dispatch_result.to_dict()
            elif isinstance(dispatch_result, dict):
                result_dict = dispatch_result
            else:
                result_dict = {}
            
            # KPI-Extraktion
            kpis.update({
                "profit_eur": float(result_dict.get("total_profit", 0)),
                "cycles_per_day": float(result_dict.get("avg_cycles_per_day", 0)),
                "autarky_pct": float(result_dict.get("autarky_percentage", 0)),
                "revenue_eur": float(result_dict.get("total_revenue", 0)),
                "costs_eur": float(result_dict.get("total_costs", 0)),
                "roi_pct": float(result_dict.get("roi_percentage", 0)),
                "payback_years": float(result_dict.get("payback_years", 0)),
            })
            
        except Exception as e:
            logger.error(f"Fehler beim Extrahieren der KPIs: {e}")
            kpis["status"] = "error"
            kpis["error_message"] = str(e)
        
        return kpis

def run_dispatch(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Hauptfunktion für MCP-Dispatch-Integration
    
    Args:
        params: MCP-Parameter (JSON-String oder Dict)
        
    Returns:
        Dict mit KPIs für Cursor AI
    """
    
    # Parameter normalisieren
    if isinstance(params, str):
        try:
            params = json.loads(params)
        except json.JSONDecodeError:
            params = {}
    elif params is None:
        params = {}
    
    logger.info(f"MCP Dispatch aufgerufen mit Parametern: {params}")
    
    # Adapter initialisieren
    adapter = MCPDispatchAdapter()
    
    if not DISPATCH_SYSTEM_AVAILABLE:
        logger.warning("Dispatch-System nicht verfügbar, verwende Demo-Modus")
        return _demo_dispatch(params)
    
    if not adapter.dispatch_system:
        logger.warning("Dispatch-System nicht initialisiert, verwende Demo-Modus")
        return _demo_dispatch(params)
    
    try:
        # Parameter mappen
        dispatch_params = adapter._map_mcp_params_to_dispatch(params)
        logger.info(f"Gemappte Dispatch-Parameter: {dispatch_params}")
        
        # Dispatch-Simulation ausführen
        dispatch_result = adapter.dispatch_system.run_dispatch_simulation(dispatch_params)
        
        # KPIs extrahieren
        kpis = adapter._extract_kpis(dispatch_result)
        
        # Zusätzliche Metadaten
        kpis.update({
            "timestamp": datetime.now().isoformat(),
            "parameters_used": dispatch_params,
            "dispatch_system_version": "advanced_v2.0"
        })
        
        logger.info(f"Dispatch erfolgreich abgeschlossen: {kpis}")
        return kpis
        
    except Exception as e:
        logger.error(f"Fehler beim Ausführen des Dispatch: {e}")
        return {
            "profit_eur": 0.0,
            "cycles_per_day": 0.0,
            "autarky_pct": 0.0,
            "status": "error",
            "error_message": str(e),
            "timestamp": datetime.now().isoformat()
        }

def _demo_dispatch(params: Dict[str, Any]) -> Dict[str, Any]:
    """Demo-Dispatch für Fallback-Szenario"""
    
    # Einfache Demo-Berechnung
    capacity_mwh = params.get("capacity_mwh", 0.2)
    price_spread = params.get("price_spread_eur_mwh", 80)
    cycles_limit = params.get("cycles_limit_per_day", 1.0)
    
    # Demo-KPIs
    profit = 0.35 * price_spread * cycles_limit * capacity_mwh
    revenue = profit * 1.2
    costs = profit * 0.3
    
    return {
        "profit_eur": round(profit, 2),
        "cycles_per_day": cycles_limit,
        "autarky_pct": 65.0,
        "revenue_eur": round(revenue, 2),
        "costs_eur": round(costs, 2),
        "roi_pct": 12.5,
        "payback_years": 8.0,
        "status": "demo_mode",
        "notes": "Demo-Modus - echte Simulation nicht verfügbar",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    # Test der MCP-Integration
    test_params = {
        "capacity_mwh": 0.5,
        "price_spread_eur_mwh": 100,
        "cycles_limit_per_day": 1.5
    }
    
    result = run_dispatch(test_params)
    print("MCP Dispatch Test:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
