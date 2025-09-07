#!/usr/bin/env python3
"""
Erstellt eine Test-Benachrichtigung für das Benachrichtigungs-System
"""

import sqlite3
from datetime import datetime

def create_test_notification():
    """Erstellt eine Test-Benachrichtigung"""
    try:
        conn = sqlite3.connect('instance/bess.db')
        cursor = conn.cursor()
        
        # Test-Benachrichtigung erstellen
        cursor.execute('''
        INSERT INTO notifications (user_id, type, title, message, priority, read, created_at)
        VALUES (1, 'info', '🔔 Willkommen im Benachrichtigungs-System', 
                'Das Benachrichtigungs-System wurde erfolgreich implementiert und ist einsatzbereit!', 
                'medium', 0, datetime('now'))
        ''')
        
        conn.commit()
        print('✅ Test-Benachrichtigung erstellt')
        
        # Prüfen ob Benachrichtigung erstellt wurde
        cursor.execute('SELECT COUNT(*) FROM notifications WHERE user_id = 1')
        count = cursor.fetchone()[0]
        print(f'📊 Gesamt Benachrichtigungen für User 1: {count}')
        
        conn.close()
        
    except Exception as e:
        print(f'❌ Fehler beim Erstellen der Test-Benachrichtigung: {e}')

if __name__ == '__main__':
    create_test_notification()
