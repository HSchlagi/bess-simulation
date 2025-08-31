#!/usr/bin/env python3
"""
Performance-Optimierung für BESS-Simulation
===========================================

Redis-Caching, Datenbank-Indizes, API-Optimierungen und Lazy Loading
"""

import os
import time
from functools import wraps
from flask import request, jsonify, current_app
from flask_caching import Cache
import redis
import sqlite3
from typing import Dict, Any, List, Optional

# Redis-Caching Konfiguration
cache_config = {
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_HOST': 'localhost',
    'CACHE_REDIS_PORT': 6379,
    'CACHE_REDIS_DB': 0,
    'CACHE_DEFAULT_TIMEOUT': 300,  # 5 Minuten
    'CACHE_KEY_PREFIX': 'bess_'
}

# Cache-Instanz
cache = Cache()

# Performance-Monitoring
class PerformanceMonitor:
    """Performance-Monitoring für API-Endpoints"""
    
    def __init__(self):
        self.metrics = {}
    
    def time_endpoint(self, endpoint_name: str):
        """Decorator für Endpoint-Performance-Messung"""
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                result = f(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Metriken speichern
                if endpoint_name not in self.metrics:
                    self.metrics[endpoint_name] = []
                self.metrics[endpoint_name].append(execution_time)
                
                # Performance-Header hinzufügen
                if hasattr(result, 'headers'):
                    result.headers['X-Execution-Time'] = f"{execution_time:.3f}s"
                
                return result
            return wrapper
        return decorator
    
    def get_metrics(self) -> Dict[str, Any]:
        """Performance-Metriken abrufen"""
        metrics = {}
        for endpoint, times in self.metrics.items():
            if times:
                metrics[endpoint] = {
                    'count': len(times),
                    'avg_time': sum(times) / len(times),
                    'min_time': min(times),
                    'max_time': max(times),
                    'last_10_avg': sum(times[-10:]) / min(len(times), 10)
                }
        return metrics

# Performance-Monitor Instanz
performance_monitor = PerformanceMonitor()

# Datenbank-Indizes
DATABASE_INDICES = [
    # Projekte-Tabelle
    "CREATE INDEX IF NOT EXISTS idx_projects_customer_id ON projects(customer_id)",
    "CREATE INDEX IF NOT EXISTS idx_projects_created_at ON projects(created_at)",
    "CREATE INDEX IF NOT EXISTS idx_projects_bess_size ON projects(bess_size)",
    "CREATE INDEX IF NOT EXISTS idx_projects_pv_power ON projects(pv_power)",
    
    # Kunden-Tabelle
    "CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email)",
    "CREATE INDEX IF NOT EXISTS idx_customers_company ON customers(company)",
    
    # Spot-Preise-Tabelle
    "CREATE INDEX IF NOT EXISTS idx_spot_prices_timestamp ON spot_prices(timestamp)",
    "CREATE INDEX IF NOT EXISTS idx_spot_prices_region ON spot_prices(region)",
    "CREATE INDEX IF NOT EXISTS idx_spot_prices_price ON spot_prices(price)",
    
    # Load-Profile-Tabelle
    "CREATE INDEX IF NOT EXISTS idx_load_profiles_project_id ON load_profiles(project_id)",
    "CREATE INDEX IF NOT EXISTS idx_load_profiles_timestamp ON load_profiles(timestamp)",
    
    # Use-Cases-Tabelle
    "CREATE INDEX IF NOT EXISTS idx_use_cases_project_id ON use_cases(project_id)",
    "CREATE INDEX IF NOT EXISTS idx_use_cases_type ON use_cases(type)",
    
    # Benutzer-Tabelle
    "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
    "CREATE INDEX IF NOT EXISTS idx_users_role_id ON users(role_id)",
    "CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active)"
]

def create_database_indices(db_path: str):
    """Datenbank-Indizes erstellen"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        for index_sql in DATABASE_INDICES:
            cursor.execute(index_sql)
        
        conn.commit()
        conn.close()
        print("✅ Datenbank-Indizes erfolgreich erstellt")
        
    except Exception as e:
        print(f"❌ Fehler beim Erstellen der Datenbank-Indizes: {e}")

# Lazy Loading für große Datasets
class LazyDatasetLoader:
    """Lazy Loading für große Datasets"""
    
    def __init__(self, chunk_size: int = 1000):
        self.chunk_size = chunk_size
    
    def load_in_chunks(self, query_func, *args, **kwargs):
        """Daten in Chunks laden"""
        offset = 0
        while True:
            chunk = query_func(*args, limit=self.chunk_size, offset=offset, **kwargs)
            if not chunk:
                break
            
            yield from chunk
            offset += self.chunk_size
    
    def paginate_results(self, query_func, page: int = 1, per_page: int = 50):
        """Ergebnisse paginieren"""
        offset = (page - 1) * per_page
        return query_func(limit=per_page, offset=offset)

# API-Response-Optimierung
def optimize_api_response(data: Any, include_metadata: bool = True) -> Dict[str, Any]:
    """API-Response optimieren"""
    if include_metadata:
        return {
            'success': True,
            'data': data,
            'timestamp': time.time(),
            'cached': False
        }
    return data

def cache_api_response(timeout: int = 300):
    """API-Response cachen"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Cache-Key generieren
            cache_key = f"{f.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Versuche aus Cache zu laden
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return optimize_api_response(cached_result, include_metadata=True)
            
            # Führe Funktion aus
            result = f(*args, **kwargs)
            
            # Ergebnis cachen
            cache.set(cache_key, result, timeout=timeout)
            
            return optimize_api_response(result, include_metadata=True)
        return wrapper
    return decorator

# Statische Assets CDN-Optimierung
def get_cdn_url(asset_path: str) -> str:
    """CDN-URL für statische Assets generieren"""
    # In Produktion würde hier die echte CDN-URL stehen
    if os.environ.get('FLASK_ENV') == 'production':
        cdn_base = os.environ.get('CDN_BASE_URL', 'https://cdn.bess.instanet.at')
        return f"{cdn_base}/{asset_path}"
    
    # Lokale Entwicklung
    return f"/static/{asset_path}"

# Performance-Middleware
def performance_middleware():
    """Performance-Middleware für alle Requests"""
    start_time = time.time()
    
    def after_request(response):
        execution_time = time.time() - start_time
        
        # Performance-Header
        response.headers['X-Execution-Time'] = f"{execution_time:.3f}s"
        response.headers['X-Cache-Status'] = 'MISS'  # Wird später auf HIT gesetzt
        
        # Performance-Metriken aktualisieren
        endpoint = request.endpoint
        if endpoint:
            if endpoint not in performance_monitor.metrics:
                performance_monitor.metrics[endpoint] = []
            performance_monitor.metrics[endpoint].append(execution_time)
        
        return response
    
    return after_request

# Cache-Status-Header
def add_cache_headers(response, cache_status: str = 'MISS'):
    """Cache-Status-Header hinzufügen"""
    response.headers['X-Cache-Status'] = cache_status
    response.headers['Cache-Control'] = 'public, max-age=300'
    return response

# Performance-Konfiguration exportieren
__all__ = [
    'cache_config',
    'cache',
    'performance_monitor',
    'create_database_indices',
    'LazyDatasetLoader',
    'optimize_api_response',
    'cache_api_response',
    'get_cdn_url',
    'performance_middleware',
    'add_cache_headers'
]
