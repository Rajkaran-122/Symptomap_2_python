"""
Chatbot Tools Service
Provides database access tools for the AI Doctor to query real-time health data.
"""

from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from datetime import datetime, timezone

from app.models.outbreak import Outbreak, Hospital, Alert, Prediction

class ChatbotToolsService:
    """
    Service to provide read-only database tools for the chatbot
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def get_active_outbreaks(self, city: Optional[str] = None) -> List[Dict]:
        """
        Get list of active disease outbreaks, optionally filtered by city
        """
        query = select(Outbreak).where(Outbreak.verified == True)
        
        if city:
            # Case-insensitive partial match
            query = query.where(Outbreak.city.ilike(f"%{city}%"))
            
        # Order by verification date descending
        query = query.order_by(Outbreak.verification_date.desc()).limit(10)
        
        result = await self.db.execute(query)
        outbreaks = result.scalars().all()
        
        return [
            {
                "disease": o.disease_type,
                "cases": o.patient_count,
                "severity": o.severity,
                "city": o.city,
                "date": o.verification_date.strftime("%Y-%m-%d") if o.verification_date else "Recent"
            }
            for o in outbreaks
        ]

    async def find_hospitals(self, city: str, required_resource: Optional[str] = None) -> List[Dict]:
        """
        Find hospitals in a city, optionally filtering by resource (ICU, Beds)
        """
        query = select(Hospital).where(Hospital.city.ilike(f"%{city}%"))
        
        if required_resource:
            if "icu" in required_resource.lower():
                query = query.where(Hospital.icu_beds > 0)
            elif "bed" in required_resource.lower():
                query = query.where(Hospital.available_beds > 0)
                
        # Order by available beds desc
        query = query.order_by(Hospital.available_beds.desc()).limit(5)
        
        result = await self.db.execute(query)
        hospitals = result.scalars().all()
        
        return [
            {
                "name": h.name,
                "type": h.hospital_type,
                "address": h.address,
                "phone": h.phone,
                "available_beds": h.available_beds,
                "icu_beds": h.icu_beds
            }
            for h in hospitals
        ]

    async def get_health_alerts(self, city: Optional[str] = None) -> List[Dict]:
        """
        Get active government/system health alerts
        """
        now = datetime.now(timezone.utc)
        query = select(Alert).where(Alert.expires_at > now)
        
        if city:
            # Match specific city or 'All'
            query = query.where(or_(
                Alert.zone_name.ilike(f"%{city}%"),
                Alert.zone_name == "All"
            ))
            
        result = await self.db.execute(query)
        alerts = result.scalars().all()
        
        return [
            {
                "title": a.title,
                "severity": a.severity,
                "message": a.message,
                "issued_at": a.sent_at.strftime("%Y-%m-%d")
            }
            for a in alerts
        ]

    # Schema definitions for OpenAI Tools
    @staticmethod
    def get_tool_definitions() -> List[Dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_active_outbreaks",
                    "description": "Get a list of confirmed disease outbreaks. Use this when users ask about 'flu', 'virus', 'dengue', or 'disease' trends in their area.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city": {
                                "type": "string",
                                "description": "The city to check for outbreaks (e.g., 'Mumbai', 'Delhi')"
                            }
                        },
                        "required": ["city"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "find_hospitals",
                    "description": "Find nearby hospitals. Use this when users need medical care, beds, or ICU availability.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city": {
                                "type": "string",
                                "description": "The city to search in"
                            },
                            "required_resource": {
                                "type": "string",
                                "description": "Optional specific resource needed: 'ICU', 'Beds', 'Ventilator'",
                                "enum": ["ICU", "Beds", "General"]
                            }
                        },
                        "required": ["city"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_health_alerts",
                    "description": "Check for official government health alerts or warnings.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city": {
                                "type": "string",
                                "description": "The city to check"
                            }
                        },
                        "required": ["city"]
                    }
                }
            }
        ]
