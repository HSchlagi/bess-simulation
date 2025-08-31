"""
BESS-Simulation Monitoring & Logging API-Routen
API-Endpoints für Monitoring, Health-Checks und Logs
"""

from flask import Blueprint, jsonify, request, current_app
from functools import wraps
import os
import json
from datetime import datetime, timedelta
from pathlib import Path

from .monitoring_middleware import get_monitoring_stats
from .health_check import get_health_status, get_health_summary, init_health_checks
from .logging_config import setup_app_logger

# Blueprint erstellen
monitoring_bp = Blueprint('monitoring', __name__, url_prefix='/api')

# Logger einrichten
logger = setup_app_logger("monitoring_api")

def admin_required(f):
    """Decorator für Admin-Berechtigung"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Einfache Admin-Prüfung (kann später erweitert werden)
        if not current_app.config.get('ADMIN_MODE', False):
            return jsonify({'error': 'Admin-Berechtigung erforderlich'}), 403
        return f(*args, **kwargs)
    return decorated_function

@monitoring_bp.route('/health/status', methods=['GET'])
def health_status():
    """Vollständigen Health-Status abrufen"""
    try:
        status = get_health_status()
        logger.info("Health-Status abgerufen")
        return jsonify(status)
    except Exception as e:
        logger.error(f"Fehler beim Abrufen des Health-Status: {e}")
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/health/summary', methods=['GET'])
def health_summary():
    """Zusammenfassung des Health-Status abrufen"""
    try:
        summary = get_health_summary()
        return jsonify(summary)
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Health-Zusammenfassung: {e}")
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/health/check/<check_name>', methods=['POST'])
@admin_required
def run_specific_health_check(check_name):
    """Bestimmten Health-Check ausführen"""
    try:
        from .health_check import health_checker
        result = health_checker.run_check(check_name)
        logger.info(f"Health-Check {check_name} ausgeführt: {result.get('status', 'unknown')}")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Fehler beim Ausführen des Health-Checks {check_name}: {e}")
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/monitoring/stats', methods=['GET'])
def monitoring_stats():
    """Monitoring-Statistiken abrufen"""
    try:
        stats = get_monitoring_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Monitoring-Statistiken: {e}")
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/logs/recent', methods=['GET'])
@admin_required
def recent_logs():
    """Kürzlich erstellte Logs abrufen"""
    try:
        # Parameter aus Query-String
        limit = request.args.get('limit', 100, type=int)
        level = request.args.get('level', 'all')
        hours = request.args.get('hours', 24, type=int)
        
        # Log-Verzeichnis
        log_dir = Path("logs")
        if not log_dir.exists():
            return jsonify({'logs': [], 'message': 'Log-Verzeichnis nicht gefunden'})
        
        # Alle Log-Dateien durchsuchen
        all_logs = []
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        for log_file in log_dir.glob("*.log"):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            # Log-Zeile parsen
                            log_entry = parse_log_line(line, log_file.name)
                            if log_entry and log_entry['timestamp'] >= cutoff_time:
                                # Level-Filter anwenden
                                if level == 'all' or log_entry['level'] == level:
                                    all_logs.append(log_entry)
            except Exception as e:
                logger.warning(f"Fehler beim Lesen der Log-Datei {log_file}: {e}")
        
        # Nach Zeitstempel sortieren (neueste zuerst)
        all_logs.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Limit anwenden
        logs = all_logs[:limit]
        
        return jsonify({
            'logs': logs,
            'total_found': len(all_logs),
            'returned': len(logs),
            'level_filter': level,
            'time_filter_hours': hours
        })
        
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Logs: {e}")
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/logs/search', methods=['POST'])
@admin_required
def search_logs():
    """Logs durchsuchen"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        level = data.get('level', 'all')
        hours = data.get('hours', 24, type=int)
        limit = data.get('limit', 100, type=int)
        
        if not query:
            return jsonify({'error': 'Suchbegriff erforderlich'}), 400
        
        # Log-Verzeichnis
        log_dir = Path("logs")
        if not log_dir.exists():
            return jsonify({'logs': [], 'message': 'Log-Verzeichnis nicht gefunden'})
        
        # Logs durchsuchen
        matching_logs = []
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        for log_file in log_dir.glob("*.log"):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip() and query.lower() in line.lower():
                            log_entry = parse_log_line(line, log_file.name)
                            if log_entry and log_entry['timestamp'] >= cutoff_time:
                                if level == 'all' or log_entry['level'] == level:
                                    matching_logs.append(log_entry)
            except Exception as e:
                logger.warning(f"Fehler beim Durchsuchen der Log-Datei {log_file}: {e}")
        
        # Nach Zeitstempel sortieren
        matching_logs.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Limit anwenden
        logs = matching_logs[:limit]
        
        return jsonify({
            'logs': logs,
            'total_matches': len(matching_logs),
            'returned': len(logs),
            'query': query,
            'level_filter': level,
            'time_filter_hours': hours
        })
        
    except Exception as e:
        logger.error(f"Fehler bei der Log-Suche: {e}")
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/logs/levels', methods=['GET'])
def log_levels():
    """Verfügbare Log-Level abrufen"""
    try:
        log_dir = Path("logs")
        if not log_dir.exists():
            return jsonify({'levels': []})
        
        # Alle Log-Level aus allen Dateien sammeln
        levels = set()
        for log_file in log_dir.glob("*.log"):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            log_entry = parse_log_line(line, log_file.name)
                            if log_entry and log_entry['level']:
                                levels.add(log_entry['level'])
            except Exception:
                continue
        
        return jsonify({'levels': sorted(list(levels))})
        
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Log-Level: {e}")
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/logs/files', methods=['GET'])
def log_files():
    """Verfügbare Log-Dateien auflisten"""
    try:
        log_dir = Path("logs")
        if not log_dir.exists():
            return jsonify({'files': []})
        
        files = []
        for log_file in log_dir.glob("*.log"):
            try:
                stat = log_file.stat()
                files.append({
                    'name': log_file.name,
                    'size_mb': round(stat.st_size / (1024 * 1024), 2),
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'created': datetime.fromtimestamp(stat.st_ctime).isoformat()
                })
            except Exception as e:
                logger.warning(f"Fehler beim Abrufen der Datei-Info für {log_file}: {e}")
        
        # Nach Größe sortieren (größte zuerst)
        files.sort(key=lambda x: x['size_mb'], reverse=True)
        
        return jsonify({'files': files})
        
    except Exception as e:
        logger.error(f"Fehler beim Auflisten der Log-Dateien: {e}")
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/logs/cleanup', methods=['POST'])
@admin_required
def cleanup_logs():
    """Alte Log-Dateien bereinigen"""
    try:
        data = request.get_json()
        days_to_keep = data.get('days', 30, type=int)
        max_size_mb = data.get('max_size_mb', 100, type=int)
        
        log_dir = Path("logs")
        if not log_dir.exists():
            return jsonify({'message': 'Log-Verzeichnis nicht gefunden'})
        
        cutoff_time = datetime.now() - timedelta(days=days_to_keep)
        deleted_files = []
        freed_space_mb = 0
        
        for log_file in log_dir.glob("*.log"):
            try:
                stat = log_file.stat()
                file_time = datetime.fromtimestamp(stat.st_mtime)
                file_size_mb = stat.st_size / (1024 * 1024)
                
                # Datei löschen wenn zu alt oder zu groß
                if (file_time < cutoff_time or file_size_mb > max_size_mb):
                    freed_space_mb += file_size_mb
                    log_file.unlink()
                    deleted_files.append(log_file.name)
                    logger.info(f"Log-Datei gelöscht: {log_file.name}")
                    
            except Exception as e:
                logger.warning(f"Fehler beim Bereinigen der Log-Datei {log_file}: {e}")
        
        return jsonify({
            'message': f'{len(deleted_files)} Log-Dateien bereinigt',
            'deleted_files': deleted_files,
            'freed_space_mb': round(freed_space_mb, 2),
            'days_to_keep': days_to_keep,
            'max_size_mb': max_size_mb
        })
        
    except Exception as e:
        logger.error(f"Fehler bei der Log-Bereinigung: {e}")
        return jsonify({'error': str(e)}), 500

def parse_log_line(line, filename):
    """Log-Zeile parsen"""
    try:
        # Verschiedene Log-Formate unterstützen
        if ' | ' in line:
            # Detailliertes Format: timestamp | level | logger | function | line | message
            parts = line.strip().split(' | ')
            if len(parts) >= 6:
                timestamp_str = parts[0]
                level = parts[1]
                logger_name = parts[2]
                function = parts[3]
                line_num = parts[4]
                message = ' | '.join(parts[5:])
                
                # Zeitstempel parsen
                try:
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    timestamp = datetime.now()
                
                return {
                    'timestamp': timestamp.isoformat(),
                    'level': level.strip(),
                    'logger': logger_name.strip(),
                    'function': function.strip(),
                    'line': line_num.strip(),
                    'message': message.strip(),
                    'file': filename
                }
        
        elif '[' in line and ']' in line:
            # Einfaches Format: [LEVEL] timestamp message
            level_start = line.find('[')
            level_end = line.find(']')
            
            if level_start != -1 and level_end != -1:
                level = line[level_start + 1:level_end]
                remaining = line[level_end + 1:].strip()
                
                # Zeitstempel und Nachricht trennen
                parts = remaining.split(' ', 1)
                if len(parts) >= 2:
                    timestamp_str = parts[0]
                    message = parts[1]
                    
                    try:
                        timestamp = datetime.strptime(timestamp_str, '%H:%M:%S')
                        # Aktuelles Datum hinzufügen
                        timestamp = timestamp.replace(
                            year=datetime.now().year,
                            month=datetime.now().month,
                            day=datetime.now().day
                        )
                    except ValueError:
                        timestamp = datetime.now()
                    
                    return {
                        'timestamp': timestamp.isoformat(),
                        'level': level.strip(),
                        'logger': 'unknown',
                        'function': 'unknown',
                        'line': '0',
                        'message': message.strip(),
                        'file': filename
                    }
        
        # Fallback: Einfache Zeile
        return {
            'timestamp': datetime.now().isoformat(),
            'level': 'INFO',
            'logger': 'unknown',
            'function': 'unknown',
            'line': '0',
            'message': line.strip(),
            'file': filename
        }
        
    except Exception as e:
        logger.warning(f"Fehler beim Parsen der Log-Zeile: {e}")
        return None

# Health-Checks initialisieren
def init_monitoring():
    """Monitoring beim ersten Request initialisieren"""
    try:
        init_health_checks()
        logger.info("Monitoring-APIs initialisiert")
    except Exception as e:
        logger.error(f"Fehler bei der Monitoring-Initialisierung: {e}")

# Fehlerbehandlung
@monitoring_bp.errorhandler(Exception)
def handle_error(error):
    """Allgemeine Fehlerbehandlung"""
    logger.error(f"Monitoring-API-Fehler: {error}")
    return jsonify({'error': str(error)}), 500
