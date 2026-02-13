from twilio.rest import Client
import requests
from flask import current_app
import threading

class SMSService:
    """SMS delivery service"""
    
    @staticmethod
    def send_otp_sms(to_phone: str, otp_code: str, purpose: str) -> bool:
        """Send OTP via SMS (async thread)"""
        thread = threading.Thread(
            target=SMSService._send_sync,
            args=(current_app._get_current_object(), to_phone, otp_code, purpose)
        )
        thread.start()
        return True

    @staticmethod
    def _send_sync(app, to_phone, otp_code, purpose):
        """Synchronous SMS send"""
        with app.app_context():
            provider = app.config.get('SMS_PROVIDER', 'mock')
            try:
                if provider == 'twilio':
                    SMSService._send_via_twilio(app, to_phone, otp_code, purpose)
                elif provider == 'mock':
                    print(f"[MOCK SMS] To: {to_phone} | Code: {otp_code} | Purpose: {purpose}")
            except Exception as e:
                print(f"Error sending SMS: {e}")

    @staticmethod
    def _send_via_twilio(app, to_phone, otp, purpose):
        client = Client(app.config['TWILIO_ACCOUNT_SID'], app.config['TWILIO_AUTH_TOKEN'])
        msg_body = f"SymptoMap: Your {purpose} code is {otp}. Valid for 5 mins."
        client.messages.create(
            body=msg_body,
            from_=app.config['TWILIO_PHONE_NUMBER'],
            to=to_phone
        )
