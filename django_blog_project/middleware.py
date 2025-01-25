from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class CORSMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Development settings
        if settings.DEBUG:
            response["Access-Control-Allow-Credentials"] = "true"
            response["Access-Control-Allow-Origin"] = request.headers.get("Origin", "")
            response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-CSRFToken"
            response["Access-Control-Max-Age"] = "3600"
        else:
            # Production settings
            origin = request.headers.get("Origin", "")
            allowed_origins = ["https://echoe5.com", "https://www.echoe5.com"]
            
            if origin in allowed_origins:
                response["Access-Control-Allow-Credentials"] = "true"
                response["Access-Control-Allow-Origin"] = origin
                response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
                response["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-CSRFToken"
                response["Access-Control-Max-Age"] = "3600"
                
                logger.info(f"CORS headers set for origin: {origin}")

        return response

class SecurityHeadersMiddleware:
    """Enhanced security headers middleware that handles both general and API security"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Base security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'SAMEORIGIN'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=self camera=self microphone=self interest-cohort=() payment=self'
        
        # API-specific headers for /api/ endpoints
        if request.path.startswith('/api/'):
            response['Access-Control-Allow-Origin'] = 'https://echoe5.com' if not settings.DEBUG else 'http://localhost:8000'
            response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            
        # Enhanced CSP header with all required sources
        csp_directives = [
            "default-src 'self'",
            "img-src 'self' data: https://*.googleusercontent.com https://*.google.com https://s3.amazonaws.com",
            "script-src 'self' 'unsafe-inline' https://code.jquery.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://accounts.google.com https://apis.google.com",
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com",
            "font-src 'self' https://cdnjs.cloudflare.com https://fonts.gstatic.com",
            "frame-src 'self' https://accounts.google.com",
            "connect-src 'self' https://*.google.com https://accounts.google.com",
            "media-src 'self' https://s3.amazonaws.com",
            "object-src 'none'",
            "base-uri 'self'"
        ]
        
        # Add HSTS and upgrade-insecure-requests in production
        if not settings.DEBUG:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
            csp_directives.append("upgrade-insecure-requests")
            
            # Log security header application in production
            logger.info(
                f"Applied security headers for {request.path}. CSP directives: {'; '.join(csp_directives)}"
            )
        
        response['Content-Security-Policy'] = "; ".join(csp_directives)
        return response