# NeuroScan Cloud Deployment Guide

## 🌐 Cloud Migration: Von lokal zu 24/7 Online

Dieses Dokument beschreibt die Migration des NeuroScan-Systems von lokaler Docker-Umgebung zu kostenfreien Cloud-Plattformen.

### 🎯 Ziel-Architektur

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   Database      │
│   (Vercel)      │───▶│   (Render)      │───▶│   PostgreSQL    │
│   Vue.js        │    │   FastAPI       │    │   (Render)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
   verify.domain.com    api.domain.com         (automatisch)
```

### 📋 Deployment-Checkliste

#### Phase 1: Backend (Render.com)
- [ ] Repository zu GitHub pushen
- [ ] Render.com Service erstellen
- [ ] Umgebungsvariablen konfigurieren
- [ ] PostgreSQL Datenbank verbinden
- [ ] Health Check testen

#### Phase 2: Frontend (Vercel.com)
- [ ] Repository mit Vercel verbinden
- [ ] Build-Konfiguration prüfen
- [ ] API-URL auf Render Backend setzen
- [ ] Deployment testen

#### Phase 3: Domain-Konfiguration
- [ ] Custom Domain kaufen (optional)
- [ ] Subdomains konfigurieren
- [ ] SSL-Zertifikate prüfen

## 🚀 Schnellstart

### 1. Repository vorbereiten
```bash
# Git Repository initialisieren (falls noch nicht vorhanden)
git init
git add .
git commit -m "Initial commit - NeuroScan Cloud Migration"

# GitHub Repository erstellen und pushen
git remote add origin https://github.com/IhrUsername/neuroscan.git
git push -u origin main
```

### 2. Render.com Backend Deployment

1. **Service erstellen:**
   - Gehen Sie zu https://render.com/dashboard
   - Klicken Sie "New +" → "Blueprint"
   - Repository: Ihr GitHub NeuroScan Repository
   - Blueprint Path: `render.yaml`

2. **Umgebungsvariablen:**
   Die wichtigsten Variablen werden automatisch über `render.yaml` gesetzt:
   - `DATABASE_URL` (automatisch von PostgreSQL Service)
   - `JWT_SECRET_KEY` (automatisch generiert)
   - `CORS_ORIGINS` (Frontend URLs)

3. **Health Check:**
   ```bash
   curl https://neuroscan-api.onrender.com/health
   ```

### 3. Vercel.com Frontend Deployment

1. **Projekt verbinden:**
   - Gehen Sie zu https://vercel.com/dashboard
   - Klicken Sie "New Project"
   - Repository: Ihr GitHub NeuroScan Repository
   - Framework: Vite (automatisch erkannt)

2. **Build Settings:**
   - Build Command: `cd WebFrontend && npm install && npm run build`
   - Output Directory: `WebFrontend/dist`
   - Install Command: `cd WebFrontend && npm install`

3. **Umgebungsvariablen:**
   ```
   VITE_API_URL=https://neuroscan-api.onrender.com
   VITE_ENVIRONMENT=production
   ```

## 🔧 Konfiguration

### Backend Environment (.env)
```env
# Automatisch von Render gesetzt
DATABASE_URL=postgresql://user:pass@host:port/dbname
REDIS_URL=redis://host:port
JWT_SECRET_KEY=auto-generated-secret

# Manuell konfigurieren
ENVIRONMENT=production
DEBUG=false
CORS_ORIGINS=https://neuroscan.vercel.app
```

### Frontend Environment
```env
VITE_API_URL=https://neuroscan-api.onrender.com
VITE_ENVIRONMENT=production
```

## 🌐 Domain-Konfiguration (Optional)

### Ziel-URLs:
- **API**: `https://api.neuroscan.io`
- **Verifikation**: `https://verify.neuroscan.io`
- **Portal**: `https://portal.neuroscan.io`

### DNS-Einstellungen:
```
Type  Name    Value
CNAME api     neuroscan-api.onrender.com
CNAME verify  neuroscan.vercel.app
CNAME portal  neuroscan.vercel.app
```

## 📊 Monitoring & Wartung

### Render.com Dashboard:
- **Logs**: Echtzeit-Logs anzeigen
- **Metrics**: CPU/Memory Usage
- **Health**: Service Status

### Vercel.com Dashboard:
- **Deployments**: Build-Historie
- **Analytics**: Seitenaufrufe
- **Functions**: Edge Functions Status

## 🆓 Kostenübersicht

| Service | Plan | Limits | Kosten |
|---------|------|--------|---------|
| Render | Free | 750h/Monat | €0 |
| Vercel | Hobby | 100GB Bandwidth | €0 |
| GitHub | Public Repos | Unlimited | €0 |
| **Total** | | | **€0/Monat** |

## 🔒 Sicherheit

### SSL/TLS:
- ✅ Automatisch von Render/Vercel bereitgestellt
- ✅ HTTPS-Weiterleitung aktiviert
- ✅ HSTS Headers gesetzt

### Authentifizierung:
- ✅ JWT Token Security
- ✅ CORS konfiguriert
- ✅ Rate Limiting aktiv

## 🚨 Troubleshooting

### Häufige Probleme:

1. **Build Fehler:**
   ```bash
   # Frontend Build prüfen
   cd WebFrontend
   npm install
   npm run build
   ```

2. **API Connection:**
   ```bash
   # Backend Health Check
   curl https://neuroscan-api.onrender.com/health
   ```

3. **CORS Fehler:**
   - Vercel URL zu CORS_ORIGINS hinzufügen
   - Render Service neu starten

## 📞 Support

Bei Problemen:
1. Render Logs prüfen: Dashboard → Service → Logs
2. Vercel Build Logs: Dashboard → Project → Functions
3. GitHub Issues erstellen für Code-Probleme
