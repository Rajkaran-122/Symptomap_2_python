from flask import Blueprint, request, jsonify, current_app
from app.extensions import db, limiter
from app.models.user import User
from app.models.otp import OTP
from app.models.auth_event import AuthEvent
from app.services.email_service import EmailService
from app.services.sms_service import SMSService
from app.services.rate_limiter import RateLimiterService
from app.auth.otp_service import OTPService
from app.auth.jwt_service import JWTService
from app.utils.security import hash_password, verify_password
from app.utils.validators import validate_email, validate_password, validate_phone
from app.middleware.security import require_auth
from datetime import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/signup', methods=['POST'])
@limiter.limit("5 per minute")
def signup():
    data = request.get_json()
    email = data.get('email', '').lower().strip()
    phone = data.get('phone', '').strip()
    password = data.get('password', '')
    role = data.get('role', 'user')
    
    # 1. Validation
    if not validate_email(email):
        return jsonify({'error': 'Invalid email'}), 400
    if not validate_password(password):
        return jsonify({'error': 'Weak password'}), 400
        
    # 2. Check Exists
    if User.query.filter((User.email == email) | (User.phone == phone)).first():
        return jsonify({'error': 'User exists'}), 409
        
    # 3. Create User
    user = User(
        email=email,
        phone=phone,
        password_hash=hash_password(password),
        role=role,
        is_verified=False
    )
    db.session.add(user)
    db.session.commit()
    
    # 4. Send OTP
    otp_code, _ = OTPService.create_otp(
        user.id, 'signup', request.remote_addr, request.user_agent.string
    )
    EmailService.send_otp_email(email, otp_code, 'signup')
    SMSService.send_otp_sms(phone, otp_code, 'signup')
    
    return jsonify({'message': 'User created. Please verify.', 'user_id': user.id}), 201

@auth_bp.route('/verify-otp', methods=['POST'])
@limiter.limit("10 per minute")
def verify_otp():
    data = request.get_json()
    email = data.get('email', '').lower()
    otp = data.get('otp', '')
    purpose = data.get('purpose', 'signup')
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    success, msg = OTPService.verify_otp(user.id, otp, purpose)
    
    if success:
        if purpose == 'signup':
            user.is_verified = True
            db.session.commit()
            
        return jsonify({'message': 'Verified successfully'}), 200
    else:
        return jsonify({'error': msg}), 400

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")  # Basic DDoS protection
def login():
    data = request.get_json()
    email = data.get('email', '').lower()
    password = data.get('password', '')
    
    # 1. Custom Rate Limiter (Business Logic)
    allowed, remaining, blocked_until = RateLimiterService.check_rate_limit(
        email, 'email', 'login_attempt'
    )
    if not allowed:
        return jsonify({'error': 'Too many failed attempts', 'blocked_until': blocked_until}), 429
        
    # 2. Verify User
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
        
    valid, new_hash = verify_password(user.password_hash, password)
    if not valid:
        return jsonify({'error': 'Invalid credentials'}), 401
        
    if new_hash:
        user.password_hash = new_hash
        db.session.commit()
        
    # 3. 2FA (Send OTP)
    otp_code, _ = OTPService.create_otp(
        user.id, 'login', request.remote_addr, request.user_agent.string
    )
    
    EmailService.send_otp_email(user.email, otp_code, 'login')
    if user.phone:
        SMSService.send_otp_sms(user.phone, otp_code, 'login')
        
    return jsonify({'message': 'Password valid. OTP sent.', 'otp_required': True}), 200

@auth_bp.route('/login/verify', methods=['POST'])
def login_verify():
    data = request.get_json()
    email = data.get('email', '').lower()
    otp = data.get('otp', '')
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    success, msg = OTPService.verify_otp(user.id, otp, 'login')
    if not success:
        return jsonify({'error': msg}), 400
        
    # Success - Issue Tokens
    access, refresh = JWTService.create_tokens(
        user.id, user.role, user.email, 
        request.remote_addr, request.user_agent.string
    )
    
    return jsonify({
        'access_token': access,
        'refresh_token': refresh,
        'user': user.to_dict()
    }), 200

@auth_bp.route('/me', methods=['GET'])
@require_auth()
def me():
    print(f"Me endpoint called by user_id: {request.user_id}")
    return jsonify({
        'user_id': request.user_id,
        'role': request.user_role,
        'email': request.user_email
    })

@auth_bp.route('/forgot-password', methods=['POST'])
@limiter.limit("3 per hour")
def forgot_password():
    data = request.get_json()
    email = data.get('email', '').lower()
    
    user = User.query.filter_by(email=email).first()
    if user:
        otp_code, _ = OTPService.create_otp(
            user.id, 'password_reset', request.remote_addr, request.user_agent.string
        )
        EmailService.send_otp_email(user.email, otp_code, 'password_reset')
        if user.phone:
            SMSService.send_otp_sms(user.phone, otp_code, 'password_reset')
            
    # Always return 200 to prevent enumeration
    return jsonify({'message': 'If account exists, OTP sent.'}), 200

@auth_bp.route('/reset-password', methods=['POST'])
@limiter.limit("5 per hour")
def reset_password():
    data = request.get_json()
    email = data.get('email', '').lower()
    otp = data.get('otp', '')
    new_password = data.get('new_password', '')
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    success, msg = OTPService.verify_otp(user.id, otp, 'password_reset')
    if not success:
        return jsonify({'error': msg}), 400
        
    if not validate_password(new_password):
        return jsonify({'error': 'Weak password'}), 400
        
    user.password_hash = hash_password(new_password)
    # Invalidate all sessions (optional but secure)
    # UserSession.query.filter_by(user_id=user.id).delete()
    db.session.commit()
    
    return jsonify({'message': 'Password reset successfully'}), 200
