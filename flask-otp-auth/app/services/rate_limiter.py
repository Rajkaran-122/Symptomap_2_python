from datetime import datetime, timedelta
from app.extensions import db
from app.models.rate_limit import RateLimit
import sqlalchemy as sa

class RateLimiterService:
    """
    Custom Rate Limiter Service backed by PostgreSQL
    """
    
    LIMITS = {
        'otp_request': {'count': 3, 'window_minutes': 60},
        'login_attempt': {'count': 5, 'window_minutes': 15},
        'signup_attempt': {'count': 3, 'window_minutes': 60},
        'verification_attempt': {'count': 5, 'window_minutes': 5}
    }
    
    @staticmethod
    def check_rate_limit(identifier: str, identifier_type: str, action: str) -> tuple[bool, int, datetime | None]:
        """
        Returns: (allowed, remaining, blocked_until)
        """
        if action not in RateLimiterService.LIMITS:
            return True, 999, None
            
        config = RateLimiterService.LIMITS[action]
        max_count = config['count']
        window_mins = config['window_minutes']
        
        now = datetime.utcnow()
        
        # 1. Get record
        record = RateLimit.query.filter_by(
            identifier=identifier,
            identifier_type=identifier_type,
            action=action
        ).first()
        
        if not record:
            # Create new
            record = RateLimit(
                identifier=identifier,
                identifier_type=identifier_type,
                action=action,
                attempt_count=1,
                window_start=now
            )
            db.session.add(record)
            db.session.commit()
            return True, max_count - 1, None
            
        # 2. Check if blocked
        if record.blocked_until:
            if now < record.blocked_until:
                return False, 0, record.blocked_until
            else:
                # Block expired
                record.blocked_until = None
                record.attempt_count = 1
                record.window_start = now
                db.session.commit()
                return True, max_count - 1, None
        
        # 3. Check window expiry
        window_end = record.window_start + timedelta(minutes=window_mins)
        if now > window_end:
            # Reset window
            record.attempt_count = 1
            record.window_start = now
            record.blocked_until = None
            db.session.commit()
            return True, max_count - 1, None
            
        # 4. Check limits
        if record.attempt_count >= max_count:
            # Block!
            record.blocked_until = window_end
            db.session.commit()
            return False, 0, window_end
            
        # 5. Increment
        record.attempt_count += 1
        db.session.commit()
        
        return True, max_count - record.attempt_count, None
