"""
Notification Service
Handles multi-channel notification delivery (Email, SMS, In-App, Push)
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.broadcast import Broadcast
from app.services.email_service import email_service
from app.services.sms_service import SMSAlertService

sms_service = SMSAlertService()

logger = logging.getLogger(__name__)

class NotificationService:
    """
    Orchestrator for sending notifications across multiple channels
    based on user preferences and broadcast settings.
    """

    @staticmethod
    async def send_broadcast(broadcast: Broadcast, is_resend: bool = False):
        """
        Send a broadcast message to its target audience via configured channels.
        """
        try:
            logger.info(f"Processing broadcast {broadcast.id}: {broadcast.title}")
            
            # 1. Identify Target Audience using SQLAlchemy
            async with AsyncSessionLocal() as session:
                if broadcast.region:
                    # Filter by region
                    stmt = select(User).where(User.region == broadcast.region)
                else:
                    # All users
                    stmt = select(User)
                
                result = await session.execute(stmt)
                target_users = result.scalars().all()
            
            sent_count = 0
            
            for user in target_users:
                # 2. Check User Preferences (Mock logic for now)
                # In real app: user_prefs = await session.execute(select(Preferences).where(...))
                
                # 3. Deliver via Channels
                # Ensure channels is a list (it's JSON/Validation driven usually)
                channels = broadcast.channels or ["in_app"]
                if isinstance(channels, str):
                    import json
                    try:
                        channels = json.loads(channels)
                    except:
                        channels = ["in_app"]

                if "email" in channels and user.email:
                    # Fire and forget email to avoid blocking loop? 
                    # For now await is fine for small batches. Reference implementation used await.
                    await email_service.send_outbreak_alert(
                        to=user.email,
                        zone=broadcast.region or "All Regions",
                        disease=broadcast.title,
                        severity=broadcast.severity,
                        patient_count=0 
                    )
                
                if "sms" in channels and user.phone:
                    alert_data = {
                        "severity": broadcast.severity,
                        "title": broadcast.title,
                        "zone_name": broadcast.region or "All Regions",
                        "risk_level": broadcast.severity,
                        "predicted_cases": 0 # Default for broadcast
                    }
                    await sms_service.send_outbreak_sms([user.phone], alert_data)
                
                sent_count += 1
            
            logger.info(f"Broadcast {broadcast.id} sent to {sent_count} users")
            return sent_count

        except Exception as e:
            logger.error(f"Failed to send broadcast {broadcast.id}: {str(e)}")
            # Don't raise, just log error to avoid crashing the whole task
            return 0

    @staticmethod
    async def schedule_broadcast(broadcast_id: str, send_at: datetime):
        """
        Task to be picked up by scheduler for future broadcasts
        """
        logger.info(f"Broadcast {broadcast_id} scheduled for {send_at}")
        pass

    @staticmethod
    async def send_welcome_notification(user: User):
        """Send welcome notifications to new users"""
        if user.email:
            await email_service.send_welcome_email(user.email, user.full_name or "User")
        
        if user.phone:
            welcome_alert = {
                "severity": "info",
                "title": "Welcome to SymptoMap",
                "zone_name": user.region or "Your Region",
                "risk_level": "low",
                "predicted_cases": "N/A"
            }
            await sms_service.send_outbreak_sms([user.phone], welcome_alert)
