from rest_framework.throttling import UserRateThrottle
from django.conf import settings

class PostAPIThrottle(UserRateThrottle):
    rate = '100/day' if not settings.DEBUG else '1000/day'