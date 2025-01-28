from django.shortcuts import redirect
from django.urls import resolve
from django.conf import settings
from django.http import HttpResponseForbidden
from django.core.cache import cache
import time
import logging

logger = logging.getLogger(__name__)

class RateLimitMiddleware:
    """Rate limiting middleware to prevent abuse"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Rate limit settings
        self.RATE_LIMITS = {
            'POST': {'max_requests': 50, 'time_window': 3600},  # 50 requests per hour
            'GET': {'max_requests': 200, 'time_window': 3600},  # 200 requests per hour
        }

    def __call__(self, request):
        if not request.user.is_staff:  # Staff bypass rate limiting
            # Get IP with fallback options
            ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
            if ip and "," in ip:
                ip = ip.split(",")[0].strip()

            method = request.method
            if method in self.RATE_LIMITS:
                cache_key = f'rate_limit:{ip}:{method}'
                now = time.time()
                
                # Get current requests from cache
                requests = cache.get(cache_key, [])
                
                # Clean old requests outside time window
                requests = [req for req in requests 
                          if req > now - self.RATE_LIMITS[method]['time_window']]
                
                # Check if limit exceeded
                if len(requests) >= self.RATE_LIMITS[method]['max_requests']:
                    logger.warning(f'Rate limit exceeded for IP: {ip}, Method: {method}')
                    return HttpResponseForbidden('Rate limit exceeded. Please try again later.')
                
                # Add current request and update cache
                requests.append(now)
                cache.set(
                    cache_key,
                    requests,
                    self.RATE_LIMITS[method]['time_window']
                )

        return self.get_response(request)

class AuthenticationMiddleware:
    """Middleware to restrict non-authenticated users to landing page only"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        # URLs that don't require authentication
        self.public_urls = {
            'landing-page',
            'login',
            'register',
            'password_reset',
            'password_reset_done',
            'password_reset_confirm',
            'password_reset_complete',
            'verify_email',
            'email_verification_sent',
            'social:begin',
            'social:complete',
            'api-token-auth',
            'token_obtain_pair',
            'token_refresh',
            'token_verify',
            'swagger',
            'redoc',
        }

    def __call__(self, request):
        # Get current URL name
        try:
            current_url_name = resolve(request.path_info).url_name
        except:
            current_url_name = None

        # Special handling for admin URLs
        if request.path.startswith('/admin/'):
            if not request.user.is_authenticated:
                logger.warning(f"Unauthenticated user attempted to access admin: {request.path}")
                return redirect('landing-page')
            elif not request.user.is_staff:
                logger.warning(
                    f"Authenticated non-staff user attempted to access admin: {request.user.username}"
                )
                return redirect('blog-home')  # Redirect authenticated non-staff to home
            return self.get_response(request)

        # Check if user is authenticated and URL is restricted
        if not request.user.is_authenticated:
            # Allow access to static and media files
            if request.path.startswith((settings.STATIC_URL, settings.MEDIA_URL)):
                return self.get_response(request)
                
            # Allow access to public URLs
            if current_url_name not in self.public_urls:
                logger.info(
                    f"Redirecting unauthenticated user from {request.path} to landing page"
                )
                return redirect('landing-page')

        response = self.get_response(request)
        return response