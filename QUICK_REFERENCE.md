# ⚡ Quick Reference Card

**SymptoMap Doctor Station - Command Cheat Sheet**

---

## 🚀 Startup Commands

### Start Everything (Quick)
```bash
# Windows
.\start.bat

# Mac/Linux
./start.sh
```

### Start Backend Only
```bash
cd backend-python
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Start Frontend Only
```bash
cd frontend
npm run dev
```

### Docker Start
```bash
docker-compose up -d
```

---

## 🔧 Development Commands

### Backend Setup
```bash
cd backend-python
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev          # Development
npm run build        # Production build
npm run preview      # Preview build
```

### Database Commands
```bash
# Backup
python scripts/backup.py

# Import CSV
python scripts/import_csv.py data/outbreaks.csv

# Export CSV
python scripts/export_csv.py output/export.csv
```

---

## 🌐 URLs & Endpoints

### Frontend URLs
```
Doctor Login:    http://localhost:3000/doctor
Doctor Station:  http://localhost:3000/doctor/station
Main Dashboard:  http://localhost:3000/dashboard
Home Page:       http://localhost:3000/
```

### Backend URLs
```
API Base:        http://localhost:8000/api/v1
API Docs:        http://localhost:8000/api/docs
Health Check:    http://localhost:8000/health
```

---

## 📡 API Endpoints

### Authentication
```http
POST /api/v1/doctor/login
Body: { "password": "Doctor@SymptoMap2025" }
```

### Outbreak Management
```http
POST /api/v1/doctor/outbreak
Header: Authorization: Bearer {token}
Body: { disease_type, patient_count, severity, latitude, longitude, ... }

GET /api/v1/outbreaks/all
Public endpoint - no auth required
```

### Alert Management
```http
POST /api/v1/doctor/alert
Header: Authorization: Bearer {token}
Body: { alert_type, title, message, latitude, longitude, ... }

GET /api/v1/doctor/submissions
Header: Authorization: Bearer {token}
```

---

## 🔑 Default Credentials

```
URL:      http://localhost:3000/doctor
Password: Doctor@SymptoMap2025
Token:    Valid for 24 hours
```

---

## 🐳 Docker Commands

### Basic Operations
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Build images
docker-compose build

# Remove everything
docker-compose down -v
```

### Individual Services
```bash
# Backend only
docker-compose up -d backend

# Frontend only
docker-compose up -d frontend

# View specific logs
docker-compose logs -f backend
```

---

## 💾 Database Operations

### Backup
```bash
# Manual backup
python scripts/backup.py

# Scheduled backup (cron - Mac/Linux)
0 */6 * * * python /path/to/scripts/backup.py

# Windows Task Scheduler
schtasks /create /tn "Backup SymptoMap" /tr "python C:\path\to\scripts\backup.py" /sc hourly /mo 6
```

### Import/Export
```bash
# Import outbreaks from CSV
python scripts/import_csv.py data/sample_outbreaks.csv

# Export to CSV
python scripts/export_csv.py export/outbreaks_$(date +%Y%m%d).csv

# Direct SQL
sqlite3 symptomap.db "SELECT * FROM doctor_outbreaks;"
```

### Manual Database
```bash
# Open database
sqlite3 symptomap.db

# Common queries
SELECT COUNT(*) FROM doctor_outbreaks;
SELECT * FROM doctor_outbreaks WHERE city='Jaipur';
SELECT * FROM doctor_alerts WHERE status='active';
```

---

## 🧪 Testing

### Run Tests
```bash
# Python tests
cd backend-python
python -m pytest tests/ -v

# TypeScript tests
cd frontend
npm test

# With coverage
npm test -- --coverage
```

### API Testing
```bash
# Using curl
curl -X POST http://localhost:8000/api/v1/doctor/login \
  -H "Content-Type: application/json" \
  -d '{"password":"Doctor@SymptoMap2025"}'

# Using httpie
http POST localhost:8000/api/v1/doctor/login password="Doctor@SymptoMap2025"
```

---

## 📦 Deployment

### Render.com
```bash
# Connect GitHub repo
git remote add render https://github.com/your-repo
git push render main

# Environment variables (set in Render dashboard):
DATABASE_URL=sqlite:///symptomap.db
SECRET_KEY=your-secret-key
```

### Railway
```bash
railway login
railway init
railway up

# Auto-deploy on push
git push railway main
```

### Traditional VPS
```bash
# Ubuntu setup
sudo apt update
sudo apt install python3-pip nodejs npm nginx

# Clone repo
git clone <your-repo-url>
cd symptomap

# Setup
./start.sh

# Nginx config
sudo cp nginx.conf /etc/nginx/sites-available/symptomap
sudo ln -s /etc/nginx/sites-available/symptomap /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🔧 Troubleshooting

### Kill Processes
```bash
# Windows
# Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# Kill process on port 3000
netstat -ano | findstr :3000
taskkill /PID <process_id> /F

# Mac/Linux
# Kill on port 8000
lsof -ti:8000 | xargs kill -9

# Kill on port 3000
lsof -ti:3000 | xargs kill -9
```

### Clear Cache
```bash
# Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Node modules
rm -rf node_modules package-lock.json
npm install

# Build cache
rm -rf .vite dist build
```

### Reset Database
```bash
# Backup first!
cp symptomap.db symptomap_backup.db

# Delete database
rm symptomap.db

# Restart backend (auto-creates)
cd backend-python
python -m uvicorn app.main:app --reload
```

---

## 📊 Useful Scripts

### Generate Sample Data
```python
# Python script
python scripts/generate_sample_data.py --outbreaks 50 --alerts 10
```

### Check System Status
```bash
# Quick health check
curl http://localhost:8000/health
curl http://localhost:3000
```

### View Logs
```bash
# Backend logs
tail -f backend-python/logs/app.log

# Frontend logs (browser console)
# Open: http://localhost:3000
# Press F12 -> Console

# Docker logs
docker-compose logs --tail=100 -f
```

---

## 🎨 Code Formatting

### Python
```bash
# Format code
black backend-python/

# Lint
flake8 backend-python/

# Type check
mypy backend-python/
```

### TypeScript
```bash
# Format
cd frontend
npx prettier --write "src/**/*.{ts,tsx}"

# Lint
npm run lint

# Fix auto-fixable issues
npm run lint -- --fix
```

---

## 🔐 Security

### Generate Secret Key
```python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Password Hash (if implementing)
```python
import bcrypt
password = b"Doctor@SymptoMap2025"
hashed = bcrypt.hashpw(password, bcrypt.gensalt())
print(hashed)
```

---

## 📁 File Paths

### Important Files
```
Configuration:
  .env
  docker-compose.yml
  nginx.conf

Backend:
  backend-python/app/main.py
  backend-python/app/api/v1/auth_doctor.py
  backend-python/requirements.txt

Frontend:
  frontend/src/App.tsx
  frontend/src/pages/DoctorStation.tsx
  frontend/package.json

Database:
  symptomap.db
  backups/

Scripts:
  scripts/backup.py
  scripts/import_csv.py
  scripts/export_csv.py
```

---

## 🚨 Emergency Commands

### Quick Fix
```bash
# Stop everything
docker-compose down
pkill -f uvicorn
pkill -f "npm run dev"

# Clean start
rm -rf node_modules .vite dist
npm install
docker-compose up -d --build
```

### Database Restore
```bash
# From latest backup
cp backups/symptomap_backup_<latest>.db symptomap.db

# Restart services
docker-compose restart
```

---

## 📋 Checklists

### Pre-Deployment
- [ ] Set environment variables
- [ ] Change default password
- [ ] Test all features
- [ ] Run tests
- [ ] Backup database
- [ ] Configure HTTPS
- [ ] Set up monitoring
- [ ] Review security settings

### Post-Deployment
- [ ] Verify URLs work
- [ ] Test doctor login
- [ ] Submit test outbreak
- [ ] Check dashboard updates
- [ ] Test mobile view
- [ ] Monitor logs
- [ ] Set up backups
- [ ] Document any changes

---

## 🔗 Quick Links

| Resource | Link |
|----------|------|
| Doctor Portal | http://localhost:3000/doctor |
| Dashboard | http://localhost:3000/dashboard |
| API Docs | http://localhost:8000/api/docs |
| GitHub | (your-repo-url) |
| Docs | START_HERE.md |

---

## 💡 Pro Tips

1. **Use aliases** for frequent commands:
   ```bash
   alias start-backend="cd backend-python && python -m uvicorn app.main:app --reload"
   alias start-frontend="cd frontend && npm run dev"
   ```

2. **Keep backups** before major changes:
   ```bash
   python scripts/backup.py
   ```

3. **Monitor logs** in separate terminals:
   ```bash
   # Terminal 1: Backend
   tail -f backend-python/logs/app.log
   
   # Terminal 2: Frontend  
   # Browser console (F12)
   ```

4. **Use environment files** for different environments:
   ```bash
   .env.development
   .env.production
   .env.local
   ```

---

**Last Updated**: December 2025  
**Version**: 1.0

*Keep this card handy for quick reference!* 📌
