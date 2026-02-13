import secrets
import hashlib
from datetime import datetime, timedelta
from app.extensions import db
from app.models.otp import OTP

class OTPService:
    @staticmethod
    def generate_otp() -> str:
        return ''.join(str(secrets.randbelow(10)) for _ in range(6))
        
    @staticmethod
    def hash_otp(otp: str, user_id: str) -> str:
        data = f"{user_id}:{otp}".encode('utf-8')
        return hashlib.sha256(data).hexdigest()
        
    @staticmethod
    def create_otp(user_id: str, purpose: str, ip_address: str, user_agent: str) -> str:
        otp_code = OTPService.generate_otp()
        otp_hash = OTPService.hash_otp(otp_code, user_id)
        
        otp_entry = OTP(
            user_id=user_id,
            otp_hash=otp_hash,
            purpose=purpose,
            expires_at=datetime.utcnow() + timedelta(minutes=5),
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.session.add(otp_entry)
        db.session.commit()
        return otp_code, otp_entry.id

    @staticmethod
    def verify_otp(user_id: str, otp_input: str, purpose: str) -> tuple[bool, str]:
        """Returns: (success, message)"""
        # Find active valid OTP
        otp_record = OTP.query.filter_by(
            user_id=user_id,
            purpose=purpose,
            is_used=False
        ).order_by(OTP.created_at.desc()).first()
        
        if not otp_record:
            return False, "No active OTP found"
            
        if datetime.utcnow() > otp_record.expires_at:
            return False, "OTP expired"
            
        if otp_record.verification_attempts >= 5:
            otp_record.is_used = True  # Invalidate
            db.session.commit()
            return False, "Too many failed attempts"
            
        # Verify
        computed_hash = OTPService.hash_otp(otp_input, user_id)
        if secrets.compare_digest(otp_record.otp_hash, computed_hash):
            otp_record.is_used = True
            otp_record.verified_at = datetime.utcnow()
            otp_record.verification_attempts += 1
            db.session.commit()
            return True, "Success"
        else:
            otp_record.verification_attempts += 1
            db.session.commit()
            return False, "Invalid OTP"
