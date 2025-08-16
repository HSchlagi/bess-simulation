# 🚀 Anleitung: BESS-Programm auf Hetzner-Server überspielen

## 📋 Voraussetzungen

- Hetzner-Server läuft bereits mit nginx auf Port 5050
- Alte Version läuft unter `/opt/bess-simulation/`
- SSH-Zugang zum Server verfügbar
- Lokale Kopie des aktuellen BESS-Programms bereit

## 🔄 Schritt-für-Schritt Anleitung

### 1. 📦 Backup der aktuellen Version erstellen

```bash
# Auf dem Hetzner-Server ausführen:
sudo systemctl stop bess-simulation
cd /opt
sudo cp -r bess-simulation bess-simulation-backup-$(date +%Y%m%d-%H%M%S)
```

### 2. 🗂️ Aktuelle Dateien sichern

```bash
# Wichtige Konfigurationsdateien sichern:
sudo cp /opt/bess-simulation/instance/bess.db /opt/bess-simulation-backup-db-$(date +%Y%m%d-%H%M%S).db
sudo cp /opt/bess-simulation/config.py /opt/bess-simulation-backup-config-$(date +%Y%m%d-%H%M%S).py
```

### 3. 📤 Lokale Dateien vorbereiten

```bash
# Auf Ihrem lokalen System:
# Alle Dateien in ein Archiv packen (außer venv und __pycache__)
tar -czf bess-simulation-update.tar.gz \
  --exclude='venv' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.git' \
  --exclude='instance/bess.db' \
  --exclude='instance/*.db' \
  .
```

### 4. 📤 Dateien auf Server übertragen

```bash
# Von Ihrem lokalen System zum Server:
scp bess-simulation-update.tar.gz root@IHRE-SERVER-IP:/tmp/
```

### 5. 🔄 Server vorbereiten

```bash
# Auf dem Hetzner-Server:
sudo systemctl stop bess-simulation
sudo systemctl stop nginx

# Alte Version umbenennen (als Fallback)
sudo mv /opt/bess-simulation /opt/bess-simulation-old
```

### 6. 📦 Neue Version installieren

```bash
# Auf dem Hetzner-Server:
cd /opt
sudo tar -xzf /tmp/bess-simulation-update.tar.gz
sudo mv bess-simulation-* bess-simulation

# Berechtigungen setzen
sudo chown -R root:root /opt/bess-simulation
sudo chmod -R 755 /opt/bess-simulation
```

### 7. 🔧 Konfiguration anpassen

```bash
# Datenbank wiederherstellen (falls gewünscht)
sudo cp /opt/bess-simulation-backup-db-*.db /opt/bess-simulation/instance/bess.db

# Konfiguration prüfen
sudo nano /opt/bess-simulation/config.py
```

### 8. 🐍 Python-Umgebung einrichten

```bash
# Virtual Environment erstellen
cd /opt/bess-simulation
sudo python3 -m venv venv
sudo /opt/bess-simulation/venv/bin/pip install -r requirements.txt
```

### 8.5. 🔐 Supabase-Authentifizierung konfigurieren

```bash
# WICHTIG: E-Mail-Bestätigung für Produktion aktivieren
sudo nano /opt/bess-simulation/auth_module.py

# Zeile 108 ändern von:
# "options": {"email_confirm": False}
# zu:
# "options": {"email_confirm": True}

# Umgebungsvariablen für Produktion setzen
sudo nano /etc/environment

# Folgende Zeilen hinzufügen:
SUPABASE_URL=https://wxkbyeueyrxoevcwwqop.supabase.co
SUPABASE_KEY=ihr-produktions-supabase-key
FLASK_SECRET_KEY=sicherer-produktions-secret-key

# Umgebungsvariablen neu laden
source /etc/environment
```

### 9. 🔍 Systemd-Service prüfen

```bash
# Service-Datei prüfen
sudo cat /etc/systemd/system/bess-simulation.service

# Falls nötig, Service neu laden
sudo systemctl daemon-reload
```

### 10. 🚀 System starten

```bash
# BESS-Service starten
sudo systemctl start bess-simulation
sudo systemctl enable bess-simulation

# Nginx starten
sudo systemctl start nginx

# Status prüfen
sudo systemctl status bess-simulation
sudo systemctl status nginx
```

### 11. ✅ Funktionsprüfung

```bash
# Logs prüfen
sudo journalctl -u bess-simulation -f

# Port prüfen
sudo netstat -tlnp | grep :5050

# Web-Interface testen
curl http://localhost:5050

# Supabase-Auth testen
curl http://localhost:5050/login
curl http://localhost:5050/register
```

## 🔧 Troubleshooting

### Falls Probleme auftreten:

```bash
# 1. Logs prüfen
sudo journalctl -u bess-simulation -n 50

# 2. Alte Version wiederherstellen
sudo systemctl stop bess-simulation
sudo rm -rf /opt/bess-simulation
sudo mv /opt/bess-simulation-old /opt/bess-simulation
sudo systemctl start bess-simulation

# 3. Berechtigungen prüfen
sudo chown -R root:root /opt/bess-simulation
sudo chmod -R 755 /opt/bess-simulation

# 4. Supabase-Auth prüfen
sudo cat /opt/bess-simulation/auth_module.py | grep "email_confirm"
sudo env | grep SUPABASE
```

### Nginx-Konfiguration prüfen:

```bash
# Nginx-Konfiguration testen
sudo nginx -t

# Nginx-Konfiguration anzeigen
sudo cat /etc/nginx/sites-available/bess-simulation
```

## 📝 Wichtige Hinweise

1. **Backup immer erstellen** - Die alte Version bleibt als Backup erhalten
2. **Datenbank sichern** - Falls wichtige Daten in der DB sind
3. **Konfiguration prüfen** - Besonders `config.py` und nginx-Settings
4. **Logs beobachten** - Nach dem Start die Logs prüfen
5. **Testen** - Web-Interface und alle Funktionen testen
6. **Supabase-Auth konfigurieren** - E-Mail-Bestätigung für Produktion aktivieren
7. **Umgebungsvariablen setzen** - SUPABASE_URL, SUPABASE_KEY, FLASK_SECRET_KEY

## 🎯 Rollback-Plan

Falls etwas schief geht:

```bash
# Schneller Rollback
sudo systemctl stop bess-simulation
sudo rm -rf /opt/bess-simulation
sudo mv /opt/bess-simulation-old /opt/bess-simulation
sudo systemctl start bess-simulation
sudo systemctl start nginx
```

## 📞 Support

Bei Problemen:
- Logs prüfen: `sudo journalctl -u bess-simulation -f`
- Nginx-Logs: `sudo tail -f /var/log/nginx/error.log`
- System-Status: `sudo systemctl status bess-simulation`
- Supabase-Auth: `sudo cat /opt/bess-simulation/auth_module.py | grep -A 5 -B 5 "email_confirm"`
- Umgebungsvariablen: `sudo env | grep -E "(SUPABASE|FLASK)"`

## 🔐 Neue Features nach Deployment

### ✅ Supabase-Authentifizierung:
- **Login/Register/Logout** über `/login`, `/register`, `/logout`
- **Session-Management** mit Flask
- **Route-Protection** für geschützte Bereiche
- **E-Mail-Bestätigung** für neue Benutzer (Produktion)

### ✅ UI/UX-Verbesserungen:
- **Echtes BESS-Container-Bild** auf Login-Seite
- **Moderne Login-UI** mit TailwindCSS
- **Responsive Design** für alle Geräte
- **Animations und Glassmorphism-Effekte**

### ✅ Sicherheit:
- **Supabase Backend** für sichere Authentifizierung
- **CSRF-Schutz** für alle Formulare
- **Umgebungsvariablen** für API-Keys
- **Session-Timeout** und sichere Cookies

---

**Viel Erfolg beim Deployment! 🚀** 