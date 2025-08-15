Erweitere ein bestehendes Flask-Webprojekt mit folgenden Funktionen:

1. Verwende Supabase für Benutzeranmeldung via E-Mail und Passwort.
2. Beim erfolgreichen Login speichere die Benutzersession mit Flask `session`.
3. Zeige nach Login eine Dashboard-Seite mit den letzten Simulationsergebnissen aus einer SQLite-Datenbank `bess_simulation.db`, Tabelle `simulation_results`.
4. Nutze TailwindCSS für das Styling der Login- und Dashboard-Seiten.
5. Falls der Benutzer nicht eingeloggt ist, leite automatisch auf /login um.
6. Implementiere Logout-Funktion über /logout.
7. Richte sichere Fehlerbehandlung beim Login ein (ungültige Credentials, leere Felder etc.).
8. Optional: Zeige im Dashboard eine Tabelle mit `timestamp`, `capacity_kwh`, `state_of_charge`.

Verzeichnisstruktur:
- `app.py`: Backend-Logik
- `templates/login.html`: Anmeldeseite
- `templates/dashboard.html`: Dashboard nach Login

Nutze Python 3.10+, SQLite3, Supabase Python SDK, TailwindCSS CDN.

Optional:
- Ergänze eine `register.html` Seite mit Formular für Benutzerregistrierung über Supabase.
- Erstelle ein Setup-Skript zur lokalen Initialisierung der SQLite-Datenbank mit Beispieldaten.