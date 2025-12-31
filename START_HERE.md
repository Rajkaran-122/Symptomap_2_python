# 🚀 Doctor Station - Quick Start Guide

Welcome to the SymptoMap Doctor Station! This guide will get you up and running in 5 minutes.

---

## 📋 What is This?

A **secure, password-protected web portal** for healthcare professionals to:
- ✅ Submit disease outbreak data with patient counts
- ✅ Mark exact locations on interactive maps  
- ✅ Create health alerts for regions
- ✅ View real-time statistics on public dashboard

All data appears **instantly** on the main dashboard for public health monitoring.

---

## ⚡ 3-Minute Quick Start

### Option 1: Automated Start (Recommended)

**Windows:**
```batch
.\start.bat
```

**Mac/Linux:**
```bash
chmod +x start.sh
./start.sh
```

### Option 2: Manual Start

**Terminal 1 - Backend:**
```bash
cd backend-python
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Option 3: Docker (Production)

```bash
docker-compose up -d
```

---

## 🌐 Access the Application

Once started, open your browser:

| Service | URL | Purpose |
|---------|-----|---------|
| **Doctor Portal** | [http://localhost:3000/doctor](http://localhost:3000/doctor) | Submit outbreaks & alerts |
| **Main Dashboard** | [http://localhost:3000/dashboard](http://localhost:3000/dashboard) | View all data |
| **API Docs** | [http://localhost:8000/api/docs](http://localhost:8000/api/docs) | API documentation |

### Default Credentials

```
🔑 Password: Doctor@SymptoMap2025
```

*Note: Password is displayed on the login page for easy access*

---

## ✅ Quick Test

1. **Open Doctor Portal**: http://localhost:3000/doctor
2. **Login** with password: `Doctor@SymptoMap2025`
3. **Submit a Test Outbreak**:
   - Disease: Dengue
   - Patients: 10
   - Severity: Moderate
   - Click on map to mark location
   - Submit
4. **View Dashboard**: http://localhost:3000/dashboard
5. **See your submission** in "Recent Doctor Submissions" section

---

## 📚 Next Steps

### For Doctors (Users)
👉 **Read**: [USER_MANUAL.md](./USER_MANUAL.md)  
Complete step-by-step guide on using the portal

### For Developers
👉 **Read**: [PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md)  
Full technical details and architecture

### For Deployment
👉 **Read**: [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)  
Deploy to production (Render, Railway, Docker, etc.)

### Quick Reference
👉 **Read**: [QUICK_REFERENCE.md](./QUICK_REFERENCE.md)  
Command cheat sheet for common tasks

---

## 🆘 Troubleshooting

### Backend won't start
```bash
# Check Python version (need 3.8+)
python --version

# Install dependencies
cd backend-python
pip install -r requirements.txt
```

### Frontend won't start
```bash
# Check Node version (need 16+)
node --version

# Install dependencies
cd frontend
npm install
```

### Port already in use
```bash
# Windows: Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# Mac/Linux: Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

### Can't login
- Ensure password is exactly: `Doctor@SymptoMap2025` (case-sensitive)
- Check backend is running on port 8000
- Clear browser cache and cookies

---

## 🎯 Key Features

✅ **Secure Authentication** - JWT token-based, 24-hour sessions  
✅ **Interactive Maps** - Click to mark locations, search cities  
✅ **Real-time Dashboard** - Data appears within 30 seconds  
✅ **Mobile Responsive** - Works on phones, tablets, desktops  
✅ **Auto Backup** - Database backed up every 6 hours  
✅ **CSV Import/Export** - Bulk data operations  

---

## 📦 What's Included

```
📁 Doctor Station/
├── 📄 Backend (Python FastAPI)
│   ├── JWT Authentication
│   ├── Outbreak Management API
│   ├── Alert System API
│   └── SQLite Database
│
├── 🎨 Frontend (React + TypeScript)
│   ├── Doctor Login
│   ├── Outbreak Submission Form
│   ├── Alert Creation Form
│   ├── Interactive Map (OpenStreetMap)
│   └── Real-time Dashboard
│
├── 🐳 Docker Configuration
│   └── docker-compose.yml
│
├── 📝 Documentation (6 guides)
│   ├── START_HERE.md (this file)
│   ├── PROJECT_SUMMARY.md
│   ├── USER_MANUAL.md
│   ├── QUICK_REFERENCE.md
│   ├── DEPLOYMENT_GUIDE.md
│   └── DOCTOR_STATION_BRD.md
│
└── 🛠️ Utilities
    ├── Automated backup script
    ├── CSV import/export
    ├── Sample data generator
    └── Quick start scripts
```

---

## 🚀 Production Deployment

Ready to go live? Choose your platform:

### Free Hosting Options
- **Render.com** (Recommended) - Free tier, auto-deploy from Git
- **Railway.app** - Easy setup, generous free tier
- **Heroku** - Classic platform, simple deployment

### Professional Hosting
- **AWS/GCP/Azure** - Full control, scalable
- **DigitalOcean** - Affordable VPS
- **Self-hosted** - On your own server

👉 See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for detailed instructions

---

## 📞 Support & Help

### Documentation
- 📖 Complete guides in `docs/` folder
- 💻 API documentation at `/api/docs`
- 🎓 Video tutorials (coming soon)

### Issues & Bugs
- Create an issue on GitHub
- Check existing documentation first
- Provide error logs and screenshots

### Contributing
- Pull requests welcome!
- See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines

---

## 📊 System Requirements

### Minimum
- **OS**: Windows 10, macOS 10.15+, Linux (Ubuntu 20.04+)
- **Python**: 3.8 or higher
- **Node.js**: 16.0 or higher
- **RAM**: 2 GB
- **Disk**: 500 MB

### Recommended
- **Python**: 3.10+
- **Node.js**: 18+
- **RAM**: 4 GB
- **Disk**: 1 GB

---

## 🎉 Success!

If you see the Doctor Portal login page, **congratulations!** You're all set.

### What's Next?

1. ✅ Login and submit a test outbreak
2. ✅ View it on the dashboard
3. ✅ Read the USER_MANUAL for detailed usage
4. ✅ Deploy to production when ready
5. ✅ Share the link with doctors!

---

## 📝 License

This project is open source. See [LICENSE](./LICENSE) for details.

---

## 🌟 Quick Links

| Resource | Link |
|----------|------|
| Doctor Portal | http://localhost:3000/doctor |
| Dashboard | http://localhost:3000/dashboard |
| API Docs | http://localhost:8000/api/docs |
| GitHub Issues | (your-repo-url) |
| Documentation | [Project Summary](./PROJECT_SUMMARY.md) |

---

**Made with ❤️ for public health monitoring**

*Last Updated: December 2025*
