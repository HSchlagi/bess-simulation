"""
BESS-Simulation Health-Check-System
Umfassende Überwachung aller Systemkomponenten
"""

import time
import sqlite3
import redis
import psutil
import os
from datetime import datetime, timedelta
from pathlib import Path
from .logging_config import setup_app_logger, log_performance_metric

logger = setup_app_logger("health_check")

class HealthChecker:
    """Haupt-Health-Checker für BESS-Simulation"""
    
    def __init__(self):
        self.checks = {}
        self.last_check = {}
        self.check_interval = 30  # Sekunden
        
    def register_check(self, name, check_function, interval=None):
        """Neuen Health-Check registrieren"""
        self.checks[name] = {
            'function': check_function,
            'interval': interval or self.check_interval,
            'last_run': 0,
            'status': 'unknown',
            'details': {}
        }
        logger.info(f"Health-Check registriert: {name}")
    
    def run_check(self, name):
        """Bestimmten Health-Check ausführen"""
        if name not in self.checks:
            return {'status': 'error', 'message': f'Check {name} nicht gefunden'}
        
        check = self.checks[name]
        current_time = time.time()
        
        # Prüfen ob Check ausgeführt werden soll
        if current_time - check['last_run'] < check['interval']:
            return check['details']
        
        try:
            # Check ausführen
            start_time = time.time()
            result = check['function']()
            execution_time = time.time() - start_time
            
            # Ergebnis speichern
            check['last_run'] = current_time
            check['status'] = result.get('status', 'unknown')
            check['details'] = result
            check['details']['execution_time'] = execution_time
            check['details']['last_check'] = datetime.now().isoformat()
            
            # Performance-Metrik loggen
            log_performance_metric(
                f"health_check_{name}_time",
                execution_time,
                unit="seconds",
                tags={"check_name": name, "status": result.get('status', 'unknown')}
            )
            
            logger.debug(f"Health-Check {name} ausgeführt: {result.get('status', 'unknown')}")
            return result
            
        except Exception as e:
            error_result = {
                'status': 'error',
                'message': str(e),
                'error_type': type(e).__name__,
                'last_check': datetime.now().isoformat()
            }
            
            check['status'] = 'error'
            check['details'] = error_result
            
            logger.error(f"Health-Check {name} fehlgeschlagen: {e}")
            return error_result
    
    def run_all_checks(self):
        """Alle Health-Checks ausführen"""
        results = {}
        overall_status = 'healthy'
        
        for name in self.checks:
            result = self.run_check(name)
            results[name] = result
            
            # Gesamtstatus bestimmen
            if result.get('status') == 'error':
                overall_status = 'unhealthy'
            elif result.get('status') == 'warning' and overall_status == 'healthy':
                overall_status = 'degraded'
        
        return {
            'overall_status': overall_status,
            'timestamp': datetime.now().isoformat(),
            'checks': results
        }
    
    def get_status_summary(self):
        """Zusammenfassung des aktuellen Status"""
        summary = {
            'healthy': 0,
            'warning': 0,
            'error': 0,
            'unknown': 0
        }
        
        for check in self.checks.values():
            status = check.get('status', 'unknown')
            summary[status] += 1
        
        return summary

# Globale Health-Checker-Instanz
health_checker = HealthChecker()

def check_database_health():
    """Datenbank-Gesundheit prüfen"""
    try:
        db_path = Path("instance/bess.db")
        
        if not db_path.exists():
            return {
                'status': 'error',
                'message': 'Datenbank-Datei nicht gefunden',
                'details': {'db_path': str(db_path)}
            }
        
        # Datenbank-Verbindung testen
        start_time = time.time()
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Einfache Query testen
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        table_count = cursor.fetchone()[0]
        
        # Datenbank-Größe prüfen
        db_size = db_path.stat().st_size / (1024 * 1024)  # MB
        
        # Verbindung schließen
        conn.close()
        
        query_time = time.time() - start_time
        
        # Status bestimmen
        if query_time > 1.0:
            status = 'warning'
        elif query_time > 5.0:
            status = 'error'
        else:
            status = 'healthy'
        
        return {
            'status': status,
            'message': 'Datenbank funktioniert normal',
            'details': {
                'table_count': table_count,
                'db_size_mb': round(db_size, 2),
                'query_time': round(query_time, 3),
                'db_path': str(db_path)
            }
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Datenbank-Fehler: {str(e)}',
            'details': {'error_type': type(e).__name__}
        }

def check_redis_health():
    """Redis-Gesundheit prüfen"""
    try:
        # Redis-Verbindung testen
        start_time = time.time()
        r = redis.Redis(host='localhost', port=6379, db=0, socket_timeout=5)
        
        # Ping testen
        r.ping()
        
        # Info abrufen
        info = r.info()
        
        # Memory-Info
        memory_info = r.info('memory')
        
        connection_time = time.time() - start_time
        
        # Status bestimmen
        if connection_time > 0.1:
            status = 'warning'
        elif connection_time > 1.0:
            status = 'error'
        else:
            status = 'healthy'
        
        return {
            'status': status,
            'message': 'Redis funktioniert normal',
            'details': {
                'version': info.get('redis_version', 'unknown'),
                'uptime': info.get('uptime_in_seconds', 0),
                'connected_clients': info.get('connected_clients', 0),
                'used_memory_mb': round(memory_info.get('used_memory', 0) / (1024 * 1024), 2),
                'connection_time': round(connection_time, 3)
            }
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Redis-Fehler: {str(e)}',
            'details': {'error_type': type(e).__name__}
        }

def check_system_resources():
    """System-Ressourcen prüfen"""
    try:
        # CPU-Auslastung
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory-Auslastung
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Disk-Auslastung
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        
        # Status bestimmen
        status = 'healthy'
        warnings = []
        
        if cpu_percent > 80:
            status = 'warning'
            warnings.append(f'CPU-Auslastung hoch: {cpu_percent}%')
        elif cpu_percent > 95:
            status = 'error'
            warnings.append(f'CPU-Auslastung kritisch: {cpu_percent}%')
        
        if memory_percent > 80:
            status = 'warning'
            warnings.append(f'Memory-Auslastung hoch: {memory_percent}%')
        elif memory_percent > 95:
            status = 'error'
            warnings.append(f'Memory-Auslastung kritisch: {memory_percent}%')
        
        if disk_percent > 80:
            status = 'warning'
            warnings.append(f'Disk-Auslastung hoch: {disk_percent}%')
        elif disk_percent > 95:
            status = 'error'
            warnings.append(f'Disk-Auslastung kritisch: {disk_percent}%')
        
        return {
            'status': status,
            'message': 'System-Ressourcen normal' if not warnings else '; '.join(warnings),
            'details': {
                'cpu_percent': round(cpu_percent, 1),
                'memory_percent': round(memory_percent, 1),
                'memory_available_gb': round(memory.available / (1024**3), 2),
                'disk_percent': round(disk_percent, 1),
                'disk_free_gb': round(disk.free / (1024**3), 2)
            }
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f'System-Check-Fehler: {str(e)}',
            'details': {'error_type': type(e).__name__}
        }

def check_application_health():
    """Anwendungs-Gesundheit prüfen"""
    try:
        # Log-Dateien prüfen
        log_dir = Path("logs")
        log_files = list(log_dir.glob("*.log")) if log_dir.exists() else []
        
        # Log-Datei-Größen prüfen
        log_sizes = {}
        total_log_size = 0
        
        for log_file in log_files:
            size_mb = log_file.stat().st_size / (1024 * 1024)
            log_sizes[log_file.name] = round(size_mb, 2)
            total_log_size += size_mb
        
        # Status bestimmen
        status = 'healthy'
        warnings = []
        
        if total_log_size > 100:  # 100MB
            status = 'warning'
            warnings.append(f'Log-Dateien groß: {round(total_log_size, 1)}MB')
        elif total_log_size > 500:  # 500MB
            status = 'error'
            warnings.append(f'Log-Dateien kritisch groß: {round(total_log_size, 1)}MB')
        
        return {
            'status': status,
            'message': 'Anwendung funktioniert normal' if not warnings else '; '.join(warnings),
            'details': {
                'log_files_count': len(log_files),
                'total_log_size_mb': round(total_log_size, 2),
                'log_sizes': log_sizes,
                'working_directory': str(Path.cwd())
            }
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Anwendungs-Check-Fehler: {str(e)}',
            'details': {'error_type': type(e).__name__}
        }

def check_network_health():
    """Netzwerk-Gesundheit prüfen"""
    try:
        # Port-Verfügbarkeit prüfen
        import socket
        
        ports_to_check = [5000, 6379]  # Flask, Redis
        port_status = {}
        
        for port in ports_to_check:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                
                if result == 0:
                    port_status[port] = 'open'
                else:
                    port_status[port] = 'closed'
                    
            except Exception as e:
                port_status[port] = f'error: {str(e)}'
        
        # Status bestimmen
        status = 'healthy'
        warnings = []
        
        for port, port_status_val in port_status.items():
            if port_status_val != 'open':
                status = 'error'
                warnings.append(f'Port {port}: {port_status_val}')
        
        return {
            'status': status,
            'message': 'Netzwerk funktioniert normal' if not warnings else '; '.join(warnings),
            'details': {
                'port_status': port_status,
                'hostname': socket.gethostname()
            }
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Netzwerk-Check-Fehler: {str(e)}',
            'details': {'error_type': type(e).__name__}
        }

def init_health_checks():
    """Alle Health-Checks registrieren"""
    # Standard-Checks registrieren
    health_checker.register_check('database', check_database_health, interval=60)
    health_checker.register_check('redis', check_redis_health, interval=30)
    health_checker.register_check('system', check_system_resources, interval=120)
    health_checker.register_check('application', check_application_health, interval=300)
    health_checker.register_check('network', check_network_health, interval=60)
    
    logger.info("Health-Check-System initialisiert")

def get_health_status():
    """Aktuellen Health-Status abrufen"""
    return health_checker.run_all_checks()

def get_health_summary():
    """Zusammenfassung des Health-Status"""
    return health_checker.get_status_summary()

# Health-Checks initialisieren
if __name__ == "__main__":
    init_health_checks()
    status = get_health_status()
    print(f"Health-Status: {status['overall_status']}")
    for check_name, check_result in status['checks'].items():
        print(f"  {check_name}: {check_result['status']}")
