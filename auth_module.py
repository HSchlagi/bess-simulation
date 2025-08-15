"""
BESS-Simulation Authentication Module
====================================

Supabase-basierte Benutzeranmeldung für die BESS-Simulation.
"""

import os
from functools import wraps
from flask import session, redirect, url_for, flash, request
from supabase import create_client, Client
from typing import Optional

# Supabase-Initialisierung
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Fallback für Entwicklung (sollte in Produktion über Umgebungsvariablen gesetzt werden)
if not SUPABASE_URL:
    SUPABASE_URL = "https://your-project.supabase.co"
if not SUPABASE_KEY:
    SUPABASE_KEY = "your-anon-key"

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    AUTH_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Supabase nicht verfügbar: {e}")
    AUTH_AVAILABLE = False
    supabase = None

def login_required(f):
    """
    Decorator für Routen, die eine Anmeldung erfordern
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not AUTH_AVAILABLE:
            # Wenn Auth nicht verfügbar ist, erlaube Zugriff (Entwicklungsmodus)
            return f(*args, **kwargs)
        
        if "user" not in session:
            flash("Bitte melden Sie sich an, um diese Seite zu sehen.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function

def auth_optional(f):
    """
    Decorator für Routen, die optional eine Anmeldung haben können
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not AUTH_AVAILABLE:
            return f(*args, **kwargs)
        return f(*args, **kwargs)
    return decorated_function

class BESSAuth:
    """Hauptklasse für BESS-Authentifizierung"""
    
    def __init__(self):
        self.supabase = supabase
        self.available = AUTH_AVAILABLE
    
    def login(self, email: str, password: str) -> tuple[bool, str]:
        """
        Benutzer anmelden
        
        Args:
            email: E-Mail-Adresse
            password: Passwort
            
        Returns:
            tuple[bool, str]: (Erfolg, Nachricht)
        """
        if not self.available:
            return False, "Authentifizierung nicht verfügbar"
        
        try:
            result = self.supabase.auth.sign_in_with_password({
                "email": email, 
                "password": password
            })
            
            if result.user:
                session["user"] = {
                    "email": result.user.email,
                    "id": result.user.id,
                    "created_at": result.user.created_at
                }
                return True, "Anmeldung erfolgreich"
            else:
                return False, "Anmeldung fehlgeschlagen"
                
        except Exception as e:
            return False, f"Anmeldungsfehler: {str(e)}"
    
    def register(self, email: str, password: str) -> tuple[bool, str]:
        """
        Neuen Benutzer registrieren
        
        Args:
            email: E-Mail-Adresse
            password: Passwort
            
        Returns:
            tuple[bool, str]: (Erfolg, Nachricht)
        """
        if not self.available:
            return False, "Authentifizierung nicht verfügbar"
        
        try:
            result = self.supabase.auth.sign_up({
                "email": email,
                "password": password
            })
            
            if result.user:
                return True, "Registrierung erfolgreich. Bitte bestätigen Sie Ihre E-Mail."
            else:
                return False, "Registrierung fehlgeschlagen"
                
        except Exception as e:
            return False, f"Registrierungsfehler: {str(e)}"
    
    def logout(self) -> bool:
        """
        Benutzer abmelden
        
        Returns:
            bool: Erfolg
        """
        try:
            if self.available and self.supabase:
                self.supabase.auth.sign_out()
            session.clear()
            return True
        except Exception as e:
            print(f"Logout-Fehler: {e}")
            session.clear()
            return True
    
    def get_current_user(self) -> Optional[dict]:
        """
        Aktuellen Benutzer abrufen
        
        Returns:
            Optional[dict]: Benutzerdaten oder None
        """
        return session.get("user")
    
    def is_authenticated(self) -> bool:
        """
        Prüfen ob Benutzer angemeldet ist
        
        Returns:
            bool: True wenn angemeldet
        """
        return "user" in session

# Globale Auth-Instanz
bess_auth = BESSAuth()
