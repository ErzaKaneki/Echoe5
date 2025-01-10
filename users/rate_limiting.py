from django.core.cache import cache
from django.http import HttpResponseForbidden
from functools import wraps
from django.utils.decorators import method_decorator
import time

def rate_limit(key_prefix, limit=5, period=300):
    """
    Rate limiting decorator that limits views based on IP and optional user ID

    Args:
        key_prefix (str): Identifier for the type of rate limit (e.g., 'login', 'post')
        limit (int): Number of allowed requests within the period
        period (int): Time period in seconds
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            # Get IP address
            ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))

            # Add user ID if authenticated for more precise limiting
            user_id = request.user.id if request.user.is_authenticated else None
            cache_key = f"rate_limit:{key_prefix}:{ip}:{user_id}"

            # Get current requests from cache
            requests = cache.get(cache_key, [])
            now = time.time()

            # Add current request timestamp
            requests.append(now)
            cache.set(catche_key, requests, period)

            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator

# Specific rate limiters for different actions
def login_rate_limit():
    """5 login attempts per 5 minutes"""
    return rate_limit('login', limit=5, period=300)

def registration_rate_limit():
    """3 registration attempts per hour per IP"""
    return rate_limit('registration', limit=3, period=3600)

def post_creation_rate_limit():
    """10 posts per hour per user"""
    return rate_limit('post_creation', limit=10, period=3600)
