from rest_framework.throttling import UserRateThrottle
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class PostAPIThrottle(UserRateThrottle):
    rate = '100/day' if not settings.DEBUG else '1000/day'
    
    def allow_request(self, request, view):
        allowed = super().allow_request(request, view)
        if not allowed:
            logger.warning(
                f"API rate limit exceeded for user {request.user.username if request.user.is_authenticated else 'anonymous'}"
            )
        return allowed