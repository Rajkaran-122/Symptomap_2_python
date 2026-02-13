import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app
import threading

class EmailService:
    """Email delivery service using SMTP"""
    
    @staticmethod
    def send_otp_email(to_email: str, otp_code: str, purpose: str, user_name: str = None) -> bool:
        """
        Send OTP via email (runs in thread to avoid blocking)
        Returns: True (assumed queued successfully)
        """
        # threading for async behavior in Flask without Celery for MVP
        thread = threading.Thread(
            target=EmailService._send_sync,
            args=(current_app._get_current_object(), to_email, otp_code, purpose, user_name)
        )
        thread.start()
        return True

    @staticmethod
    def _send_sync(app, to_email, otp_code, purpose, user_name):
        """Synchronous SMTP send"""
        with app.app_context():
            try:
                subject, html_body = EmailService._get_email_template(otp_code, purpose, user_name)
                
                msg = MIMEMultipart('alternative')
                msg['From'] = app.config['SMTP_FROM_EMAIL']
                msg['To'] = to_email
                msg['Subject'] = subject
                
                msg.attach(MIMEText(html_body, 'html'))
                
                with smtplib.SMTP(app.config['SMTP_HOST'], app.config['SMTP_PORT']) as server:
                    server.starttls()
                    server.login(app.config['SMTP_USERNAME'], app.config['SMTP_PASSWORD'])
                    server.send_message(msg)
                    
            except Exception as e:
                # In production, log this to error monitor
                print(f"Error sending email: {e}")

    @staticmethod
    def _get_email_template(otp, purpose, user_name) -> tuple[str, str]:
        """Get email subject and HTML body"""
        name_str = f" {user_name}" if user_name else ""
        
        if purpose == 'signup':
            return 'Verify Your Email - SymptoMap', f'''
                <h2>Welcome to SymptoMap!</h2>
                <p>Hello{name_str},</p>
                <p>Your verification code is: <strong>{otp}</strong></p>
                <p>Valid for 5 minutes.</p>
            '''
        elif purpose == 'login':
             return 'Login Verification - SymptoMap', f'''
                <h2>Login Verification</h2>
                <p>Hello{name_str},</p>
                <p>Your login code is: <strong>{otp}</strong></p>
                <p>Valid for 5 minutes.</p>
            '''
        elif purpose == 'password_reset':
             return 'Password Reset - SymptoMap', f'''
                <h2>Password Reset</h2>
                <p>Hello{name_str},</p>
                <p>Your password reset code is: <strong>{otp}</strong></p>
                <p>Valid for 5 minutes.</p>
            '''
        return 'Verification Code', f'Your code is {otp}'
