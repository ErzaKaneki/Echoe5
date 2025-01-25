from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    """Custom exception handler for REST framework API views"""
    
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # If unexpected error occurs (not handled by DRF's exception handler)
    if response is None:
        logger.error(f"Unhandled exception: {str(exc)}")
        response = Response({
            'error': 'Internal server error',
            'detail': 'An unexpected error occurred'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    else:
        # Add more context to the response
        if response.status_code == 404:
            response.data = {
                'error': 'Not found',
                'detail': response.data.get('detail', 'The requested resource was not found')
            }
            
        elif response.status_code == 403:
            response.data = {
                'error': 'Permission denied',
                'detail': response.data.get('detail', 'You do not have permission to perform this action')
            }
            
        elif response.status_code == 401:
            response.data = {
                'error': 'Authentication failed',
                'detail': response.data.get('detail', 'Authentication credentials were not provided')
            }
            
        elif response.status_code == 400:
            response.data = {
                'error': 'Bad request',
                'detail': response.data
            }
            
        # Log client errors
        if 400 <= response.status_code < 500:
            logger.warning(
                f"Client error: {response.status_code} at {context['request'].path}",
                extra={
                    'status_code': response.status_code,
                    'path': context['request'].path,
                    'user': getattr(context['request'].user, 'username', 'anonymous'),
                    'error_detail': response.data
                }
            )
        
        # Log server errors
        elif response.status_code >= 500:
            logger.error(
                f"Server error: {response.status_code} at {context['request'].path}",
                extra={
                    'status_code': response.status_code,
                    'path': context['request'].path,
                    'user': getattr(context['request'].user, 'username', 'anonymous'),
                    'error_detail': response.data
                }
            )
    
    return response