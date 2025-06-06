# Git Setup Script für NeuroScan Cloud Deployment (PowerShell)

Write-Host "🚀 Setting up Git for NeuroScan Cloud Deployment..." -ForegroundColor Green

# Git initialisieren
git init

# Git Konfiguration
git config user.name "NeuroCompany"
git config user.email "highnesspalm@gmail.com"

# .gitignore erstellen
$gitignoreContent = @"
# Python
__pycache__/
*.py[cod]
*`$py.class
*.so
.Python
env/
venv/
ENV/
env.bak/
venv.bak/

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.DS_Store

# Environment variables
.env
.env.local
.env.production
.env.staging

# Database
*.db
*.sqlite

# Logs
logs/
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
Thumbs.db
.DS_Store

# Build outputs
dist/
build/
*.egg-info/

# Docker
.dockerignore

# Render
.render/

# Vercel
.vercel

# Temporary files
tmp/
temp/
*.tmp
"@

$gitignoreContent | Out-File -FilePath ".gitignore" -Encoding UTF8

Write-Host "📝 Created .gitignore file" -ForegroundColor Yellow

# Alle Dateien hinzufügen
Write-Host "📦 Adding all files to Git..." -ForegroundColor Yellow
git add .

# Ersten Commit erstellen
Write-Host "💾 Creating initial commit..." -ForegroundColor Yellow
git commit -m "Initial NeuroScan cloud deployment setup

- Added Backend API (FastAPI + PostgreSQL)
- Added Web Frontend (Vue.js + Vite)  
- Added Desktop App (PySide6)
- Added Render.com configuration (render.yaml)
- Added Vercel.com configuration (vercel.json)
- Added cloud deployment documentation
- Ready for production deployment"

Write-Host ""
Write-Host "✅ Git repository successfully initialized!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Create GitHub repository: https://github.com/new" -ForegroundColor White
Write-Host "2. Repository name: neuroscan-system" -ForegroundColor White
Write-Host "3. Add remote: git remote add origin https://github.com/YOUR_USERNAME/neuroscan-system.git" -ForegroundColor White
Write-Host "4. Push to GitHub: git push -u origin main" -ForegroundColor White
Write-Host "5. Deploy to Render.com and Vercel.com" -ForegroundColor White
Write-Host ""
Write-Host "📚 Read CLOUD_DEPLOYMENT_GUIDE.md for detailed instructions" -ForegroundColor Yellow
