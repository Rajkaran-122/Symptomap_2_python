"""
Email Service using Resend API (Free Tier: 3,000 emails/month)
Production-ready email service for SymptoMap
"""

import os
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

# Try to import resend
try:
    import resend
    RESEND_AVAILABLE = True
except ImportError:
    RESEND_AVAILABLE = False


class EmailService:
    """Production email service using Resend"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("RESEND_API_KEY", "")
        self.from_email = os.getenv("EMAIL_FROM", "noreply@symptomap.com")
        self.from_name = os.getenv("EMAIL_FROM_NAME", "SymptoMap")
        
        if RESEND_AVAILABLE and self.api_key:
            resend.api_key = self.api_key
            self.enabled = True
        else:
            self.enabled = False
            print("⚠️ Email service disabled: Resend not configured")
    
    async def send_email(
        self,
        to: str | List[str],
        subject: str,
        html: str,
        text: Optional[str] = None,
        reply_to: Optional[str] = None,
        tags: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """Send an email using Resend API"""
        
        if not self.enabled:
            print(f"📧 [MOCK] Email to {to}: {subject}")
            return {"id": "mock", "status": "mock_sent"}
        
        try:
            params = {
                "from": f"{self.from_name} <{self.from_email}>",
                "to": [to] if isinstance(to, str) else to,
                "subject": subject,
                "html": html,
            }
            
            if text:
                params["text"] = text
            if reply_to:
                params["reply_to"] = reply_to
            if tags:
                params["tags"] = tags
            
            response = resend.Emails.send(params)
            return {"id": response.get("id"), "status": "sent"}
            
        except Exception as e:
            print(f"❌ Email error: {e}")
            return {"id": None, "status": "failed", "error": str(e)}
    
    # ==========================================================================
    # EMAIL TEMPLATES
    # ==========================================================================
    
    async def send_welcome_email(self, to: str, name: str) -> Dict[str, Any]:
        """Send welcome email to new user"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .header h1 {{ color: white; margin: 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏥 Welcome to SymptoMap</h1>
                </div>
                <div class="content">
                    <h2>Hello {name}!</h2>
                    <p>Welcome to SymptoMap, India's real-time disease surveillance platform.</p>
                    <p>With SymptoMap, you can:</p>
                    <ul>
                        <li>📊 Track disease outbreaks in real-time</li>
                        <li>🗺️ View interactive outbreak maps</li>
                        <li>🔔 Receive instant alerts for your region</li>
                        <li>📈 Access predictive analytics</li>
                    </ul>
                    <p>Get started by logging in to your dashboard:</p>
                    <a href="https://symptomap.com/login" class="button">Go to Dashboard</a>
                </div>
                <div class="footer">
                    <p>© 2026 SymptoMap. All rights reserved.</p>
                    <p>This email was sent to {to}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(
            to=to,
            subject="Welcome to SymptoMap 🏥",
            html=html,
            tags=[{"name": "category", "value": "welcome"}]
        )
    
    async def send_verification_email(self, to: str, name: str, otp: str) -> Dict[str, Any]:
        """Send email verification OTP"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #667eea; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .header h1 {{ color: white; margin: 0; font-size: 24px; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .otp-box {{ background: white; border: 2px dashed #667eea; padding: 20px; text-align: center; margin: 20px 0; border-radius: 8px; }}
                .otp-code {{ font-size: 32px; font-weight: bold; color: #667eea; letter-spacing: 5px; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Email Verification</h1>
                </div>
                <div class="content">
                    <h2>Hello {name},</h2>
                    <p>Use the following code to verify your email address:</p>
                    <div class="otp-box">
                        <div class="otp-code">{otp}</div>
                    </div>
                    <p><strong>This code expires in 10 minutes.</strong></p>
                    <p>If you didn't request this code, please ignore this email.</p>
                </div>
                <div class="footer">
                    <p>© 2026 SymptoMap. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(
            to=to,
            subject=f"Verify your email: {otp}",
            html=html,
            tags=[{"name": "category", "value": "verification"}]
        )
    
    async def send_password_reset_email(self, to: str, name: str, reset_link: str) -> Dict[str, Any]:
        """Send password reset email"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #dc3545; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .header h1 {{ color: white; margin: 0; font-size: 24px; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; background: #dc3545; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔑 Password Reset</h1>
                </div>
                <div class="content">
                    <h2>Hello {name},</h2>
                    <p>We received a request to reset your password. Click the button below to set a new password:</p>
                    <a href="{reset_link}" class="button">Reset Password</a>
                    <p><strong>This link expires in 1 hour.</strong></p>
                    <p>If you didn't request this, please ignore this email or contact support if you're concerned.</p>
                </div>
                <div class="footer">
                    <p>© 2026 SymptoMap. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(
            to=to,
            subject="Reset your SymptoMap password",
            html=html,
            tags=[{"name": "category", "value": "password_reset"}]
        )
    
    async def send_outbreak_alert(
        self,
        to: str | List[str],
        zone: str,
        disease: str,
        severity: str,
        patient_count: int
    ) -> Dict[str, Any]:
        """Send outbreak alert notification"""
        
        severity_colors = {
            "critical": "#dc3545",
            "severe": "#fd7e14",
            "moderate": "#ffc107",
            "mild": "#28a745"
        }
        color = severity_colors.get(severity.lower(), "#667eea")
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: {color}; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .header h1 {{ color: white; margin: 0; font-size: 24px; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .alert-box {{ background: white; border-left: 4px solid {color}; padding: 15px; margin: 20px 0; }}
                .stat {{ display: inline-block; background: {color}; color: white; padding: 5px 15px; border-radius: 20px; margin: 5px; }}
                .button {{ display: inline-block; background: {color}; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚨 OUTBREAK ALERT</h1>
                </div>
                <div class="content">
                    <div class="alert-box">
                        <h2>{disease} Outbreak in {zone}</h2>
                        <p>
                            <span class="stat">Severity: {severity.upper()}</span>
                            <span class="stat">Cases: {patient_count}</span>
                        </p>
                    </div>
                    <p>An outbreak has been reported and verified by health officials. Please take necessary precautions.</p>
                    <a href="https://symptomap.com/dashboard" class="button">View Details</a>
                </div>
                <div class="footer">
                    <p>© 2026 SymptoMap. Stay Safe.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(
            to=to,
            subject=f"🚨 {severity.upper()}: {disease} Outbreak in {zone}",
            html=html,
            tags=[
                {"name": "category", "value": "outbreak_alert"},
                {"name": "severity", "value": severity}
            ]
        )
    
    async def send_submission_status(
        self,
        to: str,
        name: str,
        disease: str,
        status: str,  # approved or rejected
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send submission approval/rejection notification"""
        
        is_approved = status.lower() == "approved"
        color = "#28a745" if is_approved else "#dc3545"
        icon = "✅" if is_approved else "❌"
        
        reason_html = f"<p><strong>Reason:</strong> {reason}</p>" if reason else ""
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: {color}; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .header h1 {{ color: white; margin: 0; font-size: 24px; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .status-box {{ background: white; border: 2px solid {color}; padding: 20px; text-align: center; margin: 20px 0; border-radius: 8px; }}
                .status {{ font-size: 24px; color: {color}; font-weight: bold; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{icon} Submission {status.title()}</h1>
                </div>
                <div class="content">
                    <h2>Hello {name},</h2>
                    <p>Your outbreak submission for <strong>{disease}</strong> has been reviewed.</p>
                    <div class="status-box">
                        <div class="status">{status.upper()}</div>
                    </div>
                    {reason_html}
                    <p>Thank you for contributing to public health surveillance.</p>
                </div>
                <div class="footer">
                    <p>© 2026 SymptoMap. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(
            to=to,
            subject=f"{icon} Your outbreak submission was {status}",
            html=html,
            tags=[{"name": "category", "value": "submission_status"}]
        )


# Global instance
email_service = EmailService()
