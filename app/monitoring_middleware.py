"""
BESS-Simulation Monitoring-Middleware
Professionelles Monitoring für alle HTTP-Requests und Performance-Metriken
"""

import time
import json
import traceback
from datetime import datetime
from functools import wraps
from flask import request, g, current_app, jsonify
from .logging_config import (
    log_request, log_error, log_security_event, 
    log_performance_metric, setup_app_logger
)

logger = setup_app_logger("monitoring")

class MonitoringMiddleware:
    """Haupt-Monitoring-Middleware für BESS-Simulation"""
    
    def __init__(self, app):
        self.app = app
        self.request_count = 0
        self.error_count = 0
        self.active_requests = 0
        
        # Middleware registrieren
        self.app.before_request(self.before_request)
        self.app.after_request(self.after_request)
        self.app.errorhandler(Exception)(self.handle_exception)
        
        logger.info("Monitoring-Middleware initialisiert")
    
    def before_request(self):
        """Vor jedem Request ausführen"""
        # Request-Zähler erhöhen
        self.request_count += 1
        self.active_requests += 1
        
        # Request-Start-Zeit speichern
        g.start_time = time.time()
        g.request_id = f"req_{self.request_count}_{int(time.time())}"
        
        # Request-Details loggen
        logger.debug(f"Request gestartet: {g.request_id} - {request.method} {request.path}")
        
        # Performance-Metrik für aktive Requests
        log_performance_metric(
            "active_requests",
            self.active_requests,
            tags={"request_id": g.request_id}
        )
    
    def after_request(self, response):
        """Nach jedem Request ausführen"""
        # Request-Zeit berechnen
        if hasattr(g, 'start_time'):
            response_time = time.time() - g.start_time
        else:
            response_time = 0
        
        # Aktive Requests reduzieren
        self.active_requests = max(0, self.active_requests - 1)
        
        # Request loggen
        user_id = getattr(g, 'user_id', None)
        log_request(
            request=request,
            response_time=response_time,
            status_code=response.status_code,
            user_id=user_id
        )
        
        # Performance-Metriken loggen
        log_performance_metric(
            "response_time",
            response_time,
            unit="seconds",
            tags={
                "method": request.method,
                "path": request.path,
                "status_code": response.status_code
            }
        )
        
        # Response-Header für Monitoring
        response.headers['X-Request-ID'] = getattr(g, 'request_id', 'unknown')
        response.headers['X-Response-Time'] = f"{response_time:.3f}s"
        response.headers['X-Request-Count'] = str(self.request_count)
        
        logger.debug(f"Request beendet: {getattr(g, 'request_id', 'unknown')} - {response_time:.3f}s")
        
        return response
    
    def handle_exception(self, exception):
        """Exception-Handler für alle unbehandelten Fehler"""
        # Fehler-Zähler erhöhen
        self.error_count += 1
        
        # Fehler-Details sammeln
        error_context = {
            'request_id': getattr(g, 'request_id', 'unknown'),
            'method': request.method,
            'path': request.path,
            'ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', 'Unknown'),
            'user_id': getattr(g, 'user_id', None)
        }
        
        # Fehler loggen
        log_error(exception, error_context, getattr(g, 'user_id', None))
        
        # Security-Events für bestimmte Fehler
        if hasattr(exception, 'code') and exception.code == 403:
            log_security_event(
                "access_denied",
                f"Zugriff verweigert: {request.path}",
                user_id=getattr(g, 'user_id', None),
                ip_address=request.remote_addr,
                severity="WARNING"
            )
        
        # Performance-Metrik für Fehler
        log_performance_metric(
            "error_rate",
            self.error_count / max(self.request_count, 1),
            unit="percentage",
            tags={"error_type": type(exception).__name__}
        )
        
        # Benutzerfreundliche Fehlermeldung
        if current_app.debug:
            return jsonify({
                'error': str(exception),
                'traceback': traceback.format_exc(),
                'request_id': getattr(g, 'request_id', 'unknown')
            }), 500
        else:
            return jsonify({
                'error': 'Ein interner Fehler ist aufgetreten',
                'request_id': getattr(g, 'request_id', 'unknown')
            }), 500

def monitor_endpoint(monitor_name=None):
    """Decorator für Endpoint-Monitoring"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            endpoint_name = monitor_name or f.__name__
            start_time = time.time()
            
            try:
                # Endpoint ausführen
                result = f(*args, **kwargs)
                
                # Erfolg loggen
                response_time = time.time() - start_time
                log_performance_metric(
                    f"endpoint_{endpoint_name}_success",
                    response_time,
                    unit="seconds",
                    tags={"endpoint": endpoint_name, "status": "success"}
                )
                
                return result
                
            except Exception as e:
                # Fehler loggen
                response_time = time.time() - start_time
                log_performance_metric(
                    f"endpoint_{endpoint_name}_error",
                    response_time,
                    unit="seconds",
                    tags={"endpoint": endpoint_name, "status": "error"}
                )
                
                # Fehler weiterwerfen
                raise
        
        return decorated_function
    return decorator

def track_user_activity(user_id):
    """User-Aktivität tracken"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # User-ID für Request setzen
            g.user_id = user_id
            
            # User-Aktivität loggen
            logger.info(f"User {user_id} aktiv: {request.method} {request.path}")
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def monitor_database_queries():
    """Datenbank-Query-Monitoring"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = f(*args, **kwargs)
                
                # Query-Zeit loggen
                query_time = time.time() - start_time
                log_performance_metric(
                    "database_query_time",
                    query_time,
                    unit="seconds",
                    tags={"function": f.__name__}
                )
                
                return result
                
            except Exception as e:
                # Datenbank-Fehler loggen
                query_time = time.time() - start_time
                log_performance_metric(
                    "database_query_error",
                    query_time,
                    unit="seconds",
                    tags={"function": f.__name__, "error": str(e)}
                )
                raise
        
        return decorated_function
    return decorator

def monitor_cache_operations():
    """Cache-Operation-Monitoring"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = f(*args, **kwargs)
                
                # Cache-Operation-Zeit loggen
                cache_time = time.time() - start_time
                log_performance_metric(
                    "cache_operation_time",
                    cache_time,
                    unit="seconds",
                    tags={"function": f.__name__}
                )
                
                return result
                
            except Exception as e:
                # Cache-Fehler loggen
                cache_time = time.time() - start_time
                log_performance_metric(
                    "cache_operation_error",
                    cache_time,
                    unit="seconds",
                    tags={"function": f.__name__, "error": str(e)}
                )
                raise
        
        return decorated_function
    return decorator

# Globale Monitoring-Instanz
monitoring = None

def init_monitoring(app):
    """Monitoring für Flask-App initialisieren"""
    global monitoring
    monitoring = MonitoringMiddleware(app)
    logger.info("Monitoring für Flask-App initialisiert")
    return monitoring

def get_monitoring_stats():
    """Aktuelle Monitoring-Statistiken abrufen"""
    if monitoring:
        return {
            'total_requests': monitoring.request_count,
            'active_requests': monitoring.active_requests,
            'error_count': monitoring.error_count,
            'error_rate': monitoring.error_count / max(monitoring.request_count, 1),
            'uptime': time.time() - getattr(monitoring, '_start_time', time.time())
        }
    return {}
