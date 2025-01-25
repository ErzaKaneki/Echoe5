from django.urls import path
from . import views
from .auth import LoginAPIView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'posts', views.PostViewSet)

urlpatterns = [
    path('auth/login/', LoginAPIView.as_view(), name='api-login'),
    path('posts/', views.PostViewSet.as_view({'get': 'list', 'post': 'create'}), name='post-list'),
    path('posts/<int:pk>/', views.PostViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='post-detail'),
]