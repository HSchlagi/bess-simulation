# Deployment-Konfiguration für Hetzner
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///instance/bess.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Supabase-Konfiguration (falls benötigt)
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
    
    # Debug-Modus deaktivieren für Produktion
    DEBUG = False
    
    # Logging-Konfiguration
    LOG_LEVEL = 'INFO'
