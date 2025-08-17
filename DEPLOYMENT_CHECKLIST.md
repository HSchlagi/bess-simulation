# 🚀 Hetzner Deployment Checkliste

## Vor dem Deployment

### 1. Lokale Vorbereitung ✅
- [x] Datenbank gesichert
- [x] Datenbank optimiert (VACUUM)
- [x] Deployment-Dateien erstellt
- [x] Git Repository aktualisiert

### 2. Hetzner Server Vorbereitung
- [ ] Server-Zugang einrichten
- [ ] Domain/Subdomain konfigurieren
- [ ] SSL-Zertifikat vorbereiten (Let's Encrypt)

### 3. Umgebungsvariablen
```bash
# Auf Hetzner Server setzen:
export SECRET_KEY="your-secret-key-here"
export DATABASE_URL="sqlite:///instance/bess.db"
export SUPABASE_URL="your-supabase-url"  # Falls verwendet
export SUPABASE_KEY="your-supabase-key"  # Falls verwendet
```

## Deployment-Schritte

### 1. Projekt übertragen
```bash
# Option A: Git Clone
git clone https://github.com/HSchlagi/bess-simulation.git /var/www/bess-simulation

# Option B: Dateien manuell kopieren
scp -r ./* user@hetzner-server:/var/www/bess-simulation/
```

### 2. Deployment ausführen
```bash
cd /var/www/bess-simulation
chmod +x deploy_hetzner.sh
./deploy_hetzner.sh
```

### 3. Datenbank migrieren
```bash
# Use Cases zu projektabhängig migrieren
python migrate_use_cases_to_project_based.py

# Fehlende created_at Werte setzen
python fix_created_at_dates.py
```

### 4. Konfiguration anpassen
- [ ] Domain in nginx_bess_deployment.conf anpassen
- [ ] SSL-Zertifikat einrichten
- [ ] Umgebungsvariablen setzen

## Nach dem Deployment

### 1. Tests durchführen
- [ ] Website erreichbar
- [ ] Login funktioniert
- [ ] Projekte anzeigen
- [ ] Use Case Manager funktioniert
- [ ] Datenbank-Operationen funktionieren

### 2. Monitoring einrichten
- [ ] Logs überwachen: `sudo journalctl -u bess-simulation`
- [ ] Nginx-Logs: `sudo tail -f /var/log/nginx/access.log`
- [ ] Datenbank-Größe überwachen

### 3. Backup-Strategie
- [ ] Automatische Datenbank-Backups einrichten
- [ ] Log-Rotation konfigurieren
- [ ] Monitoring-Alerts einrichten

## Troubleshooting

### Häufige Probleme
1. **Permission Denied**: `sudo chown -R www-data:www-data /var/www/bess-simulation`
2. **Port bereits belegt**: `sudo netstat -tlnp | grep :80`
3. **Datenbank-Fehler**: `python check_database_structure.py`

### Logs prüfen
```bash
sudo systemctl status bess-simulation
sudo journalctl -u bess-simulation -f
sudo tail -f /var/log/nginx/error.log
```

## Sicherheit

### Wichtige Sicherheitsmaßnahmen
- [ ] Firewall konfiguriert
- [ ] SSH-Zugang gesichert
- [ ] Regelmäßige Updates
- [ ] Datenbank-Backups
- [ ] SSL-Zertifikat aktiv

---
**Erstellt:** 2025-08-17 15:22:56
**Version:** BESS-Simulation v2.0 (Multi-User + Use Case Manager)
