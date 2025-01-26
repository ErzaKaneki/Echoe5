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
            # Production settings remain unchanged
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
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Base security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'SAMEORIGIN'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=self camera=self microphone=self interest-cohort=() payment=self'

        # Development vs Production CSP handling
        if settings.DEBUG:
            csp_directives = [
                "default-src 'self' http: https:",
                "img-src 'self' data: http: https: blob:",
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://code.jquery.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com http: https:",
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com http: https:",
                "font-src 'self' https://cdnjs.cloudflare.com http: https:",
                "connect-src 'self' http: https:",
                "media-src 'self' https://s3.amazonaws.com http: https:",
                "object-src 'none'",
                "base-uri 'self'"
            ]
        else:
            # Production CSP directives remain unchanged
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
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
            csp_directives.append("upgrade-insecure-requests")
            
            logger.info(
                f"Applied security headers for {request.path}. CSP directives: {'; '.join(csp_directives)}"
            )
        
        response['Content-Security-Policy'] = "; ".join(csp_directives)
        return response