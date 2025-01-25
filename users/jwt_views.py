from rest_framework import status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import authenticate
from .authentication import generate_tokens_for_user
import logging

logger = logging.getLogger(__name__)

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            
            user = authenticate(username=username, password=password)
            if user is None:
                logger.warning(f"Failed login attempt for username: {username}")
                return Response(
                    {'error': 'Invalid credentials'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )

            tokens = generate_tokens_for_user(user)
            logger.info(f"Tokens generated successfully for user: {username}")
            
            return Response(tokens, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Token generation error: {str(e)}")
            return Response(
                {'error': 'Authentication failed'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response(
                    {'error': 'Refresh token required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            refresh = RefreshToken(refresh_token)
            tokens = {
                'access': str(refresh.access_token),
            }
            
            logger.info("Access token refreshed successfully")
            return Response(tokens, status=status.HTTP_200_OK)
            
        except TokenError as e:
            logger.warning(f"Token refresh error: {str(e)}")
            return Response(
                {'error': 'Invalid refresh token'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            logger.error(f"Unexpected token refresh error: {str(e)}")
            return Response(
                {'error': 'Token refresh failed'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class LogoutView(views.APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response(
                    {'error': 'Refresh token required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            token = RefreshToken(refresh_token)
            token.blacklist()
            
            logger.info(f"User {request.user.username} logged out successfully")
            return Response(
                {'detail': 'Successfully logged out'}, 
                status=status.HTTP_200_OK
            )
        except TokenError as e:
            logger.warning(f"Logout error: {str(e)}")
            return Response(
                {'error': 'Invalid token'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unexpected logout error: {str(e)}")
            return Response(
                {'error': 'Logout failed'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )