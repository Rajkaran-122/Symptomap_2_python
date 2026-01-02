# 🏥 SymptoMap - Real-Time Disease Surveillance Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Node](https://img.shields.io/badge/Node.js-18%2B-green.svg)](https://nodejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18%2B-61DAFB.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5%2B-3178C6.svg)](https://www.typescriptlang.org/)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)]()

> **An AI-powered epidemiological surveillance platform for real-time disease outbreak tracking, prediction, and public health response coordination.**

---

## 🚀 Quick Start

### Prerequisites

| Requirement | Version | Check Command |
|-------------|---------|---------------|
| Python | 3.10+ | `python --version` |
| Node.js | 18+ | `node --version` |
| npm | 9+ | `npm --version` |
| Git | Latest | `git --version` |

### Installation & Setup

```bash
# 1. Clone the repository
git clone https://github.com/Rajkaran-122/Symptomap_2_python.git
cd Symptomap_2_python

# 2. Setup Backend (Terminal 1)
cd backend-python
python -m venv venv

# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 3. Setup Frontend (Terminal 2)
cd frontend
npm install
npm run dev
```

### 🌐 Access the Application

| Portal | URL | Credentials |
|--------|-----|-------------|
| 📊 **Dashboard** | http://localhost:3000/dashboard | Public |
| 🏥 **Doctor Station** | http://localhost:3000/doctor | Password: `Doctor@SymptoMap2025` |
| 👨‍💼 **Admin Panel** | http://localhost:3000/admin | Same as Doctor |
| ✅ **Approval Requests** | http://localhost:3000/admin/approvals | Same as Doctor |
| 📚 **API Docs** | http://localhost:8000/docs | Public |

---

## ✨ Features

### 🗺️ Real-Time Outbreak Map
- Interactive MapLibre GL map with outbreak markers
- Aggregated zone visualization by city/region
- Color-coded severity (Mild 🟢 | Moderate 🟡 | Severe 🔴)
- Live location-based risk zones

### 👨‍⚕️ Doctor Station
- Secure authenticated portal for healthcare professionals
- Submit outbreak reports with location, severity, case counts
- Create health alerts with geo-targeting
- View submission history and status

### 👨‍💼 Admin Approval Workflow
- Review pending doctor submissions
- Approve or reject outbreak reports
- Real-time dashboard updates after approval
- Complete audit trail

### 📈 Analytics Dashboard
- SEIR model disease progression charts
- Week-over-week comparison trends
- Risk zone assessment
- System performance metrics
- PDF report generation

### 🔔 Real-Time Updates
- WebSocket live notifications
- Auto-refresh every 60 seconds
- Toast notifications for new outbreaks/alerts

---

## 📁 Project Structure

```
Symptomap_2_python/
├── backend-python/              # FastAPI Backend
│   ├── app/
│   │   ├── api/v1/             # API Endpoints
│   │   │   ├── doctor_station.py    # Doctor submission API
│   │   │   ├── approval.py          # Admin approval API
│   │   │   ├── public_outbreaks.py  # Public outbreak data
│   │   │   └── ...
│   │   ├── core/               # Database & Config
│   │   ├── models/             # SQLAlchemy Models
│   │   └── main.py             # App Entry Point
│   └── requirements.txt
│
├── frontend/                    # React + TypeScript Frontend
│   ├── src/
│   │   ├── pages/              # Page Components
│   │   │   ├── DashboardPage.tsx
│   │   │   ├── DoctorStation.tsx
│   │   │   ├── ApprovalRequestsPage.tsx
│   │   │   └── ...
│   │   ├── components/         # Reusable Components
│   │   │   ├── OutbreakMap.tsx
│   │   │   ├── FilterPanel.tsx
│   │   │   └── ...
│   │   ├── hooks/              # Custom React Hooks
│   │   └── services/           # API Service Layer
│   └── package.json
│
├── generate_pending.py          # Test data generator
├── start.bat                    # Windows startup script
├── start.sh                     # Linux/Mac startup script
└── README.md
```

---

## 🔧 API Endpoints

### Public Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/outbreaks/all` | Get all approved outbreaks |
| GET | `/api/v1/outbreaks/pending-count` | Get pending approval count |
| GET | `/api/v1/stats/dashboard` | Dashboard statistics |

### Authenticated Endpoints (Require JWT Token)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/login` | Doctor login |
| POST | `/api/v1/doctor/outbreak` | Submit outbreak report |
| POST | `/api/v1/doctor/alert` | Create health alert |
| GET | `/api/v1/doctor/submissions` | Get doctor's submissions |
| GET | `/api/v1/admin/pending` | Get pending approvals |
| POST | `/api/v1/admin/approve/{id}` | Approve submission |
| POST | `/api/v1/admin/reject/{id}` | Reject submission |

📚 **Full API Documentation:** http://localhost:8000/docs

---

## 🎯 Workflow

### Doctor Submission Flow
```
Doctor Login → Submit Outbreak → Status: PENDING
                                      ↓
                              Admin Reviews
                                      ↓
                    ┌─────────────────┴─────────────────┐
                    ↓                                   ↓
             APPROVED                              REJECTED
                    ↓                                   ↓
         Appears on Dashboard              Not shown on Dashboard
```

### Testing the Workflow

1. **Generate Test Data:**
   ```bash
   python generate_pending.py
   ```

2. **Login as Doctor:**
   - Go to http://localhost:3000/doctor
   - Password: `Doctor@SymptoMap2025`

3. **Submit an Outbreak:**
   - Navigate to Doctor Station
   - Fill in disease, location, severity
   - Submit

4. **Approve as Admin:**
   - Go to http://localhost:3000/admin/approvals
   - Click "Approve" on pending request

5. **Verify on Dashboard:**
   - Go to http://localhost:3000/dashboard
   - See approved outbreak on map

---

## 🛠️ Development

### Environment Variables

Create `.env` file in `backend-python/`:
```env
# JWT Configuration
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_HOURS=24

# Doctor Password
DOCTOR_PASSWORD=Doctor@SymptoMap2025

# Database
DATABASE_URL=sqlite:///./symptomap.db

# CORS Origins
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

Create `.env` in `frontend/`:
```env
VITE_API_URL=http://localhost:8000/api/v1
```

### Running Tests

```bash
# Backend API Test
cd backend-python
python -m pytest tests/ -v

# Frontend Type Check
cd frontend
npm run build
```

---

## 🐳 Docker Deployment

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## 📊 Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React 18, TypeScript, Vite, TailwindCSS |
| **Backend** | Python 3.10+, FastAPI, SQLAlchemy |
| **Database** | SQLite (dev), PostgreSQL (prod) |
| **Maps** | MapLibre GL JS, OpenStreetMap |
| **Charts** | Recharts |
| **Auth** | JWT (PyJWT) |
| **Real-time** | WebSockets |

---

## 🔐 Security Features

- ✅ JWT-based authentication (24hr expiry)
- ✅ Password-protected doctor access
- ✅ Admin approval workflow for data validation
- ✅ SQL injection prevention (parameterized queries)
- ✅ Input validation and sanitization
- ✅ CORS configuration
- ✅ HTTPS ready for production

---

## 📈 Roadmap

### ✅ Version 1.0 (Current)
- [x] Real-time outbreak map
- [x] Doctor submission portal
- [x] Admin approval workflow
- [x] Dashboard analytics
- [x] SEIR model projections
- [x] PDF report generation

### 🔜 Version 1.1 (Planned)
- [ ] Multi-user authentication
- [ ] Email/SMS notifications
- [ ] Advanced analytics
- [ ] Mobile app (PWA)
- [ ] Multi-language support

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

---

## 👨‍💻 Author

**Rajkaran**  
GitHub: [@Rajkaran-122](https://github.com/Rajkaran-122)

---

<div align="center">

**Made with ❤️ for Public Health Surveillance**

[⭐ Star this repo](https://github.com/Rajkaran-122/Symptomap_2_python) • [🐛 Report Bug](https://github.com/Rajkaran-122/Symptomap_2_python/issues) • [💡 Request Feature](https://github.com/Rajkaran-122/Symptomap_2_python/issues)

**Last Updated:** January 2026 • **Version:** 1.0.0

</div>
