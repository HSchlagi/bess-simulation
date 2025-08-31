"""
BESS-Simulation Logging-Konfiguration
Professionelles Logging-System mit verschiedenen Log-Levels und Formaten
"""

import os
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path

# Log-Verzeichnisse erstellen
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Log-Dateien
APP_LOG = LOG_DIR / "bess_simulation.log"
ERROR_LOG = LOG_DIR / "errors.log"
ACCESS_LOG = LOG_DIR / "access.log"
PERFORMANCE_LOG = LOG_DIR / "performance.log"
SECURITY_LOG = LOG_DIR / "security.log"

# Log-Formate
DETAILED_FORMAT = logging.Formatter(
    '%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-20s | %(lineno)-4d | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

SIMPLE_FORMAT = logging.Formatter(
    '%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
    datefmt='%H:%M:%S'
)

JSON_FORMAT = logging.Formatter(
    '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "function": "%(funcName)s", "line": %(lineno)d, "message": "%(message)s"}',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def setup_logging():
    """Haupt-Logging-System einrichten"""
    
    # Root-Logger konfigurieren
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Bestehende Handler entfernen
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console-Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(SIMPLE_FORMAT)
    root_logger.addHandler(console_handler)
    
    # Haupt-Log-Datei
    file_handler = logging.handlers.RotatingFileHandler(
        APP_LOG,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(DETAILED_FORMAT)
    root_logger.addHandler(file_handler)
    
    # Error-Log-Datei
    error_handler = logging.handlers.RotatingFileHandler(
        ERROR_LOG,
        maxBytes=5*1024*1024,   # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(DETAILED_FORMAT)
    root_logger.addHandler(error_handler)
    
    return root_logger

def setup_app_logger(name="bess_simulation"):
    """Anwendungsspezifischen Logger einrichten"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Verhindere doppelte Handler
    if not logger.handlers:
        # App-spezifische Log-Datei
        app_handler = logging.handlers.RotatingFileHandler(
            APP_LOG,
            maxBytes=10*1024*1024,
            backupCount=5,
            encoding='utf-8'
        )
        app_handler.setLevel(logging.DEBUG)
        app_handler.setFormatter(DETAILED_FORMAT)
        logger.addHandler(app_handler)
    
    return logger

def setup_access_logger():
    """Access-Logger für HTTP-Requests"""
    access_logger = logging.getLogger("access")
    access_logger.setLevel(logging.INFO)
    
    if not access_logger.handlers:
        access_handler = logging.handlers.RotatingFileHandler(
            ACCESS_LOG,
            maxBytes=5*1024*1024,
            backupCount=3,
            encoding='utf-8'
        )
        access_handler.setLevel(logging.INFO)
        access_handler.setFormatter(SIMPLE_FORMAT)
        access_logger.addHandler(access_handler)
    
    return access_logger

def setup_performance_logger():
    """Performance-Logger für Metriken"""
    perf_logger = logging.getLogger("performance")
    perf_logger.setLevel(logging.INFO)
    
    if not perf_logger.handlers:
        perf_handler = logging.handlers.RotatingFileHandler(
            PERFORMANCE_LOG,
            maxBytes=5*1024*1024,
            backupCount=3,
            encoding='utf-8'
        )
        perf_handler.setLevel(logging.INFO)
        perf_handler.setFormatter(JSON_FORMAT)
        perf_logger.addHandler(perf_handler)
    
    return perf_logger

def setup_security_logger():
    """Security-Logger für Sicherheitsereignisse"""
    security_logger = logging.getLogger("security")
    security_logger.setLevel(logging.WARNING)
    
    if not security_logger.handlers:
        security_handler = logging.handlers.RotatingFileHandler(
            SECURITY_LOG,
            maxBytes=2*1024*1024,  # 2MB
            backupCount=5,
            encoding='utf-8'
        )
        security_handler.setLevel(logging.WARNING)
        security_handler.setFormatter(DETAILED_FORMAT)
        security_logger.addHandler(security_handler)
    
    return security_logger

def log_request(request, response_time=None, status_code=None, user_id=None):
    """HTTP-Request loggen"""
    access_logger = setup_access_logger()
    
    # Request-Details sammeln
    log_data = {
        'timestamp': datetime.now().isoformat(),
        'method': request.method,
        'path': request.path,
        'ip': request.remote_addr,
        'user_agent': request.headers.get('User-Agent', 'Unknown'),
        'status_code': status_code or 200,
        'response_time': f"{response_time:.3f}s" if response_time else None,
        'user_id': user_id,
        'query_params': dict(request.args),
        'content_length': request.content_length or 0
    }
    
    # Log-Level basierend auf Status-Code
    if status_code and status_code >= 400:
        access_logger.warning(f"HTTP {status_code}: {request.method} {request.path} - {log_data}")
    else:
        access_logger.info(f"HTTP {status_code}: {request.method} {request.path} - {log_data}")

def log_error(error, context=None, user_id=None):
    """Fehler loggen"""
    error_logger = logging.getLogger("errors")
    
    error_data = {
        'timestamp': datetime.now().isoformat(),
        'error_type': type(error).__name__,
        'error_message': str(error),
        'context': context or {},
        'user_id': user_id
    }
    
    error_logger.error(f"Error: {error_data}")

def log_security_event(event_type, details, user_id=None, ip_address=None, severity="INFO"):
    """Sicherheitsereignis loggen"""
    security_logger = setup_security_logger()
    
    security_data = {
        'timestamp': datetime.now().isoformat(),
        'event_type': event_type,
        'details': details,
        'user_id': user_id,
        'ip_address': ip_address,
        'severity': severity
    }
    
    if severity == "CRITICAL":
        security_logger.critical(f"Security Event: {security_data}")
    elif severity == "ERROR":
        security_logger.error(f"Security Event: {security_data}")
    elif severity == "WARNING":
        security_logger.warning(f"Security Event: {security_data}")
    else:
        security_logger.info(f"Security Event: {security_data}")

def log_performance_metric(metric_name, value, unit=None, tags=None):
    """Performance-Metrik loggen"""
    perf_logger = setup_performance_logger()
    
    perf_data = {
        'timestamp': datetime.now().isoformat(),
        'metric_name': metric_name,
        'value': value,
        'unit': unit,
        'tags': tags or {}
    }
    
    perf_logger.info(f"Performance: {perf_data}")

# Logging-System initialisieren
if __name__ == "__main__":
    setup_logging()
    logger = setup_app_logger()
    logger.info("BESS-Simulation Logging-System initialisiert")
