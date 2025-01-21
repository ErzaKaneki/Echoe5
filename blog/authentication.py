from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import User
import secrets
import logging

logger = logging.getLogger(__name__)

class APIKeyAuthentication(BaseAuthentication):
    """Custom API key authentication for the blog API"""
    
    def authenticate(self, request):
        api_key = request.META.get('HTTP_X_API_KEY')
        if not api_key:
            return None  # No API key provided, fall back to other authentication methods
            
        try:
            user = User.objects.get(usersecurityprofile__api_key=api_key)
            logger.info(f"Successful API authentication for user: {user.username}")
            return (user, None)
        except User.DoesNotExist:
            logger.warning(f"Failed API authentication attempt with key: {api_key[:8]}...")
            raise AuthenticationFailed('Invalid API key')
            
    def authenticate_header(self, request):
        return 'X-API-Key'