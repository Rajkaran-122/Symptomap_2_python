from flask import request, jsonify
from functools import wraps

def require_auth(roles=None):
    """
    Authentication decorator
    Usage: @require_auth(roles=['admin'])
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'error': 'Missing or invalid token'}), 401
                
            token = auth_header.split(' ')[1]
            from app.auth.jwt_service import JWTService
            payload = JWTService.verify_token(token, 'access')
            
            if not payload:
                print("Token verification failed")
                return jsonify({'error': 'Invalid or expired token'}), 401
                
            if roles and payload['role'] not in roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
                
            # Inject user info into request
            request.user_id = payload['sub']
            request.user_role = payload['role']
            request.user_email = payload['email']
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
