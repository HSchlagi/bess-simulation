# 🧠 Cursor AI Prompts für Benutzeranmeldung / Registrierung

Diese Datei enthält durchdachte Prompts zur Nutzung in **Cursor AI**, um ein modernes und sicheres Benutzeranmeldesystem zu erstellen – ideal für die Integration in eine bestehende Flask-/React-Anwendung.

---

## 🔧 Backend (Flask)

### 📌 Registrierung + Login mit JWT + bcrypt
```text
Erstelle eine sichere Flask API mit folgenden Endpunkten:
/register: Registriert Nutzer (E-Mail, Passwort), speichert Passwort als bcrypt-Hash.
/login: Verifiziert E-Mail und Passwort, gibt bei Erfolg ein JWT zurück und setzt es als HTTP-only Cookie.
/profile: Gibt Benutzerdaten nur zurück, wenn ein gültiger JWT im Cookie enthalten ist.
Verwende Flask-JWT-Extended, bcrypt und Flask-CORS. Gib JSON-Antworten mit Statuscodes zurück.
```

---

## 🔐 Passwort-Hashing mit bcrypt
```text
Erstelle in Flask eine Utility-Funktion, die ein Passwort mit bcrypt hasht und vergleicht. 
Verwende `bcrypt.hashpw` und `bcrypt.checkpw`. Stelle sicher, dass das Passwort vor dem Speichern nicht im Klartext vorliegt.
```

---

## 🎟 JWT-Token Handling
```text
Nutze Flask-JWT-Extended, um beim Login ein JWT zu generieren und beim Zugriff auf geschützte Endpunkte (z. B. /profile) zu validieren.
Speichere das JWT im HTTP-only Cookie und verwende `@jwt_required()` für die geschützten Routen.
```

---

## 🧩 Frontend (React + Tailwind)

### 🖥️ Login- und Registrierungsformular
```text
Erstelle ein Login- und Registrierungsformular mit React und TailwindCSS. 
Verwende controlled Inputs für E-Mail und Passwort. 
Bei Klick auf Submit wird ein POST-Request an /api/login oder /api/register gesendet. 
Zeige Fehlermeldungen und Ladezustand an. 
Nach erfolgreichem Login leite den Nutzer weiter zur Startseite.
```

---

### 🪝 Custom React Auth Hook
```text
Schreibe einen React-Hook useAuth(), der prüft, ob ein gültiges Session-Cookie vorhanden ist. 
Er soll Methoden wie login(), logout(), register() und isAuthenticated enthalten.
Verwende Fetch-API für Kommunikation mit dem Backend.
```

---

## 🛡 Sicherheitsfunktionen
```text
Baue Rate Limiting in die Flask-API ein mit Flask-Limiter. Limitiere /login auf max. 5 Anfragen pro Minute pro IP.
Aktiviere CORS nur für bestimmte Domains.
Verhindere CSRF, indem du JWTs nur über HTTP-only Cookies überträgst.
```

---

## 🧪 Tests und Validierung
```text
Generiere Unit-Tests mit Pytest für die Endpunkte /register und /login. 
Stelle sicher, dass Passwörter nicht im Klartext gespeichert werden und fehlerhafte Logins korrekt behandelt werden.
```

---

## 📦 Optional: Supabase-Integration
```text
Ersetze die eigene User-DB durch Supabase Auth. 
Registrierung und Login erfolgen über Supabase API. 
Verwende Supabase JS SDK im Frontend, um Nutzerstatus zu prüfen und Sessions zu verwalten.
```
