from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.conf import settings
import jwt
import logging

logger = logging.getLogger(__name__)

class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        try:
            header = self.get_header(request)
            if header is None:
                return None

            raw_token = self.get_raw_token(header)
            if raw_token is None:
                return None

            validated_token = self.get_validated_token(raw_token)
            user = self.get_user(validated_token)
            
            # Log successful authentication
            logger.info(f"JWT Authentication successful for user: {user.username}")
            
            return user, validated_token

        except InvalidToken as e:
            logger.warning(f"Invalid token: {str(e)}")
            raise
        except TokenError as e:
            logger.warning(f"Token error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected authentication error: {str(e)}")
            raise

def generate_tokens_for_user(user):
    """Generate access and refresh tokens for a user"""
    try:
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    except Exception as e:
        logger.error(f"Error generating tokens for user {user.username}: {str(e)}")
        raise

def validate_token(token):
    """Validate a JWT token"""
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY,
            algorithms=["HS256"]
        )
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        return None
    except jwt.InvalidTokenError:
        logger.warning("Invalid token")
        return None
    except Exception as e:
        logger.error(f"Token validation error: {str(e)}")
        return None