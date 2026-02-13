# 🚀 SYMPTOMAP USER ROLE & BROADCASTING SYSTEM - IMPLEMENTATION PROMPT

## 📋 QUICK REFERENCE
**Repository:** https://github.com/Rajkaran-122/Symptomap_2_python.git  
**Feature:** Add "User" role with intelligent broadcasting/notification system  
**Priority:** HIGH - Public health engagement critical  
**Timeline:** 12 weeks (Q2 2026)

---

## 🎯 EXECUTIVE SUMMARY

Add a new "USER" role to SymptoMap with **read-only access** to public health data, plus a **dual-mode broadcasting system** (manual + automated AI-powered notifications).

### What Users Get:
- ✅ View public health dashboards (anonymized data only)
- ✅ Receive health broadcasts and alerts
- ✅ Access outbreak maps and statistics
- ✅ Get personalized notifications based on location/preferences
- ❌ NO access to patient records or clinical tools

### What We're Building:
1. **User Role** - Public viewer with limited permissions
2. **OTP Authentication** - Phone-based login (no password)
3. **Manual Broadcasting** - Admin console for health announcements
4. **Automated Alerts** - AI-powered outbreak predictions & notifications
5. **Multi-Channel Delivery** - In-app, Email, SMS, Push notifications
6. **Smart Personalization** - Location-based, disease-specific filtering

---

## 🏗️ SYSTEM ARCHITECTURE

### Current Stack:
- **Backend:** FastAPI (Python 3.11+), PostgreSQL 15+
- **Frontend:** React 18+ with TypeScript
- **Auth:** JWT with RBAC

### New Components:
- **Notification Engine:** Celery + Redis
- **Real-time:** WebSocket for live notifications
- **SMS:** Twilio integration
- **Email:** SendGrid
- **Push:** Firebase Cloud Messaging (FCM)
- **AI/ML:** scikit-learn/TensorFlow for predictions
- **Geospatial:** PostGIS extension

---

## 📂 FILE STRUCTURE

### Backend Files to Create/Modify:

```
backend-python/
├── app/
│   ├── api/v1/
│   │   ├── auth.py                    ✏️ MODIFY - Add user role
│   │   ├── otp_auth.py                ✨ NEW - OTP authentication
│   │   ├── broadcasts.py              ✨ NEW - Broadcast CRUD
│   │   ├── notifications.py           ✨ NEW - Notification management
│   │   └── analytics.py               ✏️ MODIFY - Add public endpoints
│   ├── models/
│   │   ├── broadcast.py               ✨ NEW
│   │   ├── notification_preference.py ✨ NEW
│   │   ├── notification_log.py        ✨ NEW
│   │   └── outbreak_prediction.py     ✨ NEW
│   ├── schemas/
│   │   ├── broadcast.py               ✨ NEW
│   │   ├── notification.py            ✨ NEW
│   │   └── otp.py                     ✨ NEW
│   ├── services/
│   │   ├── otp_service.py             ✨ NEW - OTP generation/validation
│   │   ├── notification_service.py    ✨ NEW - Multi-channel delivery
│   │   ├── sms_service.py             ✨ NEW - Twilio integration
│   │   ├── email_service.py           ✨ NEW - SendGrid integration
│   │   ├── push_service.py            ✨ NEW - FCM integration
│   │   └── prediction_service.py      ✨ NEW - AI outbreak prediction
│   ├── tasks/
│   │   └── notification_tasks.py      ✨ NEW - Celery tasks
│   └── ml/
│       ├── outbreak_predictor.py      ✨ NEW - ML model
│       └── data_processor.py          ✨ NEW - Feature engineering
├── migrations/
│   └── add_user_role_broadcasts.sql   ✨ NEW - Database schema
└── tests/
    ├── test_otp_auth.py               ✨ NEW
    ├── test_broadcasts.py             ✨ NEW
    └── test_notifications.py          ✨ NEW
```

### Frontend Files to Create:

```
frontend/src/
├── components/
│   ├── user/
│   │   ├── UserDashboard.tsx          ✨ NEW
│   │   ├── PublicHealthStats.tsx      ✨ NEW
│   │   ├── OutbreakHeatmap.tsx        ✨ NEW
│   │   ├── BroadcastFeed.tsx          ✨ NEW
│   │   └── NotificationCenter.tsx     ✨ NEW
│   ├── broadcasts/
│   │   ├── BroadcastList.tsx          ✨ NEW
│   │   ├── BroadcastCard.tsx          ✨ NEW
│   │   ├── BroadcastCreator.tsx       ✨ NEW (Admin only)
│   │   └── BroadcastFilter.tsx        ✨ NEW
│   └── auth/
│       ├── OTPLogin.tsx               ✨ NEW
│       └── PhoneInput.tsx             ✨ NEW
├── pages/
│   ├── UserPage.tsx                   ✨ NEW
│   └── BroadcastsPage.tsx             ✨ NEW
├── services/
│   ├── api/
│   │   ├── broadcasts.ts              ✨ NEW
│   │   ├── notifications.ts           ✨ NEW
│   │   └── otp.ts                     ✨ NEW
├── hooks/
│   ├── useNotifications.ts            ✨ NEW
│   ├── useBroadcasts.ts               ✨ NEW
│   └── useWebSocket.ts                ✨ NEW
├── contexts/
│   └── NotificationContext.tsx        ✨ NEW
└── types/
    ├── broadcast.ts                   ✨ NEW
    └── notification.ts                ✨ NEW
```

---

## 🔧 IMPLEMENTATION GUIDE

### PHASE 1: Backend Foundation (Weeks 1-2)

#### Step 1.1: Update User Role

**File:** `backend-python/app/api/v1/auth.py`

```python
from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class UserRegister(BaseModel):
    role: str = Field(
        default="user", 
        pattern=r'^(patient|doctor|user)$'
    )
    phone: Optional[str] = Field(
        None, 
        pattern=r'^\+?[1-9]\d{1,14}$'  # E.164 format
    )
    email: EmailStr
    password: Optional[str] = None  # Optional for OTP users
    region: str  # Required for location-based notifications

# Permission dependency functions
async def get_user_or_above(
    current_user: User = Depends(get_current_user)
) -> User:
    """Allow user, doctor, or admin roles"""
    if current_user.role not in ["user", "doctor", "admin"]:
        raise HTTPException(
            status_code=403, 
            detail="Access denied. Insufficient permissions."
        )
    return current_user

async def get_doctor_or_above(
    current_user: User = Depends(get_current_user)
) -> User:
    """Allow doctor or admin roles only"""
    if current_user.role not in ["doctor", "admin"]:
        raise HTTPException(
            status_code=403, 
            detail="Requires doctor or admin privileges"
        )
    return current_user

async def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """Admin-only access"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403, 
            detail="Admin access required"
        )
    return current_user
```

#### Step 1.2: OTP Authentication System

**File:** `backend-python/app/api/v1/otp_auth.py`

```python
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
import secrets
import hashlib
import redis.asyncio as redis
from app.core.config import settings
from app.models.user import User
from app.services.sms_service import TwilioSMSService
from app.core.security import create_access_token

router = APIRouter(prefix="/api/v1/auth/otp", tags=["otp-auth"])

# Redis connection
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

class OTPRequest(BaseModel):
    phone: str  # E.164 format: +919876543210

class OTPVerify(BaseModel):
    phone: str
    otp: str

def hash_otp(data: str) -> str:
    """Hash OTP for secure storage"""
    return hashlib.sha256(data.encode()).hexdigest()

@router.post("/request")
async def request_otp(
    request: OTPRequest, 
    background_tasks: BackgroundTasks
):
    """Send OTP to phone number"""
    
    # Rate limiting check
    rate_key = f"otp_rate:{request.phone}"
    attempts = await redis_client.get(rate_key)
    if attempts and int(attempts) >= 3:
        raise HTTPException(
            status_code=429, 
            detail="Too many OTP requests. Try again in 1 hour."
        )
    
    # Generate 6-digit OTP
    otp_code = str(secrets.randbelow(1000000)).zfill(6)
    
    # Hash and store in Redis with 5-minute expiry
    otp_hash = hash_otp(f"{request.phone}:{otp_code}")
    await redis_client.setex(
        f"otp:{request.phone}", 
        300,  # 5 minutes
        otp_hash
    )
    
    # Increment rate limit counter (1 hour expiry)
    await redis_client.incr(rate_key)
    await redis_client.expire(rate_key, 3600)
    
    # Send SMS (in background to avoid blocking)
    background_tasks.add_task(
        TwilioSMSService.send_sms,
        to_phone=request.phone,
        message=f"Your SymptoMap verification code is: {otp_code}. Valid for 5 minutes. Do not share this code."
    )
    
    return {
        "message": "OTP sent successfully",
        "expires_in": 300,
        "phone": request.phone[-4:]  # Only show last 4 digits
    }

@router.post("/verify")
async def verify_otp(request: OTPVerify):
    """Verify OTP and auto-register if new user"""
    
    # Retrieve stored OTP hash
    stored_hash = await redis_client.get(f"otp:{request.phone}")
    
    if not stored_hash:
        raise HTTPException(
            status_code=401, 
            detail="OTP expired or not found. Please request a new code."
        )
    
    # Verify OTP
    input_hash = hash_otp(f"{request.phone}:{request.otp}")
    if input_hash != stored_hash:
        raise HTTPException(
            status_code=401, 
            detail="Invalid OTP. Please check and try again."
        )
    
    # Delete OTP (one-time use)
    await redis_client.delete(f"otp:{request.phone}")
    
    # Check if user exists
    user = await User.find_one({"phone": request.phone})
    
    if not user:
        # Auto-register as user role
        user = User(
            phone=request.phone,
            role="user",
            phone_verified=True,
            region="default",  # Update with actual region
            created_at=datetime.utcnow()
        )
        await user.save()
    else:
        # Update verification status
        user.phone_verified = True
        await user.save()
    
    # Generate JWT token
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "phone": user.phone,
            "role": user.role,
            "region": user.region
        }
    }
```

**File:** `backend-python/app/services/sms_service.py`

```python
from twilio.rest import Client
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class TwilioSMSService:
    """Twilio SMS service for OTP and emergency notifications"""
    
    @staticmethod
    async def send_sms(to_phone: str, message: str):
        """Send SMS via Twilio"""
        try:
            client = Client(
                settings.TWILIO_ACCOUNT_SID, 
                settings.TWILIO_AUTH_TOKEN
            )
            
            msg = client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=to_phone
            )
            
            logger.info(f"SMS sent successfully to {to_phone[-4:]}. SID: {msg.sid}")
            return {"status": "sent", "sid": msg.sid}
            
        except Exception as e:
            logger.error(f"SMS failed to {to_phone[-4:]}: {str(e)}")
            raise Exception(f"Failed to send SMS: {str(e)}")
```

#### Step 1.3: Database Migrations

**File:** `backend-python/migrations/001_add_user_role_broadcasts.sql`

```sql
-- ============================================
-- MIGRATION: Add User Role & Broadcasting System
-- Version: 1.0
-- Date: 2026-02-09
-- ============================================

BEGIN;

-- Add 'user' role to users table
ALTER TABLE users 
    ALTER COLUMN role TYPE VARCHAR(20),
    DROP CONSTRAINT IF EXISTS users_role_check,
    ADD CONSTRAINT users_role_check 
        CHECK (role IN ('admin', 'doctor', 'patient', 'user'));

-- Add phone column for OTP authentication
ALTER TABLE users
    ADD COLUMN IF NOT EXISTS phone VARCHAR(20) UNIQUE,
    ADD COLUMN IF NOT EXISTS phone_verified BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS region VARCHAR(100),
    ADD CONSTRAINT check_contact 
        CHECK (email IS NOT NULL OR phone IS NOT NULL);

-- Create index on phone for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone) WHERE phone IS NOT NULL;

-- ============================================
-- BROADCASTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS broadcasts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    severity VARCHAR(20) DEFAULT 'info' 
        CHECK (severity IN ('info', 'warning', 'critical', 'emergency')),
    
    -- Targeting
    region VARCHAR(100),  -- NULL = all regions
    target_audience JSONB DEFAULT '{"type": "all"}'::jsonb,
    
    -- Delivery
    channels JSONB DEFAULT '["in_app"]'::jsonb,
    
    -- Metadata
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    scheduled_for TIMESTAMP,  -- NULL = send immediately
    expires_at TIMESTAMP,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_automated BOOLEAN DEFAULT FALSE,  -- True if AI-generated
    
    -- Additional data
    metadata JSONB,  -- AI prediction details, sources, etc.
    
    CONSTRAINT valid_dates CHECK (expires_at IS NULL OR expires_at > created_at)
);

-- Indexes for broadcasts
CREATE INDEX idx_broadcasts_active ON broadcasts(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_broadcasts_region ON broadcasts(region) WHERE is_active = TRUE;
CREATE INDEX idx_broadcasts_severity ON broadcasts(severity);
CREATE INDEX idx_broadcasts_created_at ON broadcasts(created_at DESC);
CREATE INDEX idx_broadcasts_scheduled ON broadcasts(scheduled_for) WHERE scheduled_for IS NOT NULL;

-- ============================================
-- USER NOTIFICATION PREFERENCES
-- ============================================
CREATE TABLE IF NOT EXISTS user_notification_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Subscription preferences
    region_subscriptions TEXT[] DEFAULT ARRAY[]::TEXT[],
    disease_subscriptions TEXT[] DEFAULT ARRAY[]::TEXT[],
    
    -- Notification settings
    min_severity VARCHAR(20) DEFAULT 'info',
    frequency VARCHAR(20) DEFAULT 'real_time' 
        CHECK (frequency IN ('real_time', 'daily', 'weekly')),
    
    -- Channel preferences
    channels JSONB DEFAULT '{"in_app": true, "email": false, "sms": false, "push": false}'::jsonb,
    
    -- Quiet hours
    quiet_hours_start TIME,
    quiet_hours_end TIME,
    
    -- Status
    enabled BOOLEAN DEFAULT TRUE,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(user_id)
);

CREATE INDEX idx_notif_prefs_user ON user_notification_preferences(user_id);

-- ============================================
-- NOTIFICATION LOGS (Delivery Tracking)
-- ============================================
CREATE TABLE IF NOT EXISTS notification_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    broadcast_id UUID REFERENCES broadcasts(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Delivery details
    channel VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'sent' 
        CHECK (status IN ('sent', 'delivered', 'failed', 'clicked', 'dismissed')),
    
    -- Timestamps
    sent_at TIMESTAMP DEFAULT NOW(),
    delivered_at TIMESTAMP,
    clicked_at TIMESTAMP,
    dismissed_at TIMESTAMP,
    
    -- Error handling
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    
    -- Additional data
    metadata JSONB
);

-- Indexes for notification logs
CREATE INDEX idx_notif_logs_broadcast ON notification_logs(broadcast_id);
CREATE INDEX idx_notif_logs_user ON notification_logs(user_id);
CREATE INDEX idx_notif_logs_status ON notification_logs(status);
CREATE INDEX idx_notif_logs_sent_at ON notification_logs(sent_at DESC);

-- ============================================
-- OUTBREAK PREDICTIONS (AI/ML)
-- ============================================
CREATE TABLE IF NOT EXISTS outbreak_predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Prediction details
    disease_type VARCHAR(100) NOT NULL,
    region VARCHAR(100) NOT NULL,
    prediction_date DATE NOT NULL,
    predicted_cases INTEGER,
    
    -- Confidence and risk
    confidence_score DECIMAL(5,2) CHECK (confidence_score >= 0 AND confidence_score <= 100),
    risk_level VARCHAR(20) CHECK (risk_level IN ('low', 'medium', 'high', 'critical')),
    
    -- Model details
    factors JSONB,  -- Contributing factors
    model_version VARCHAR(50),
    
    -- Status
    created_at TIMESTAMP DEFAULT NOW(),
    broadcast_id UUID REFERENCES broadcasts(id),  -- If alert was sent
    admin_approved BOOLEAN DEFAULT FALSE,
    
    UNIQUE(disease_type, region, prediction_date)
);

-- Indexes for predictions
CREATE INDEX idx_predictions_region ON outbreak_predictions(region);
CREATE INDEX idx_predictions_date ON outbreak_predictions(prediction_date DESC);
CREATE INDEX idx_predictions_risk ON outbreak_predictions(risk_level);
CREATE INDEX idx_predictions_unapproved ON outbreak_predictions(admin_approved) 
    WHERE admin_approved = FALSE;

-- ============================================
-- TRIGGERS
-- ============================================

-- Update updated_at timestamp on broadcasts
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_broadcasts_updated_at
    BEFORE UPDATE ON broadcasts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_notif_prefs_updated_at
    BEFORE UPDATE ON user_notification_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- INITIAL DATA
-- ============================================

-- Create default notification preferences for existing users
INSERT INTO user_notification_preferences (user_id, region_subscriptions, enabled)
SELECT 
    id, 
    ARRAY[COALESCE(region, 'default')]::TEXT[],
    TRUE
FROM users
WHERE role IN ('user', 'patient')
ON CONFLICT (user_id) DO NOTHING;

COMMIT;
```

#### Step 1.4: Broadcast API Endpoints

**File:** `backend-python/app/api/v1/broadcasts.py`

```python
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from typing import List, Optional
from datetime import datetime
from app.models.broadcast import Broadcast
from app.schemas.broadcast import BroadcastCreate, BroadcastUpdate, BroadcastResponse
from app.api.v1.auth import get_current_user, require_admin, get_user_or_above
from app.models.user import User
from app.services.notification_service import NotificationService
from uuid import UUID

router = APIRouter(prefix="/api/v1/broadcasts", tags=["broadcasts"])

@router.post("/", status_code=201, response_model=BroadcastResponse)
async def create_broadcast(
    broadcast: BroadcastCreate,
    background_tasks: BackgroundTasks,
    admin: User = Depends(require_admin)
):
    """
    Create and send broadcast (Admin only)
    
    - **title**: Broadcast title (max 200 chars)
    - **content**: Full message content
    - **severity**: info, warning, critical, or emergency
    - **region**: Target region (null = all regions)
    - **channels**: Delivery channels array
    - **scheduled_for**: Optional future delivery time
    - **expires_at**: Optional expiry date
    """
    
    new_broadcast = Broadcast(
        **broadcast.dict(),
        created_by=admin.id,
        is_automated=False
    )
    await new_broadcast.save()
    
    # Send notifications based on schedule
    if broadcast.scheduled_for and broadcast.scheduled_for > datetime.utcnow():
        # Schedule for later
        background_tasks.add_task(
            NotificationService.schedule_broadcast,
            broadcast_id=str(new_broadcast.id),
            send_at=broadcast.scheduled_for
        )
    else:
        # Send immediately
        background_tasks.add_task(
            NotificationService.send_broadcast,
            broadcast=new_broadcast
        )
    
    return new_broadcast

@router.get("/", response_model=List[BroadcastResponse])
async def list_broadcasts(
    region: Optional[str] = Query(None, description="Filter by region"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    active_only: bool = Query(True, description="Show only active broadcasts"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: User = Depends(get_user_or_above)
):
    """
    List broadcasts (accessible to all authenticated users)
    
    Returns paginated list of broadcasts filtered by parameters.
    Users only see broadcasts relevant to their region (unless admin).
    """
    
    filters = {}
    
    if active_only:
        filters["is_active"] = True
        # Also filter out expired broadcasts
        filters["$or"] = [
            {"expires_at": None},
            {"expires_at": {"$gt": datetime.utcnow()}}
        ]
    
    if region:
        filters["region"] = region
    elif user.role == "user" and user.region:
        # Non-admin users only see their region + global broadcasts
        filters["$or"] = [
            {"region": user.region},
            {"region": None}
        ]
    
    if severity:
        filters["severity"] = severity
    
    broadcasts = await Broadcast.find(filters) \
        .sort("-created_at") \
        .skip(offset) \
        .limit(limit) \
        .to_list()
    
    return broadcasts

@router.get("/{broadcast_id}", response_model=BroadcastResponse)
async def get_broadcast(
    broadcast_id: UUID,
    user: User = Depends(get_user_or_above)
):
    """Get single broadcast details"""
    
    broadcast = await Broadcast.find_one({"id": broadcast_id})
    
    if not broadcast:
        raise HTTPException(status_code=404, detail="Broadcast not found")
    
    # Check if user has access to this broadcast
    if user.role != "admin":
        if broadcast.region and broadcast.region != user.region:
            raise HTTPException(
                status_code=403, 
                detail="You don't have access to this broadcast"
            )
    
    return broadcast

@router.put("/{broadcast_id}", response_model=BroadcastResponse)
async def update_broadcast(
    broadcast_id: UUID,
    updates: BroadcastUpdate,
    admin: User = Depends(require_admin)
):
    """Update broadcast (Admin only)"""
    
    broadcast = await Broadcast.find_one({"id": broadcast_id})
    
    if not broadcast:
        raise HTTPException(status_code=404, detail="Broadcast not found")
    
    # Update fields
    update_data = updates.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(broadcast, field, value)
    
    await broadcast.save()
    
    return broadcast

@router.delete("/{broadcast_id}")
async def delete_broadcast(
    broadcast_id: UUID,
    admin: User = Depends(require_admin)
):
    """
    Soft delete broadcast (Admin only)
    
    Sets is_active to False instead of deleting from database.
    """
    
    broadcast = await Broadcast.find_one({"id": broadcast_id})
    
    if not broadcast:
        raise HTTPException(status_code=404, detail="Broadcast not found")
    
    broadcast.is_active = False
    await broadcast.save()
    
    return {
        "message": "Broadcast archived successfully",
        "broadcast_id": str(broadcast_id)
    }

@router.post("/{broadcast_id}/resend")
async def resend_broadcast(
    broadcast_id: UUID,
    background_tasks: BackgroundTasks,
    admin: User = Depends(require_admin)
):
    """
    Resend an existing broadcast (Admin only)
    
    Useful for critical alerts that need to be sent again.
    """
    
    broadcast = await Broadcast.find_one({"id": broadcast_id})
    
    if not broadcast:
        raise HTTPException(status_code=404, detail="Broadcast not found")
    
    # Send notification in background
    background_tasks.add_task(
        NotificationService.send_broadcast,
        broadcast=broadcast,
        is_resend=True
    )
    
    return {
        "message": "Broadcast queued for resending",
        "broadcast_id": str(broadcast_id)
    }
```

---

### PHASE 2: Frontend Implementation (Weeks 3-4)

#### Step 2.1: User Dashboard

**File:** `frontend/src/components/user/UserDashboard.tsx`

```typescript
import React, { useEffect, useState } from 'react';
import { PublicHealthStats } from './PublicHealthStats';
import { OutbreakHeatmap } from './OutbreakHeatmap';
import { BroadcastFeed } from './BroadcastFeed';
import { NotificationCenter } from './NotificationCenter';
import { Alert, AlertCircle } from 'lucide-react';

interface DashboardData {
  stats: {
    totalCases: number;
    activeCases: number;
    recoveries: number;
    trend: 'increasing' | 'decreasing' | 'stable';
  };
  alerts: Alert[];
  userRegion: string;
}

export const UserDashboard: React.FC = () => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/analytics/public', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch dashboard data');
      }

      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md">
          <div className="flex items-center space-x-3">
            <AlertCircle className="text-red-600" size={24} />
            <div>
              <h3 className="text-red-800 font-semibold">Error Loading Dashboard</h3>
              <p className="text-red-600 text-sm mt-1">{error}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Community Health Dashboard
              </h1>
              <p className="text-sm text-gray-600 mt-1">
                {data?.userRegion || 'All Regions'}
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                <span className="w-2 h-2 bg-blue-600 rounded-full mr-2"></span>
                View Only
              </span>
              <NotificationCenter />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column: Stats & Map */}
          <div className="lg:col-span-2 space-y-6">
            {/* Key Metrics */}
            <PublicHealthStats data={data?.stats} />

            {/* Heatmap */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Outbreak Heatmap
              </h2>
              <OutbreakHeatmap region={data?.userRegion} />
            </div>

            {/* Trends Chart */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                7-Day Trend Analysis
              </h2>
              {/* Add chart component here */}
            </div>
          </div>

          {/* Right Column: Broadcasts & Alerts */}
          <div className="space-y-6">
            <BroadcastFeed limit={10} />
            
            {/* Quick Actions */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Quick Actions
              </h3>
              <div className="space-y-3">
                <button className="w-full text-left px-4 py-3 bg-blue-50 hover:bg-blue-100 rounded-lg transition">
                  <div className="flex items-center space-x-3">
                    <AlertCircle className="text-blue-600" size={20} />
                    <span className="text-blue-900 font-medium">View Alerts</span>
                  </div>
                </button>
                {/* Add more quick actions */}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};
```

#### Step 2.2: OTP Login Component

**File:** `frontend/src/components/auth/OTPLogin.tsx`

```typescript
import React, { useState } from 'react';
import { PhoneInput } from './PhoneInput';
import { otpService } from '@/services/otp';
import { useNavigate } from 'react-router-dom';
import { Loader2 } from 'lucide-react';

export const OTPLogin: React.FC = () => {
  const [step, setStep] = useState<'phone' | 'otp'>('phone');
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [countdown, setCountdown] = useState(0);
  const navigate = useNavigate();

  const handleRequestOTP = async () => {
    setError(null);
    setLoading(true);

    try {
      await otpService.requestOTP(phone);
      setStep('otp');
      setCountdown(300); // 5 minutes

      // Start countdown
      const timer = setInterval(() => {
        setCountdown(prev => {
          if (prev <= 1) {
            clearInterval(timer);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send OTP');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOTP = async () => {
    setError(null);
    setLoading(true);

    try {
      const result = await otpService.verifyOTP(phone, otp);
      
      // Store token
      localStorage.setItem('token', result.access_token);
      localStorage.setItem('user', JSON.stringify(result.user));
      
      // Navigate to dashboard
      navigate('/user/dashboard');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Invalid OTP');
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-xl p-8">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-900">Welcome to SymptoMap</h2>
          <p className="text-gray-600 mt-2">
            {step === 'phone' 
              ? 'Enter your phone number to get started' 
              : 'Enter the verification code sent to your phone'}
          </p>
        </div>

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800 text-sm">{error}</p>
          </div>
        )}

        {step === 'phone' ? (
          <>
            <PhoneInput
              value={phone}
              onChange={setPhone}
              disabled={loading}
            />
            
            <button
              onClick={handleRequestOTP}
              disabled={loading || !phone}
              className="w-full mt-6 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white font-semibold py-3 px-4 rounded-lg transition flex items-center justify-center"
            >
              {loading ? (
                <>
                  <Loader2 className="animate-spin mr-2" size={20} />
                  Sending OTP...
                </>
              ) : (
                'Send OTP'
              )}
            </button>
          </>
        ) : (
          <>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Verification Code
              </label>
              <input
                type="text"
                value={otp}
                onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                placeholder="000000"
                maxLength={6}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-center text-2xl tracking-widest"
                disabled={loading}
              />
            </div>

            {countdown > 0 && (
              <p className="text-sm text-gray-600 text-center mb-4">
                Code expires in {formatTime(countdown)}
              </p>
            )}

            <button
              onClick={handleVerifyOTP}
              disabled={loading || otp.length !== 6}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white font-semibold py-3 px-4 rounded-lg transition flex items-center justify-center"
            >
              {loading ? (
                <>
                  <Loader2 className="animate-spin mr-2" size={20} />
                  Verifying...
                </>
              ) : (
                'Verify & Login'
              )}
            </button>

            <button
              onClick={() => {
                setStep('phone');
                setOtp('');
                setError(null);
              }}
              className="w-full mt-3 text-blue-600 hover:text-blue-700 font-medium py-2"
              disabled={loading}
            >
              Change Phone Number
            </button>

            {countdown === 0 && (
              <button
                onClick={handleRequestOTP}
                className="w-full mt-2 text-gray-600 hover:text-gray-700 text-sm py-2"
                disabled={loading}
              >
                Resend OTP
              </button>
            )}
          </>
        )}

        <div className="mt-8 pt-6 border-t border-gray-200">
          <p className="text-xs text-gray-500 text-center">
            By continuing, you agree to our Terms of Service and Privacy Policy.
            Your data is protected and will only be used for health monitoring purposes.
          </p>
        </div>
      </div>
    </div>
  );
};
```

---

### PHASE 3: Notification System (Weeks 5-6)

#### Step 3.1: Notification Service

**File:** `backend-python/app/services/notification_service.py`

```python
from app.models.broadcast import Broadcast
from app.models.user import User
from app.models.notification_preference import NotificationPreference
from app.models.notification_log import NotificationLog
from app.services.email_service import EmailService
from app.services.sms_service import TwilioSMSService
from app.services.push_service import FCMService
from datetime import datetime, time
from typing import List
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    """Multi-channel notification delivery service"""
    
    @classmethod
    async def send_broadcast(
        cls, 
        broadcast: Broadcast,
        is_resend: bool = False
    ):
        """
        Send broadcast to all eligible users across multiple channels
        """
        
        # Get eligible users
        users = await cls._get_eligible_users(broadcast)
        
        logger.info(
            f"Sending broadcast '{broadcast.title}' to {len(users)} users. "
            f"Severity: {broadcast.severity}, Region: {broadcast.region or 'all'}"
        )
        
        # Send via each channel
        for user in users:
            await cls._send_to_user(user, broadcast)
        
        return {
            "broadcast_id": str(broadcast.id),
            "recipients": len(users),
            "channels": broadcast.channels
        }
    
    @classmethod
    async def _get_eligible_users(cls, broadcast: Broadcast) -> List[User]:
        """
        Get list of users who should receive this broadcast
        based on region, preferences, and quiet hours
        """
        
        filters = {"role": {"$in": ["user", "patient"]}}
        
        # Region filtering
        if broadcast.region:
            filters["region"] = broadcast.region
        
        users = await User.find(filters).to_list()
        
        # Filter by preferences
        eligible_users = []
        current_time = datetime.utcnow().time()
        
        for user in users:
            prefs = await NotificationPreference.find_one({"user_id": user.id})
            
            if not prefs or not prefs.enabled:
                continue
            
            # Check severity threshold
            severity_order = ['info', 'warning', 'critical', 'emergency']
            if severity_order.index(broadcast.severity) < severity_order.index(prefs.min_severity):
                # Skip if broadcast severity is below user's threshold
                continue
            
            # Check quiet hours (except for emergency)
            if broadcast.severity != 'emergency':
                if prefs.quiet_hours_start and prefs.quiet_hours_end:
                    if cls._is_quiet_hours(
                        current_time, 
                        prefs.quiet_hours_start, 
                        prefs.quiet_hours_end
                    ):
                        # Queue for later instead of sending now
                        continue
            
            eligible_users.append(user)
        
        return eligible_users
    
    @classmethod
    def _is_quiet_hours(cls, current: time, start: time, end: time) -> bool:
        """Check if current time is within quiet hours"""
        if start < end:
            return start <= current <= end
        else:  # Quiet hours span midnight
            return current >= start or current <= end
    
    @classmethod
    async def _send_to_user(cls, user: User, broadcast: Broadcast):
        """Send notification to a single user via their preferred channels"""
        
        prefs = await NotificationPreference.find_one({"user_id": user.id})
        
        if not prefs:
            # Default to in-app only
            await cls._send_in_app(user, broadcast)
            return
        
        # Send via each enabled channel
        for channel, enabled in prefs.channels.items():
            if not enabled:
                continue
            
            try:
                if channel == 'in_app':
                    await cls._send_in_app(user, broadcast)
                elif channel == 'email' and user.email:
                    await cls._send_email(user, broadcast)
                elif channel == 'sms' and user.phone:
                    # Only send SMS for critical/emergency
                    if broadcast.severity in ['critical', 'emergency']:
                        await cls._send_sms(user, broadcast)
                elif channel == 'push':
                    await cls._send_push(user, broadcast)
                
            except Exception as e:
                logger.error(
                    f"Failed to send {channel} notification to user {user.id}: {str(e)}"
                )
                # Log failure
                await NotificationLog.create({
                    "broadcast_id": broadcast.id,
                    "user_id": user.id,
                    "channel": channel,
                    "status": "failed",
                    "error_message": str(e)
                })
    
    @classmethod
    async def _send_in_app(cls, user: User, broadcast: Broadcast):
        """Send in-app notification (WebSocket)"""
        # This will be handled by WebSocket server
        await NotificationLog.create({
            "broadcast_id": broadcast.id,
            "user_id": user.id,
            "channel": "in_app",
            "status": "sent"
        })
    
    @classmethod
    async def _send_email(cls, user: User, broadcast: Broadcast):
        """Send email notification"""
        await EmailService.send_broadcast_email(
            to_email=user.email,
            subject=f"[{broadcast.severity.upper()}] {broadcast.title}",
            content=broadcast.content,
            severity=broadcast.severity
        )
        
        await NotificationLog.create({
            "broadcast_id": broadcast.id,
            "user_id": user.id,
            "channel": "email",
            "status": "sent"
        })
    
    @classmethod
    async def _send_sms(cls, user: User, broadcast: Broadcast):
        """Send SMS notification"""
        # Truncate for SMS
        sms_content = f"[SYMPTOMAP {broadcast.severity.upper()}] {broadcast.title[:100]}"
        
        await TwilioSMSService.send_sms(
            to_phone=user.phone,
            message=sms_content
        )
        
        await NotificationLog.create({
            "broadcast_id": broadcast.id,
            "user_id": user.id,
            "channel": "sms",
            "status": "sent"
        })
    
    @classmethod
    async def _send_push(cls, user: User, broadcast: Broadcast):
        """Send push notification"""
        await FCMService.send_notification(
            user_id=str(user.id),
            title=broadcast.title,
            body=broadcast.content[:200],  # Truncate
            data={
                "broadcast_id": str(broadcast.id),
                "severity": broadcast.severity,
                "action": "view_broadcast"
            }
        )
        
        await NotificationLog.create({
            "broadcast_id": broadcast.id,
            "user_id": user.id,
            "channel": "push",
            "status": "sent"
        })
```

---

## 🧪 TESTING CHECKLIST

### Unit Tests (90%+ Coverage Target)

```python
# test_otp_auth.py
async def test_request_otp_valid_phone():
    """Test OTP request with valid phone number"""
    response = await client.post("/api/v1/auth/otp/request", json={
        "phone": "+919876543210"
    })
    assert response.status_code == 200
    assert "expires_in" in response.json()

async def test_verify_otp_correct():
    """Test OTP verification with correct code"""
    # Request OTP first
    # Then verify
    response = await client.post("/api/v1/auth/otp/verify", json={
        "phone": "+919876543210",
        "otp": "123456"  # Mock OTP
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

async def test_rate_limiting():
    """Test OTP rate limiting (max 3 per hour)"""
    for i in range(4):
        response = await client.post("/api/v1/auth/otp/request", json={
            "phone": "+919876543210"
        })
        if i < 3:
            assert response.status_code == 200
        else:
            assert response.status_code == 429  # Too many requests
```

### Integration Tests

```python
# test_broadcast_flow.py
async def test_end_to_end_broadcast_flow():
    """Test complete broadcast creation and delivery"""
    
    # 1. Admin creates broadcast
    broadcast = await create_broadcast({
        "title": "Test Alert",
        "content": "This is a test",
        "severity": "warning",
        "region": "Mumbai",
        "channels": ["in_app", "email"]
    })
    
    # 2. Verify broadcast created
    assert broadcast.id is not None
    
    # 3. Check notifications sent
    await asyncio.sleep(2)  # Wait for async delivery
    logs = await NotificationLog.find({"broadcast_id": broadcast.id}).to_list()
    assert len(logs) > 0
    
    # 4. Verify user can retrieve broadcast
    response = await client.get(
        f"/api/v1/broadcasts/{broadcast.id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
```

### Load Tests (Locust)

```python
# locustfile.py
from locust import HttpUser, task, between

class SymptoMapUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Login
        response = self.client.post("/api/v1/auth/otp/verify", json={
            "phone": "+919876543210",
            "otp": "123456"
        })
        self.token = response.json()["access_token"]
    
    @task(3)
    def view_dashboard(self):
        self.client.get(
            "/api/v1/analytics/public",
            headers={"Authorization": f"Bearer {self.token}"}
        )
    
    @task(2)
    def list_broadcasts(self):
        self.client.get(
            "/api/v1/broadcasts",
            headers={"Authorization": f"Bearer {self.token}"}
        )
    
    @task(1)
    def view_broadcast_detail(self):
        self.client.get(
            "/api/v1/broadcasts/some-uuid",
            headers={"Authorization": f"Bearer {self.token}"}
        )
```

**Run Load Test:**
```bash
locust -f locustfile.py --host=http://localhost:8000 --users=1000 --spawn-rate=50
```

---

## 🚀 DEPLOYMENT CHECKLIST

### Environment Variables

```bash
# .env.production
DATABASE_URL=postgresql://user:pass@host:5432/symptomap
REDIS_URL=redis://localhost:6379/0

# Twilio
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# SendGrid
SENDGRID_API_KEY=your_sendgrid_key
SENDGRID_FROM_EMAIL=notifications@symptomap.com

# Firebase
FIREBASE_PROJECT_ID=symptomap-prod
FIREBASE_PRIVATE_KEY=your_private_key
FIREBASE_CLIENT_EMAIL=firebase-adminsdk@symptomap.iam.gserviceaccount.com

# JWT
SECRET_KEY=your_secret_key_change_this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# AI/ML
ML_MODEL_PATH=/app/models/outbreak_predictor_v1.pkl
PREDICTION_CONFIDENCE_THRESHOLD=85
```

### Pre-Deployment Steps

1. **Run all tests**
```bash
pytest --cov=app --cov-report=html
```

2. **Database migrations**
```bash
alembic upgrade head
```

3. **Build Docker images**
```bash
docker-compose -f docker-compose.prod.yml build
```

4. **Security scan**
```bash
bandit -r backend-python/app
safety check
```

5. **Load testing**
```bash
locust -f tests/load/locustfile.py --headless --users=10000 --spawn-rate=100 --run-time=5m
```

### Monitoring Setup

```python
# Add to main.py
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

# Prometheus metrics
Instrumentator().instrument(app).expose(app)

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0"
    }
```

---

## 📊 SUCCESS METRICS

### Track These KPIs:

1. **User Adoption**
   - Target: 10,000+ registered users in 3 months
   - Metric: `SELECT COUNT(*) FROM users WHERE role='user' AND created_at > NOW() - INTERVAL '3 months'`

2. **Notification Accuracy**
   - Target: 95%+ relevant delivery rate
   - Metric: `SELECT AVG(CASE WHEN status='clicked' THEN 1 ELSE 0 END) FROM notification_logs`

3. **Response Time**
   - Target: < 5 minutes from outbreak detection to notification
   - Metric: Monitor `outbreak_predictions.created_at` to `broadcasts.created_at` delta

4. **Engagement**
   - Target: 40%+ click-through rate
   - Metric: `SELECT COUNT(*) WHERE clicked_at IS NOT NULL / COUNT(*) FROM notification_logs`

5. **System Performance**
   - Target: 99.9% uptime
   - Metric: Use Prometheus/Grafana for real-time monitoring

---

## 🎯 FINAL CHECKLIST

Before considering this feature complete:

- [ ] All 4 roles work correctly (admin, doctor, patient, user)
- [ ] OTP authentication functional with rate limiting
- [ ] Manual broadcasts can be created by admins
- [ ] Automated alerts trigger based on outbreak spikes
- [ ] Multi-channel delivery works (in-app, email, SMS, push)
- [ ] Users can set notification preferences
- [ ] Quiet hours respected (except emergencies)
- [ ] AI prediction model achieves 85%+ accuracy
- [ ] Load testing passes (10,000 concurrent notifications)
- [ ] Security audit completed
- [ ] Documentation written
- [ ] All tests passing (90%+ coverage)
- [ ] Monitoring dashboards configured
- [ ] User training materials prepared

---

## 📞 SUPPORT & QUESTIONS

For implementation questions or issues:

1. **Backend Questions:** Contact backend team lead
2. **Frontend Questions:** Contact frontend team lead
3. **AI/ML Questions:** Contact ML engineer
4. **DevOps/Deployment:** Contact DevOps team

---

**Ready to start? Begin with Phase 1, Step 1.1! 🚀**