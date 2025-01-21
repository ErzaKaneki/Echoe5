from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import User
import secrets

class APIKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        api_key = request.META.get('HTTP_X_API_KEY')
        if not api_key:
            return None
            
        try:
            user = User.objects.get(api_key=api_key)
            return (user, None)
        except User.DoesNotExist:
            raise AuthenticationFailed('Invalid API key')