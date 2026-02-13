"""
Security Middleware for SymptoMap
- Security headers injection
- Request validation
- Response sanitization
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from typing import Callable
import time


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    SECURITY_HEADERS = {
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(self), camera=(), microphone=()",
        "X-Permitted-Cross-Domain-Policies": "none",
    }
    
    # CSP for API (more restrictive than frontend)
    CSP_POLICY = (
        "default-src 'none'; "
        "frame-ancestors 'none'; "
        "base-uri 'none'; "
        "form-action 'none'"
    )
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip for non-HTTP requests (like WebSockets)
        if request.scope["type"] != "http":
            return await call_next(request)
            
        # Skip for OPTIONS requests (CORS preflight)
        # CORSMiddleware handles these, we shouldn't add security headers that might break it
        if request.method == "OPTIONS":
            return await call_next(request)
            
        response = await call_next(request)
        
        # Add security headers
        for header, value in self.SECURITY_HEADERS.items():
            response.headers[header] = value
        
        # Add CSP for API responses (except for Swagger docs)
        if not request.url.path.startswith("/docs") and not request.url.path.startswith("/redoc"):
            response.headers["Content-Security-Policy"] = self.CSP_POLICY
        
        return response


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """Add request timing headers"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip for non-HTTP
        if request.scope["type"] != "http":
            return await call_next(request)
            
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.4f}"
        return response


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """Validate incoming requests"""
    
    # Maximum request body size (5MB)
    MAX_BODY_SIZE = 5 * 1024 * 1024
    
    # Blocked user agents (common attack tools)
    BLOCKED_USER_AGENTS = [
        "sqlmap",
        "nikto",
        "nessus",
        "nmap",
        "masscan",
        "zgrab",
    ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip for non-HTTP and OPTIONS
        if request.scope["type"] != "http" or request.method == "OPTIONS":
            return await call_next(request)
            
        # Check User-Agent for known attack tools
        user_agent = request.headers.get("User-Agent", "").lower()
        for blocked in self.BLOCKED_USER_AGENTS:
            if blocked in user_agent:
                return Response(
                    content='{"detail": "Request blocked"}',
                    status_code=403,
                    media_type="application/json"
                )
        
        # Check Content-Length
        content_length = request.headers.get("Content-Length")
        if content_length and int(content_length) > self.MAX_BODY_SIZE:
            return Response(
                content='{"detail": "Request body too large"}',
                status_code=413,
                media_type="application/json"
            )
        
        return await call_next(request)


class IPBlocklistMiddleware(BaseHTTPMiddleware):
    """Block requests from blacklisted IPs"""
    
    # In-memory blocklist (use Redis in production)
    _blocklist: set = set()
    
    @classmethod
    def block_ip(cls, ip: str) -> None:
        cls._blocklist.add(ip)
    
    @classmethod
    def unblock_ip(cls, ip: str) -> None:
        cls._blocklist.discard(ip)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip for non-HTTP
        if request.scope["type"] != "http":
            return await call_next(request)
            
        # Get client IP
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"
        
        # Check blocklist
        if client_ip in self._blocklist:
            return Response(
                content='{"detail": "Access denied"}',
                status_code=403,
                media_type="application/json"
            )
        
        return await call_next(request)


def setup_security_middleware(app):
    """Setup all security middleware"""
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestTimingMiddleware)
    app.add_middleware(RequestValidationMiddleware)
    app.add_middleware(IPBlocklistMiddleware)
