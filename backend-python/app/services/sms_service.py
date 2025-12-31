"""
SMS Alert Service using Twilio
"""

from twilio.rest import Client
from typing import List, Dict
from app.core.config import settings


class SMSAlertService:
    """Service for sending SMS alerts via Twilio"""
    
    def __init__(self):
        self.client = None
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            self.client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )
        self.from_number = settings.TWILIO_PHONE_NUMBER
    
    async def send_outbreak_sms(
        self,
        phone_numbers: List[str],
        alert_data: Dict
    ) -> Dict:
        """
        Send outbreak alert via SMS
        
        Args:
            phone_numbers: List of recipient phone numbers
            alert_data: Alert information
        
        Returns:
            Dict with delivery status
        """
        
        if not self.client:
            return {
                "status": "skipped",
                "reason": "Twilio not configured. Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER"
            }
        
        message_body = self._format_sms_message(alert_data)
        
        results = []
        for phone in phone_numbers:
            try:
                message = self.client.messages.create(
                    body=message_body,
                    from_=self.from_number,
                    to=phone
                )
                results.append({
                    "phone": phone,
                    "status": "sent",
                    "sid": message.sid
                })
            except Exception as e:
                results.append({
                    "phone": phone,
                    "status": "failed",
                    "error": str(e)
                })
        
        successful = len([r for r in results if r["status"] == "sent"])
        
        return {
            "status": "completed",
            "total": len(phone_numbers),
            "successful": successful,
            "failed": len(phone_numbers) - successful,
            "details": results
        }
    
    def _format_sms_message(self, alert_data: Dict) -> str:
        """Format alert data into SMS message (max 160 chars)"""
        
        severity_emoji = {
            "critical": "🚨",
            "warning": "⚠️",
            "info": "ℹ️"
        }
        
        emoji = severity_emoji.get(alert_data.get("severity", "info"), "ℹ️")
        
        # Keep under 160 characters for standard SMS
        message = f"{emoji} HEALTH ALERT\n"
        message += f"{alert_data.get('title', 'Disease Outbreak')}\n"
        message += f"Zone: {alert_data.get('zone_name', 'N/A')}\n"
        message += f"Risk: {alert_data.get('risk_level', 'N/A').upper()}\n"
        message += f"Cases: {alert_data.get('predicted_cases', 'N/A')}\n"
        message += "Check your email for details."
        
        return message[:160]  # Truncate if needed
