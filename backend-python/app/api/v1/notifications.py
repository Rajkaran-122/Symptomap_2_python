"""
Email Notification Subscription API
Handles email subscriptions for outbreak alerts
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime, timezone
import sqlite3

router = APIRouter(prefix="/notifications", tags=["Notifications"])


class SubscriptionRequest(BaseModel):
    email: EmailStr
    notify_outbreaks: bool = True
    notify_approvals: bool = True
    notify_alerts: bool = True
    notify_reports: bool = False


class SubscriptionResponse(BaseModel):
    success: bool
    message: str
    subscription_id: Optional[int] = None


class SubscriptionStatus(BaseModel):
    email: str
    is_subscribed: bool
    notify_outbreaks: bool = False
    notify_approvals: bool = False
    notify_alerts: bool = False
    notify_reports: bool = False
    subscribed_at: Optional[str] = None


def get_db_connection():
    """Get SQLite database connection"""
    from app.core.config import get_sqlite_db_path
    conn = sqlite3.connect(get_sqlite_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def init_subscriptions_table():
    """Initialize the subscriptions table"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS email_subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            notify_outbreaks INTEGER DEFAULT 1,
            notify_approvals INTEGER DEFAULT 1,
            notify_alerts INTEGER DEFAULT 1,
            notify_reports INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            subscribed_at TEXT,
            updated_at TEXT
        )
    ''')
    conn.commit()
    conn.close()


@router.post("/subscribe", response_model=SubscriptionResponse)
async def subscribe_to_notifications(request: SubscriptionRequest):
    """
    Subscribe an email to receive notifications.
    If already subscribed, updates preferences.
    """
    try:
        init_subscriptions_table()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        now = datetime.now(timezone.utc).isoformat()
        
        # Check if email already exists
        cursor.execute('SELECT id FROM email_subscriptions WHERE email = ?', (request.email,))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing subscription
            cursor.execute('''
                UPDATE email_subscriptions 
                SET notify_outbreaks = ?, notify_approvals = ?, notify_alerts = ?, 
                    notify_reports = ?, is_active = 1, updated_at = ?
                WHERE email = ?
            ''', (
                1 if request.notify_outbreaks else 0,
                1 if request.notify_approvals else 0,
                1 if request.notify_alerts else 0,
                1 if request.notify_reports else 0,
                now,
                request.email
            ))
            subscription_id = existing['id']
            message = "Subscription preferences updated"
        else:
            # Create new subscription
            cursor.execute('''
                INSERT INTO email_subscriptions 
                (email, notify_outbreaks, notify_approvals, notify_alerts, notify_reports, subscribed_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                request.email,
                1 if request.notify_outbreaks else 0,
                1 if request.notify_approvals else 0,
                1 if request.notify_alerts else 0,
                1 if request.notify_reports else 0,
                now,
                now
            ))
            subscription_id = cursor.lastrowid
            message = "Successfully subscribed to notifications"
        
        conn.commit()
        conn.close()
        
        return SubscriptionResponse(
            success=True,
            message=message,
            subscription_id=subscription_id
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Subscription failed: {str(e)}")


@router.post("/unsubscribe")
async def unsubscribe_from_notifications(email: str):
    """Unsubscribe an email from all notifications"""
    try:
        init_subscriptions_table()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE email_subscriptions 
            SET is_active = 0, updated_at = ?
            WHERE email = ?
        ''', (datetime.now(timezone.utc).isoformat(), email))
        
        if cursor.rowcount == 0:
            conn.close()
            return {"success": False, "message": "Email not found in subscriptions"}
        
        conn.commit()
        conn.close()
        
        return {"success": True, "message": "Successfully unsubscribed from notifications"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unsubscribe failed: {str(e)}")


@router.get("/status/{email}", response_model=SubscriptionStatus)
async def get_subscription_status(email: str):
    """Check subscription status for an email"""
    try:
        init_subscriptions_table()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM email_subscriptions WHERE email = ?', (email,))
        row = cursor.fetchone()
        conn.close()
        
        if not row or not row['is_active']:
            return SubscriptionStatus(
                email=email,
                is_subscribed=False
            )
        
        return SubscriptionStatus(
            email=email,
            is_subscribed=True,
            notify_outbreaks=bool(row['notify_outbreaks']),
            notify_approvals=bool(row['notify_approvals']),
            notify_alerts=bool(row['notify_alerts']),
            notify_reports=bool(row['notify_reports']),
            subscribed_at=row['subscribed_at']
        )
    
    except Exception as e:
        return SubscriptionStatus(email=email, is_subscribed=False)


@router.get("/subscribers")
async def list_subscribers(active_only: bool = True):
    """List all email subscribers (for admin use)"""
    try:
        init_subscriptions_table()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if active_only:
            cursor.execute('SELECT * FROM email_subscriptions WHERE is_active = 1 ORDER BY subscribed_at DESC')
        else:
            cursor.execute('SELECT * FROM email_subscriptions ORDER BY subscribed_at DESC')
        
        rows = cursor.fetchall()
        conn.close()
        
        subscribers = []
        for row in rows:
            subscribers.append({
                "id": row['id'],
                "email": row['email'],
                "notify_outbreaks": bool(row['notify_outbreaks']),
                "notify_approvals": bool(row['notify_approvals']),
                "notify_alerts": bool(row['notify_alerts']),
                "notify_reports": bool(row['notify_reports']),
                "is_active": bool(row['is_active']),
                "subscribed_at": row['subscribed_at']
            })
        
        return {
            "total": len(subscribers),
            "subscribers": subscribers
        }
    
    except Exception as e:
        return {"total": 0, "subscribers": [], "error": str(e)}
