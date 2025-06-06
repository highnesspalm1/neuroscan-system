# 🌐 NeuroScan Cloud-Deployment Guide

## 🎯 Ziel
Migration des lokalen NeuroScan-Systems auf kostenfreie Cloud-Plattformen:
- **Backend**: Render.com (kostenlos)
- **Frontend**: Vercel.com (kostenlos)
- **Datenbank**: PostgreSQL auf Render (kostenlos)

---

## 📋 Voraussetzungen
- ✅ Render.com Account
- ✅ Vercel.com Account
- ✅ GitHub Account (für Repository)

---

## 🚀 Deployment-Schritte

### Schritt 1: Git Repository erstellen

```powershell
# Git initialisieren (wenn noch nicht geschehen)
git init

# Git-Konfiguration
git config user.name "NeuroCompany"
git config user.email "highnesspalm@gmail.com"

# Alle Dateien hinzufügen
git add .

# Ersten Commit erstellen
git commit -m "Initial NeuroScan cloud deployment setup"
```

### Schritt 2: GitHub Repository erstellen

1. Gehe zu [GitHub.com](https://github.com)
2. Klicke auf "New Repository"
3. Repository Name: `neuroscan-system`
4. Beschreibung: `NeuroScan Premium Product Authentication System`
5. Public Repository wählen
6. Erstelle Repository

### Schritt 3: Code zu GitHub pushen

```powershell
# Remote Repository hinzufügen
git remote add origin https://github.com/IHR_USERNAME/neuroscan-system.git

# Code hochladen
git branch -M main
git push -u origin main
```

---

## 🖥️ Backend Deployment (Render.com)

### 1. Neuen Service erstellen
1. Gehe zu [Render Dashboard](https://dashboard.render.com/)
2. Klicke "New +" → "Web Service"
3. Verbinde GitHub Repository: `neuroscan-system`

### 2. Service Konfiguration
- **Name**: `neuroscan-api`
- **Environment**: `Python 3`
- **Build Command**: 
  ```bash
  cd BackendAPI && pip install -r requirements.txt
  ```
- **Start Command**: 
  ```bash
  cd BackendAPI && uvicorn main:app --host 0.0.0.0 --port $PORT
  ```

### 3. Umgebungsvariablen setzen
```
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=[wird automatisch von PostgreSQL DB gesetzt]
JWT_SECRET_KEY=[generiere sicheren Schlüssel]
CORS_ORIGINS=https://neuroscan-frontend.vercel.app
```

### 4. PostgreSQL Datenbank hinzufügen
1. In Render Dashboard: "New +" → "PostgreSQL"
2. **Name**: `neuroscan-db`
3. **Plan**: Free
4. Nach Erstellung: DATABASE_URL automatisch im Backend Service verfügbar

---

## 🌐 Frontend Deployment (Vercel.com)

### 1. Neues Projekt erstellen
1. Gehe zu [Vercel Dashboard](https://vercel.com/dashboard)
2. "Add New..." → "Project"
3. GitHub Repository importieren: `neuroscan-system`

### 2. Build Konfiguration
- **Framework Preset**: Vue.js
- **Root Directory**: `WebFrontend`
- **Build Command**: `npm run build`
- **Output Directory**: `dist`

### 3. Umgebungsvariablen setzen
```
VITE_API_URL=https://neuroscan-api.onrender.com
VITE_ENVIRONMENT=production
```

---

## 🔧 Finale Konfiguration

### Backend API URL aktualisieren
Nach dem Render-Deployment die tatsächliche URL im Frontend aktualisieren:

1. Render URL notieren (z.B. `https://neuroscan-api-xyz.onrender.com`)
2. In Vercel Environment Variables `VITE_API_URL` entsprechend anpassen

### CORS Konfiguration
Im Backend die Vercel URL zu CORS_ORIGINS hinzufügen:
```
CORS_ORIGINS=https://neuroscan-system-xyz.vercel.app
```

---

## 🌍 Domain-Setup (Optional)

### Custom Domains einrichten:
- **API**: `api.neuroscan.io` → Render Service
- **Frontend**: `verify.neuroscan.io` → Vercel App
- **Portal**: `portal.neuroscan.io` → Vercel App (zweites Deployment)

---

## ✅ Deployment-Checkliste

### Backend (Render):
- [ ] Repository mit Render verbunden
- [ ] PostgreSQL Datenbank erstellt
- [ ] Umgebungsvariablen konfiguriert
- [ ] Service startet erfolgreich
- [ ] API Health Check funktioniert

### Frontend (Vercel):
- [ ] Repository mit Vercel verbunden
- [ ] Build erfolgreich
- [ ] Umgebungsvariablen gesetzt
- [ ] Frontend lädt korrekt
- [ ] API-Verbindung funktioniert

### Funktionalität:
- [ ] QR-Code Verifikation funktioniert
- [ ] Admin-Login funktioniert
- [ ] Zertifikat-Generierung funktioniert
- [ ] Dashboard zeigt Daten an

---

## 🔗 Finale URLs

Nach erfolgreichem Deployment:
- **API**: `https://neuroscan-api.onrender.com`
- **Frontend**: `https://neuroscan-system.vercel.app`
- **API Docs**: `https://neuroscan-api.onrender.com/docs`

---

## 🆘 Troubleshooting

### Häufige Probleme:
1. **Build Fehler**: Überprüfe requirements.txt und package.json
2. **CORS Fehler**: Vercel URL zu CORS_ORIGINS hinzufügen
3. **DB Connection**: DATABASE_URL in Render Umgebungsvariablen prüfen
4. **Umgebungsvariablen**: Alle notwendigen Variablen gesetzt?

### Support:
- Render Logs: Dashboard → Service → Logs
- Vercel Logs: Dashboard → Projekt → Functions Tab
