from django.core.cache import cache
from django.http import HttpResponseForbidden
from functools import wraps
from django.utils.decorators import method_decorator
from django.shortcuts import render
import time
import sys

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
            if not request.user.is_staff:  # Staff bypass
                # Get IP address with fall back
                ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
                if ip and "," in ip:
                    ip = ip.split(",")[0].strip()

                # Add user ID if authenticated for more precise limiting
                user_id = request.user.id if request.user.is_authenticated else None
                cache_key = f"rate_limit:{key_prefix}:{ip}:{user_id}"

                # Get current requests from cache
                requests = cache.get(cache_key, [])
                now = time.time()
                
                # Clean old requests
                requests = [req for req in requests if req > now - period]
                
                # Check if limit is exceeded
                if len(requests) >= limit:
                    # Calculate wait time
                    oldest_request = min(requests) if requests else now
                    wait_time = int((oldest_request + period - now) / 60) + 1  # Convert to minutes and round up
                    
                    return render(request, 'users/rate_limit_exceeded.html', {
                        'wait_time': wait_time,
                        'title': 'Rate Limit Exceeded',
                        'message': f'You have exceeded the {key_prefix} attempt limit.'
                    }, status=429)

                # Add current request timestamp
                requests.append(now)
                cache.set(cache_key, requests, period)

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

def profile_update_rate_limit():
    """20 profile updates per hour per user"""
    return rate_limit('profile_update', limit=20, period=3600)