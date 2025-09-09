# 🚀 Hetzner Deployment Checklist - BESS Simulation

**Datum:** 08. September 2025  
**Version:** 2.2 (mit PWA Features)  
**Commit:** 0478a14

## 📋 Pre-Deployment Checklist

### ✅ **Datenbank-Backup erstellt:**
- **SQL-Dump:** `instance/bess_backup_2025-09-08_17-30-22.sql` (140.24 MB)
- **Komprimiert:** `instance/bess_backup_2025-09-08_17-30-22.sql.gz` (6.73 MB)
- **Kompression:** 95.2% (sehr effizient für Transfer)

### ✅ **Git-Repository aktualisiert:**
- **Repository:** https://github.com/HSchlagi/bess-simulation
- **Commit:** 0478a14 - "PWA Features vollständig implementiert"
- **Neue Features:** Progressive Web App, Advanced Dispatch & Grid Services

## 🔧 **Deployment-Schritte für Hetzner:**

### **1. SSH-Verbindung zum Hetzner-Server:**
```bash
ssh root@bess.instanet.at
```

### **2. Aktuelle Version stoppen:**
```bash
sudo systemctl stop bess
```

### **3. Backup der aktuellen Version:**
```bash
cd /opt/bess-simulation
cp -r . ../bess-backup-$(date +%Y%m%d-%H%M%S)
```

### **4. Git-Update durchführen:**
```bash
git pull origin main
```

### **5. Neue Dependencies installieren:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### **6. Datenbank-Migration (falls nötig):**
```bash
# Falls neue Tabellen hinzugefügt wurden
python migrate_advanced_dispatch_tables.py
```

### **7. PWA-Assets bereitstellen:**
```bash
# PWA-Dateien sind bereits im Git-Repository
# Service Worker, Manifest, Icons sind verfügbar
```

### **8. Service neu starten:**
```bash
sudo systemctl start bess
sudo systemctl status bess
```

## 📁 **WinSCP-Transfer (falls nötig):**

### **Lokale Dateien für Transfer:**
- `instance/bess_backup_2025-09-08_17-30-22.sql.gz` (6.73 MB)
- `static/manifest.json` (PWA Manifest)
- `static/sw.js` (Service Worker)
- `static/js/pwa.js` (PWA JavaScript)
- `app/pwa_routes.py` (PWA API Routes)

### **Ziel-Verzeichnis auf Hetzner:**
- `/opt/bess-simulation/instance/` (für Datenbank-Backup)
- `/opt/bess-simulation/static/` (für PWA-Assets)
- `/opt/bess-simulation/app/` (für PWA-Routes)

## 🆕 **Neue Features nach Deployment:**

### **PWA-Features:**
- **PWA Dashboard:** `https://bess.instanet.at/pwa/`
- **Offline-Funktionalität:** Vollständige Simulationen ohne Internet
- **Push-Notifications:** Native Benachrichtigungen
- **App-Installation:** "Zur Startseite hinzufügen"
- **Native Features:** Camera, GPS, Biometric-Auth

### **Advanced Dispatch & Grid Services:**
- **Multi-Markt-Arbitrage:** Spot, Intraday, Regelreserve
- **Grid-Services:** Frequenzregelung, Spannungshaltung
- **Virtuelles Kraftwerk:** VPP Portfolio-Optimierung
- **Demand Response:** Automatisierte Events
- **Grid Code Compliance:** Österreichische Standards

## 🔍 **Post-Deployment Tests:**

### **1. Service-Status prüfen:**
```bash
sudo systemctl status bess
curl -I https://bess.instanet.at/
```

### **2. PWA-Features testen:**
- PWA Dashboard: `https://bess.instanet.at/pwa/`
- Service Worker: Browser DevTools → Application → Service Workers
- Offline-Modus: DevTools → Network → Offline

### **3. Advanced Dispatch testen:**
- Dashboard: `https://bess.instanet.at/advanced-dispatch/`
- API-Endpoints: `/advanced-dispatch/api/*`
- Optimierung: Standard vs. Advanced

### **4. Datenbank-Integrität:**
```bash
cd /opt/bess-simulation
python -c "from app import create_app, get_db; app = create_app(); print('✅ Datenbank OK')"
```

## 📊 **Monitoring & Logs:**

### **Service-Logs:**
```bash
sudo journalctl -u bess -f
```

### **Application-Logs:**
```bash
tail -f /opt/bess-simulation/logs/bess_simulation.log
```

### **Nginx-Logs:**
```bash
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

## 🚨 **Rollback-Plan (falls nötig):**

### **1. Service stoppen:**
```bash
sudo systemctl stop bess
```

### **2. Zurück zur vorherigen Version:**
```bash
cd /opt/bess-simulation
git reset --hard HEAD~1
```

### **3. Service neu starten:**
```bash
sudo systemctl start bess
```

## ✅ **Deployment-Status:**

- [ ] SSH-Verbindung etabliert
- [ ] Service gestoppt
- [ ] Backup erstellt
- [ ] Git-Update durchgeführt
- [ ] Dependencies installiert
- [ ] Service gestartet
- [ ] PWA-Features getestet
- [ ] Advanced Dispatch getestet
- [ ] Monitoring aktiviert

## 📞 **Support-Kontakt:**

**Bei Problemen:**
- **Logs prüfen:** `sudo journalctl -u bess -f`
- **Service-Status:** `sudo systemctl status bess`
- **Git-Status:** `git status` in `/opt/bess-simulation`

---

**🎯 Ziel:** Erfolgreiches Deployment der BESS-Simulation v2.2 mit PWA-Features auf Hetzner-Server

