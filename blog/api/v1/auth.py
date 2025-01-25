from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            username = request.data.get('username')
            password = request.data.get('password')

            user = authenticate(username=username, password=password)
            if not user:
                logger.warning(f"Failed login attempt for username: {username}")
                return Response({
                    'error': 'Invalid credentials'
                }, status=status.HTTP_401_UNAUTHORIZED)

            refresh = RefreshToken.for_user(user)
            
            # Generate tokens
            tokens = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }

            response = Response(tokens, status=status.HTTP_200_OK)
            
            # Set cookie in production
            if not settings.DEBUG:
                response.set_cookie(
                    'access_token',
                    tokens['access'],
                    httponly=True,
                    secure=True,
                    samesite='Strict',
                    max_age=3600  # 1 hour
                )

            logger.info(f"Successful API login for user: {username}")
            return response

        except Exception as e:
            logger.error(f"API login error: {str(e)}")
            return Response({
                'error': 'Authentication failed'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)