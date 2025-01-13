from django.http import JsonResponse
from django.template.response import TemplateResponse

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if response.status_code == 403 and 'Too many attempts' in str(response.content):
            context = {
                    'title': 'Rate Limit Exceeded',
                    'message': 'You have made too many requests. Please try again later.',
                    'retry_after': 5 #minutes
            }
            return TemplateResponse(
                    request,
                    'users/rate_limit_exceeded.html',
                    context,
                    status=429
            )
        return response
