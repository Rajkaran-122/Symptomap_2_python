import jwt
import secrets
import hashlib
from datetime import datetime
from flask import current_app
from app.extensions import db
from app.models.session import UserSession

class JWTService:
    
    @staticmethod
    def create_tokens(user_id: str, role: str, email: str, ip: str, ua: str) -> tuple[str, str]:
        """Returns (access_token, refresh_token)"""
        # Access Token
        access_payload = {
            'sub': user_id,
            'role': role,
            'email': email,
            'type': 'access',
            'jti': secrets.token_urlsafe(32),
            'exp': datetime.utcnow() + current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
        }
        access_token = jwt.encode(access_payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')
        
        # Refresh Token
        refresh_payload = {
            'sub': user_id,
            'type': 'refresh',
            'exp': datetime.utcnow() + current_app.config['JWT_REFRESH_TOKEN_EXPIRES']
        }
        refresh_token = jwt.encode(refresh_payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')
        
        # Store Refresh Token
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        
        session = UserSession(
            user_id=user_id,
            refresh_token_hash=token_hash,
            access_token_jti=access_payload['jti'],
            ip_address=ip,
            user_agent=ua,
            expires_at=refresh_payload['exp']
        )
        db.session.add(session)
        db.session.commit()
        
        return access_token, refresh_token
        
    @staticmethod
    def verify_token(token: str, type: str = 'access'):
        try:
            payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            if payload['type'] != type:
                return None
            return payload
        except:
            return None
