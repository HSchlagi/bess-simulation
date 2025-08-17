#!/usr/bin/env python3
"""
WSGI-Entry-Point für Gunicorn auf Hetzner
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
