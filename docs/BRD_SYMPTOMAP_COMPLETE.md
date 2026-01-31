# 🏥 SymptoMap: Business Requirements Document (BRD)
## Zero-Cost Production-Ready MVP

**Version**: 1.0  
**Date**: January 29, 2026  
**Status**: Production Ready

---

## 📋 TABLE OF CONTENTS

1. [Executive Summary](#1-executive-summary)
2. [System Architecture](#2-system-architecture)
3. [Security Architecture](#3-security-architecture)
4. [Feature Requirements](#4-feature-requirements)
5. [API Specifications](#5-api-specifications)
6. [Database Schema](#6-database-schema)
7. [Deployment Strategy](#7-deployment-strategy)
8. [Testing & QA](#8-testing--qa)
9. [Monitoring & Maintenance](#9-monitoring--maintenance)
10. [Risk Management](#10-risk-management)
11. [Launch Checklist](#11-launch-checklist)
12. [Future Roadmap](#12-future-roadmap)

---

## 1. EXECUTIVE SUMMARY

### 1.1 Project Overview

SymptoMap is a production-ready, real-time disease outbreak surveillance platform enabling healthcare providers to report, track, and visualize disease outbreaks across geographic regions.

**Primary Users:**
| Role | Description | Access Level |
|------|-------------|--------------|
| Doctors | Submit outbreak reports | Authenticated |
| Admins | Approve/reject submissions | Full access |
| Public | View verified outbreaks | Read-only |

**Key Differentiators:**
- ✅ Zero infrastructure cost (free-tier only)
- ✅ Production-grade security
- ✅ <2 second response times
- ✅ 1,000+ concurrent users
- ✅ 99.5% uptime target

### 1.2 Success Metrics

| Metric | Target | Tool |
|--------|--------|------|
| API Response (p95) | <500ms | Sentry |
| Frontend Load (LCP) | <2.5s | Lighthouse |
| Database Query (p95) | <100ms | Supabase |
| Uptime | >99.5% | Better Stack |
| Error Rate | <0.1% | Sentry |
| Lighthouse Score | >90 | CI/CD |

### 1.3 Budget: ₹0

| Service | Free Tier | If Exceeded |
|---------|-----------|-------------|
| Vercel | Unlimited BW | ₹1,600/mo |
| Render | 750 hrs/mo | ₹560/mo |
| Supabase | 500MB DB | ₹2,000/mo |
| Upstash Redis | 10K req/day | ₹160/mo |
| Resend | 3K emails/mo | ₹1,600/mo |
| Sentry | 5K errors/mo | ₹2,080/mo |
| Better Stack | 10 monitors | ₹1,440/mo |

### 1.4 Timeline (10 Weeks)

```
Week 1    : Infrastructure Setup
Weeks 2-6 : Core Development
Weeks 7-8 : Testing & Security
Week 9    : Launch Preparation
Week 10   : Production Launch
```

---

## 2. SYSTEM ARCHITECTURE

### 2.1 Frontend Stack

**Platform:** Vercel (Free Tier)

| Technology | Purpose | Version |
|------------|---------|---------|
| React | UI Framework | 18.3+ |
| TypeScript | Type Safety | 5.0+ |
| Vite | Build Tool | 5.0+ |
| TailwindCSS | Styling | 3.4+ |
| MapLibre GL | Maps | 4.0+ |
| React Query | Data Fetching | 5.0+ |
| Zustand | State Management | 4.5+ |
| Recharts | Charts | 2.10+ |

**Performance Targets:**
- FCP: <1.5s
- LCP: <2.5s
- TTI: <3.5s
- CLS: <0.1
- Bundle: <200KB gzipped

### 2.2 Backend Stack

**Platform:** Render.com (Free Tier) - 512MB RAM, 0.5 CPU

| Technology | Purpose | Version |
|------------|---------|---------|
| Python | Language | 3.11+ |
| FastAPI | Framework | 0.110+ |
| Uvicorn | ASGI Server | 0.27+ |
| SQLAlchemy | ORM | 2.0+ |
| Pydantic | Validation | 2.5+ |
| PyJWT | Authentication | 2.8+ |
| Bcrypt | Passwords | 4.1+ |

**Architecture:**
```
app/
├── main.py              # Entry point
├── config.py            # Configuration
├── database.py          # DB connection
├── api/v1/
│   ├── auth.py          # Authentication
│   ├── outbreaks.py     # CRUD
│   ├── admin.py         # Approvals
│   └── analytics.py     # Dashboard
├── models/              # SQLAlchemy models
├── schemas/             # Pydantic schemas
├── services/            # Business logic
└── middleware/          # Error handling, CORS
```

### 2.3 Database

**Platform:** Supabase (Free Tier) - PostgreSQL 15 + PostGIS

- 500MB storage
- Unlimited API requests
- Row-level security
- Automatic daily backups

### 2.4 Caching

**Platform:** Upstash Redis (Free Tier)

| Cache Type | TTL | Purpose |
|------------|-----|---------|
| Sessions | 24h | Auth tokens |
| Outbreaks | 5min | List queries |
| Dashboard | 15min | Statistics |
| Hospitals | 1hr | Reference data |

---

## 3. SECURITY ARCHITECTURE

### 3.1 Authentication

**JWT Configuration:**
- Access Token: 24 hours, RS256
- Refresh Token: 7 days, HTTP-only cookie
- Token rotation on each refresh

**Password Policy:**
- Minimum: 12 characters
- Requires: uppercase, lowercase, number, special
- Bcrypt cost factor: 12
- Breach check via HaveIBeenPwned API

**Account Security:**
- 5 failed attempts → 15-minute lockout
- MFA via TOTP (Google Authenticator)
- 10 backup codes per user

### 3.2 Authorization (RBAC)

| Role | Permissions |
|------|-------------|
| Public | View approved outbreaks, view stats |
| Doctor | Submit outbreaks, view own data, export |
| Admin | All + approve/reject, manage users, audit logs |

### 3.3 API Security

**Rate Limits:**
| Endpoint | Limit | Window |
|----------|-------|--------|
| Global | 100 req | 1 min |
| Auth | 5 attempts | 15 min |
| Submit | 10 submissions | 1 hour |
| Admin | 200 req | 1 min |

**Security Headers:**
```
Strict-Transport-Security: max-age=31536000
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Content-Security-Policy: default-src 'self'
```

### 3.4 Data Protection

- TLS 1.3 in transit
- AES-256 at rest (Supabase default)
- PII encrypted at application level
- Automatic data anonymization

### 3.5 Compliance

- GDPR: Consent, export, deletion rights
- HIPAA-like: Audit trails, access controls
- 90-day audit log retention

---

## 4. FEATURE REQUIREMENTS

### 4.1 User Authentication

**Registration Flow:**
1. Email + password input
2. Validation (strength, breach check)
3. Email verification (6-digit OTP, 10-min expiry)
4. Account activation
5. Profile completion

**Login Flow:**
1. Email + password
2. MFA (if enabled)
3. JWT tokens issued
4. Session created

### 4.2 Outbreak Submission

**Form Fields:**
| Field | Type | Validation |
|-------|------|------------|
| Hospital | Autocomplete | Required |
| Location | Map picker | Required |
| Disease | Dropdown | Required |
| Patients | Number | 1-10000 |
| Severity | Select | mild/moderate/severe |
| Date Started | Date | ≤ today |
| Symptoms | Multi-select | Optional |
| Notes | Textarea | Max 1000 chars |

**Workflow:**
```
Doctor Submit → PENDING → Admin Review → APPROVED/REJECTED
                                              ↓
                                        Public Map
```

### 4.3 Outbreak Map

**Features:**
- Interactive MapLibre GL map
- Clustered markers by region
- Color-coded severity (🔴🟡🟢)
- Popup with details
- Filters: disease, severity, date
- User location detection
- Risk zone heatmap

### 4.4 Admin Dashboard

**Capabilities:**
- Pending submissions list
- Approve/reject with reason
- User management
- Audit log viewer
- Report generation (PDF/CSV)

### 4.5 Analytics

**Dashboard Metrics:**
- Total outbreaks (7/30/90 days)
- Total patients affected
- Affected hospitals count
- Severity breakdown (pie chart)
- Trend over time (line chart)
- Geographic distribution

### 4.6 Notifications

**Email (Resend - 3K/month):**
- Welcome email
- OTP verification
- Password reset
- Submission status
- Critical alerts

**In-App:**
- Toast notifications
- Notification bell
- Mark as read

---

## 5. API SPECIFICATIONS

### 5.1 Public Endpoints

```
GET  /api/v1/outbreaks/all         # Approved outbreaks
GET  /api/v1/outbreaks/stats       # Dashboard stats
GET  /api/v1/hospitals             # Hospital list
GET  /api/v1/health                # Health check
```

### 5.2 Authentication

```
POST /api/v1/auth/register         # New user
POST /api/v1/auth/verify-email     # OTP verification
POST /api/v1/auth/login            # Login → JWT
POST /api/v1/auth/refresh          # Refresh token
POST /api/v1/auth/logout           # Logout
POST /api/v1/auth/forgot-password  # Reset request
POST /api/v1/auth/reset-password   # New password
```

### 5.3 Doctor Endpoints

```
POST /api/v1/doctor/outbreaks      # Submit outbreak
GET  /api/v1/doctor/outbreaks      # List own
GET  /api/v1/doctor/outbreaks/:id  # Get details
PUT  /api/v1/doctor/outbreaks/:id  # Update pending
DEL  /api/v1/doctor/outbreaks/:id  # Delete pending
```

### 5.4 Admin Endpoints

```
GET  /api/v1/admin/pending         # Pending list
POST /api/v1/admin/approve/:id     # Approve
POST /api/v1/admin/reject/:id      # Reject
GET  /api/v1/admin/users           # User list
GET  /api/v1/admin/audit-logs      # Audit trail
```

---

## 6. DATABASE SCHEMA

### 6.1 Core Tables

```sql
-- Users
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  full_name VARCHAR(255) NOT NULL,
  role VARCHAR(50) CHECK (role IN ('doctor','admin','public')),
  is_verified BOOLEAN DEFAULT FALSE,
  is_active BOOLEAN DEFAULT TRUE,
  mfa_enabled BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Hospitals
CREATE TABLE hospitals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  city VARCHAR(100),
  state VARCHAR(100),
  location GEOGRAPHY(POINT, 4326),
  created_at TIMESTAMP DEFAULT NOW()
);

-- Outbreaks
CREATE TABLE outbreaks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  hospital_id UUID REFERENCES hospitals(id),
  reported_by UUID REFERENCES users(id),
  disease_type VARCHAR(255) NOT NULL,
  patient_count INTEGER NOT NULL,
  date_started DATE NOT NULL,
  severity VARCHAR(50) CHECK (severity IN ('mild','moderate','severe')),
  status VARCHAR(50) DEFAULT 'pending',
  verified BOOLEAN DEFAULT FALSE,
  symptoms JSONB,
  notes TEXT,
  location GEOGRAPHY(POINT, 4326),
  created_at TIMESTAMP DEFAULT NOW()
);

-- Audit Logs
CREATE TABLE audit_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  action VARCHAR(100) NOT NULL,
  resource_type VARCHAR(50),
  resource_id UUID,
  ip_address INET,
  details JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### 6.2 Indexes

```sql
CREATE INDEX idx_outbreaks_date ON outbreaks(date_reported DESC);
CREATE INDEX idx_outbreaks_status ON outbreaks(status);
CREATE INDEX idx_outbreaks_location ON outbreaks USING GIST(location);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_audit_user_date ON audit_logs(user_id, created_at DESC);
```

---

## 7. DEPLOYMENT STRATEGY

### 7.1 Infrastructure Setup

**Step 1: Database (Supabase)**
1. Create project at supabase.com
2. Run schema migrations
3. Enable Row Level Security
4. Note connection string

**Step 2: Backend (Render)**
1. Connect GitHub repo
2. Create Web Service
3. Set environment variables
4. Deploy from main branch

**Step 3: Frontend (Vercel)**
1. Import GitHub repo
2. Configure build: `npm run build`
3. Set VITE_API_URL
4. Deploy

**Step 4: Email (Resend)**
1. Create account
2. Verify domain
3. Get API key

**Step 5: Monitoring**
1. Better Stack: uptime monitors
2. Sentry: error tracking

### 7.2 Environment Variables

**Backend:**
```bash
DATABASE_URL=postgresql://...
JWT_SECRET_KEY=<random-256-bit>
RESEND_API_KEY=re_xxxxx
REDIS_URL=redis://...
CORS_ORIGINS=https://symptomap.com
```

**Frontend:**
```bash
VITE_API_URL=https://api.symptomap.com/api/v1
VITE_SENTRY_DSN=https://...
```

### 7.3 CI/CD (GitHub Actions)

```yaml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pip install -r requirements.txt
      - run: pytest tests/ --cov
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
```

---

## 8. TESTING & QA

### 8.1 Testing Strategy

| Type | Coverage | Tool |
|------|----------|------|
| Unit | 80% | pytest, vitest |
| Integration | API endpoints | pytest |
| E2E | Critical flows | Playwright |
| Security | OWASP Top 10 | OWASP ZAP |
| Performance | Load testing | Locust |

### 8.2 Test Cases

**Authentication:**
- ✓ Registration with valid data
- ✓ Registration with duplicate email (fail)
- ✓ Login with correct credentials
- ✓ Login with wrong password (fail)
- ✓ Rate limiting after 5 failures

**Outbreak Submission:**
- ✓ Submit valid outbreak
- ✓ Submit without auth (fail)
- ✓ Submit with missing fields (fail)
- ✓ Approve outbreak (admin)
- ✓ Reject with reason

---

## 9. MONITORING & MAINTENANCE

### 9.1 Uptime Monitoring (Better Stack)

| Monitor | Interval | Alert |
|---------|----------|-------|
| Frontend | 1 min | Slack, Email |
| Backend API | 1 min | Slack, Email |
| Database | 5 min | Email |

### 9.2 Error Tracking (Sentry)

- Frontend errors with stack traces
- Backend exceptions
- Performance monitoring
- Release tracking

### 9.3 Backup Strategy

- Database: Auto daily (Supabase)
- Weekly manual export
- Test restore monthly

---

## 10. RISK MANAGEMENT

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Free tier exceeded | Medium | Low | Monitor usage, alerts at 80% |
| Database failure | Low | High | Auto backups, restore tested |
| Security breach | Low | Critical | Audit logs, MFA, rate limits |
| Performance issues | Medium | Medium | Caching, query optimization |

---

## 11. LAUNCH CHECKLIST

### Pre-Launch
- [ ] All tests passing (>80% coverage)
- [ ] Security audit completed
- [ ] Performance benchmarks met
- [ ] Documentation complete
- [ ] Monitoring configured
- [ ] Backup tested
- [ ] SSL valid
- [ ] Domain configured

### Launch Day
- [ ] Deploy to production
- [ ] Smoke tests passed
- [ ] Monitoring active
- [ ] Status page live

### Post-Launch
- [ ] Monitor error rates
- [ ] Check performance
- [ ] Gather user feedback
- [ ] Fix critical bugs

---

## 12. FUTURE ROADMAP

### Phase 2 (Months 4-6)
- [ ] Mobile PWA
- [ ] Advanced analytics
- [ ] Multi-language (Hindi)
- [ ] Public API

### Phase 3 (Months 7-12)
- [ ] AI predictions
- [ ] Government integrations
- [ ] Native mobile apps
- [ ] WhatsApp/Telegram bots

---

## 📎 APPENDIX

### A. Free Tier Limits Summary

| Service | Limit | Monthly |
|---------|-------|---------|
| Vercel | 100GB bandwidth | Free |
| Render | 750 hours | Free |
| Supabase | 500MB + 2GB transfer | Free |
| Resend | 3,000 emails | Free |
| Upstash | 10K requests/day | Free |
| Sentry | 5K errors | Free |

### B. Contact Information

- Security: security@symptomap.com
- Support: support@symptomap.com
- Privacy: privacy@symptomap.com

---

**Document Version:** 1.0  
**Last Updated:** January 29, 2026  
**Next Review:** February 28, 2026
