# Doctor Station Deployment Guide

## Complete Setup

Your Doctor Station is now ready to deploy! Here's everything you need to know:

## 📦 What's Included

1. **Doctor Login Portal** - `/doctor`
2. **Doctor Dashboard** - `/doctor/station`  
3. **Outbreak Submission Form** - Disease reporting with map
4. **Alert Creation System** - Real-time health alerts
5. **Main Dashboard Integration** - Data appears instantly

## 🔑 Access Credentials

**Login URL**: `http://yourdomain.com/doctor`  
**Password**: `Doctor@SymptoMap2025`

## 🚀 Deployment Steps

### Option 1: Quick Local Test
```powershell
# Backend (Terminal 1)
cd backend-python
$env:PYTHONPATH="$PWD"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Frontend (Terminal 2)
cd frontend
npm run dev
```

Access at: `http://localhost:3000/doctor`

### Option 2: Docker Deployment (Production)

1. **Start Docker Desktop**

2. **Build and Run**:
```powershell
docker compose up -d --build
```

3. **Access**:
- Doctor Portal: `http://localhost:3000/doctor`
- Main Dashboard: `http://localhost:3000/dashboard`
- API Docs: `http://localhost:8000/api/docs`

### Option 3: Cloud Deployment

#### Using Render/Railway/Heroku:

1. Push code to GitHub
2. Connect repository to platform
3. Set environment variables:
```
DATABASE_URL=sqlite:///symptomap.db
REDIS_URL=redis://localhost:6379
JWT_SECRET_KEY=your-secret-key-here
```
4. Deploy!

#### Share this link with doctors:
```
https://your-app-name.onrender.com/doctor
```

## 📊 Database

**Type**: SQLite (`symptomap.db`)  
**Tables**:
- `doctor_outbreaks` - Outbreak submissions
- `doctor_alerts` - Alert notifications

**Backup**:
```powershell
copy symptomap.db symptomap_backup.db
```

## 🔐 Security

### Change Default Password

Edit `backend-python/app/api/v1/auth_doctor.py`:
```python
DOCTOR_PASSWORD = "YourNewSecurePassword123!"
```

### Enable HTTPS (Production)

1. Get SSL certificate (Let's Encrypt)
2. Update nginx config
3. Force HTTPS redirects

## 📝 How Doctors Use It

1. **Login** - Go to `/doctor`, enter password
2. **Submit Outbreak**:
   - Select disease type
   - Enter patient count
   - Choose severity
   - Mark location on map
   - Add description
   - Submit

3. **Create Alert**:
   - Choose alert type (Info/Warning/Critical)
   - Write title and message
   - Set affected area
   - Set expiry time
   - Submit

4. **View Submissions** - See all submitted data

## 🎯 Features

✅ Password-protected access  
✅ Real-time data updates (30s refresh)  
✅ Mobile-responsive design  
✅ Interactive map location picker  
✅ Database persistence  
✅ API integration  
✅ Dashboard visibility  

## 📡 API Endpoints

### Public (No Auth Required)
- `GET /api/v1/outbreaks/all` - All outbreaks

### Doctor (Auth Required)
- `POST /api/v1/doctor/login` - Login
- `POST /api/v1/doctor/outbreak` - Submit outbreak
- `POST /api/v1/doctor/alert` - Create alert
- `GET /api/v1/doctor/submissions` - View data
- `GET /api/v1/doctor/stats` - Statistics

## 🔧 Troubleshooting

**Login fails**: Check password in `auth_doctor.py`  
**Data not showing**: Restart backend server  
**Map not loading**: Check browser console for errors  
**Database locked**: Close other connections  

## 📞 Support

The system is fully functional and ready to share!

Share URL: `http://localhost:3000/doctor` (local)  
Or deploy to cloud and share your production URL.
