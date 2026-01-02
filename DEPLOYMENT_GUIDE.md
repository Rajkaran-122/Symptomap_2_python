# 🚀 SymptoMap Deployment Guide

Complete guide to deploy SymptoMap to production with various platforms.

---

## 📋 Table of Contents

1. [Deployment Options Overview](#-deployment-options-overview)
2. [Render.com (Recommended - Free)](#-rendercom-recommended)
3. [Railway.app](#-railwayapp)
4. [Vercel + Render Combo](#-vercel--render)
5. [Docker Self-Hosted](#-docker-self-hosted)
6. [Environment Variables](#-environment-variables)
7. [Post-Deployment Checklist](#-post-deployment-checklist)

---

## 🎯 Deployment Options Overview

| Platform | Backend | Frontend | Cost | Difficulty |
|----------|---------|----------|------|------------|
| **Render.com** | ✅ Free | ✅ Free | $0/month | ⭐ Easy |
| **Railway.app** | ✅ Free tier | ✅ Free tier | $0-5/month | ⭐ Easy |
| **Vercel + Render** | Render | Vercel | $0/month | ⭐⭐ Medium |
| **Docker (VPS)** | Docker | Docker | $5+/month | ⭐⭐⭐ Advanced |
| **AWS/GCP/Azure** | ECS/Cloud Run | S3/CDN | $10+/month | ⭐⭐⭐⭐ Complex |

**Recommendation:** Start with **Render.com** - it's free, easy, and supports both backend + frontend.

---

## 🌟 Render.com (Recommended)

### Step 1: Prepare Your Repository

Make sure your code is pushed to GitHub:
```bash
git add -A
git commit -m "Ready for deployment"
git push origin main
```

### Step 2: Deploy Backend (Web Service)

1. Go to [render.com](https://render.com) and sign up/login
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:

| Setting | Value |
|---------|-------|
| **Name** | `symptomap-api` |
| **Region** | Oregon (US West) |
| **Branch** | `main` |
| **Root Directory** | `backend-python` |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| **Plan** | Free |

5. Add Environment Variables:
   - `JWT_SECRET_KEY` = (click "Generate")
   - `DOCTOR_PASSWORD` = `Doctor@SymptoMap2025`

6. Click **"Create Web Service"**

7. Wait for deployment (~5 minutes)

8. Note your backend URL: `https://symptomap-api.onrender.com`

### Step 3: Deploy Frontend (Static Site)

1. Click **"New +"** → **"Static Site"**
2. Connect the same repository
3. Configure:

| Setting | Value |
|---------|-------|
| **Name** | `symptomap-frontend` |
| **Branch** | `main` |
| **Root Directory** | `frontend` |
| **Build Command** | `npm install && npm run build` |
| **Publish Directory** | `dist` |

4. Add Environment Variable:
   - `VITE_API_URL` = `https://symptomap-api.onrender.com/api/v1`

5. Click **"Create Static Site"**

6. Add Rewrite Rule (Settings → Redirects/Rewrites):
   - Source: `/*`
   - Destination: `/index.html`
   - Action: Rewrite

### Step 4: Access Your Live App

- **Dashboard:** `https://symptomap-frontend.onrender.com/dashboard`
- **Doctor Portal:** `https://symptomap-frontend.onrender.com/doctor`
- **API Docs:** `https://symptomap-api.onrender.com/docs`

---

## 🚂 Railway.app

### Quick Deploy

1. Go to [railway.app](https://railway.app) and login with GitHub
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select your repository

### Backend Service

```bash
# In Railway dashboard, create new service
# Set these variables:
ROOT_DIRECTORY=backend-python
NIXPACKS_PYTHON_VERSION=3.11
PORT=8000
```

Start Command:
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Frontend Service

```bash
# Create another service for frontend
ROOT_DIRECTORY=frontend
NIXPACKS_NODE_VERSION=18
```

Build Command:
```bash
npm install && npm run build
```

### Connect Services

1. Get your backend URL from Railway
2. Set `VITE_API_URL` in frontend service
3. Redeploy frontend

---

## ⚡ Vercel + Render

Best for: **Frontend on Vercel (fast CDN) + Backend on Render**

### Step 1: Deploy Backend to Render

Follow the Render backend steps above.

### Step 2: Deploy Frontend to Vercel

1. Go to [vercel.com](https://vercel.com) and login
2. Click **"Add New Project"**
3. Import your GitHub repository
4. Configure:

| Setting | Value |
|---------|-------|
| **Framework Preset** | Vite |
| **Root Directory** | `frontend` |
| **Build Command** | `npm run build` |
| **Output Directory** | `dist` |

5. Add Environment Variable:
   - `VITE_API_URL` = `https://symptomap-api.onrender.com/api/v1`

6. Click **"Deploy"**

---

## 🐳 Docker Self-Hosted

For VPS/dedicated servers (DigitalOcean, Linode, AWS EC2, etc.)

### Prerequisites

- Docker 24+
- Docker Compose 2+
- A server with 1GB+ RAM

### Deploy

```bash
# Clone repository
git clone https://github.com/Rajkaran-122/Symptomap_2_python.git
cd Symptomap_2_python

# Create production environment file
cp .env.example .env
nano .env  # Edit with production values

# Build and start containers
docker-compose up -d --build

# Check status
docker-compose ps
docker-compose logs -f
```

### With Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/symptomap
server {
    listen 80;
    server_name symptomap.yourdomain.com;

    location / {
        proxy_pass http://localhost:80;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### SSL with Certbot

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d symptomap.yourdomain.com
```

---

## 🔐 Environment Variables

### Backend Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `JWT_SECRET_KEY` | ✅ Yes | - | Secret key for JWT tokens (generate random string) |
| `JWT_ALGORITHM` | No | HS256 | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_HOURS` | No | 24 | Token expiry time |
| `DOCTOR_PASSWORD` | ✅ Yes | Doctor@SymptoMap2025 | Doctor login password |
| `DATABASE_URL` | No | sqlite:///./symptomap.db | Database connection URL |
| `CORS_ORIGINS` | No | * | Allowed CORS origins |

### Frontend Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_API_URL` | ✅ Yes | Backend API URL (e.g., `https://api.symptomap.com/api/v1`) |

### Generate Secure JWT Secret

```bash
# Python
python -c "import secrets; print(secrets.token_hex(32))"

# OpenSSL
openssl rand -hex 32
```

---

## ✅ Post-Deployment Checklist

### 1. Verify Backend
```bash
# Health check
curl https://your-api-url.com/health

# API docs
open https://your-api-url.com/docs
```

### 2. Verify Frontend
```bash
# Check all pages load
open https://your-frontend-url.com/dashboard
open https://your-frontend-url.com/doctor
open https://your-frontend-url.com/admin/approvals
```

### 3. Test Full Workflow
- [ ] Login at `/doctor` with password
- [ ] Submit test outbreak
- [ ] Approve at `/admin/approvals`
- [ ] Verify on `/dashboard` map

### 4. Security Checklist
- [ ] Changed default `DOCTOR_PASSWORD`
- [ ] Set strong `JWT_SECRET_KEY`
- [ ] HTTPS enabled
- [ ] CORS configured for your domain only

### 5. Monitoring
- Set up uptime monitoring (UptimeRobot, Pingdom)
- Enable error tracking (Sentry)
- Configure log aggregation

---

## 🆘 Troubleshooting

### Backend won't start
```bash
# Check logs
docker-compose logs backend
# or on Render: check "Logs" tab
```

### Frontend shows API errors
- Verify `VITE_API_URL` is set correctly
- Check CORS settings in backend
- Ensure backend is running

### Database issues
- SQLite file permissions
- For production, consider PostgreSQL

### CORS errors
Add your frontend URL to backend CORS settings:
```python
# In app/main.py
CORS_ORIGINS = ["https://your-frontend.com"]
```

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/Rajkaran-122/Symptomap_2_python/issues)
- **Docs:** Check `README.md` and other `.md` files in repo

---

**Happy Deploying! 🚀**
