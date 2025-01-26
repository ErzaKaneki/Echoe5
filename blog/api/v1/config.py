from rest_framework import permissions
from django.conf import settings

class CustomAPIPermission(permissions.BasePermission):
    """
    Custom permission class that handles both development and production scenarios
    """
    def has_permission(self, request, view):
        # Staff users bypass restrictions
        if request.user and request.user.is_staff:
            return True
            
        # In development, allow authenticated users
        if settings.DEBUG:
            return request.user and request.user.is_authenticated
            
        # In production, implement stricter checks
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Add any additional production checks here
        if hasattr(request.user, 'usersecurityprofile'):
            if request.user.usersecurityprofile.is_account_locked():
                return False
        
        return True

# API Throttle rates based on environment
THROTTLE_RATES = {
    'development': {
        'post_create': '100/day',
        'post_list': '1000/day',
        'user_detail': '1000/day'
    },
    'production': {
        'post_create': '50/day',
        'post_list': '200/day',
        'user_detail': '100/day'
    }
}

def get_throttle_rate(rate_key):
    """
    Get appropriate throttle rate based on environment
    """
    env_rates = THROTTLE_RATES['development' if settings.DEBUG else 'production']
    return env_rates.get(rate_key, '50/day')  # Default fallback rate

# Standard API response structure
class APIResponse:
    @staticmethod
    def success(data=None, message=None, status=200):
        response = {
            'success': True,
            'status': status
        }
        if data is not None:
            response['data'] = data
        if message:
            response['message'] = message
        return response

    @staticmethod
    def error(message, status=400, errors=None):
        response = {
            'success': False,
            'status': status,
            'message': message
        }
        if errors:
            response['errors'] = errors
        return response