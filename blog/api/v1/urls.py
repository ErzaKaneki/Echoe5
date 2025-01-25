from django.urls import path
from . import views
from .auth import TokenAuthenticationAPI

urlpatterns = [
    # Authentication endpoint
    path('auth/token/', TokenAuthenticationAPI.as_view(), name='api-token-auth'),
    
    # Posts endpoints
    path('posts/', views.PostViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='post-list'),
    
    path('posts/<int:pk>/', views.PostViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='post-detail'),
]