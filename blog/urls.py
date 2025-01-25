from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api.v1 import views as api_views
from .views import (
    PostListView,
    PostDetailView,
    PostCreateView,
    PostUpdateView,
    PostDeleteView,
    UserPostListView
)
from . import views


router = DefaultRouter()
router.register(r'posts', api_views.PostViewSet)

# Main URLs for frontend
main_urlpatterns = [
    path('', views.landing_page, name='landing-page'),
    path('home/', PostListView.as_view(), name='blog-home'),
    path('user/<str:username>/', UserPostListView.as_view(), name='user-posts'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('about/', views.about, name='blog-about'),
    path('privacy/', views.privacy, name='privacy'),
    path('terms/', views.terms, name='terms'),
]

# API URLs
api_urlpatterns = [
    path('api/v1/', include(router.urls)),
]

urlpatterns = main_urlpatterns + api_urlpatterns