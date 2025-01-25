from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class TokenAuthenticationAPI(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            username = request.data.get('username')
            password = request.data.get('password')

            if not username or not password:
                return Response({
                    'error': 'Both username and password are required'
                }, status=status.HTTP_400_BAD_REQUEST)

            user = authenticate(username=username, password=password)
            if not user:
                logger.warning(f"Failed login attempt for username: {username}")
                return Response({
                    'error': 'Invalid credentials'
                }, status=status.HTTP_401_UNAUTHORIZED)

            # Generate tokens for authenticated user
            refresh = RefreshToken.for_user(user)
            tokens = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }

            # Create response with tokens
            response = Response(tokens, status=status.HTTP_200_OK)
            
            # In production, set JWT as HttpOnly cookie
            if not settings.DEBUG:
                response.set_cookie(
                    'access_token',
                    tokens['access'],
                    httponly=True,
                    secure=True,
                    samesite='Strict',
                    max_age=3600  # 1 hour
                )
            
            logger.info(f"User {username} successfully authenticated via API")
            return response

        except Exception as e:
            logger.error(f"API authentication error: {str(e)}")
            return Response({
                'error': 'Authentication failed',
                'detail': str(e) if settings.DEBUG else 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)