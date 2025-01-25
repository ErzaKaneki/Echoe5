"""
URL configuration for django_blog_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib.auth import views as auth_views
from users.rate_limiting import login_rate_limit
from django.utils.decorators import method_decorator
from django.urls import path, include
from django.conf import settings
from users import views as user_views
from .jwt_views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    LogoutView
)


class RateLimitedLoginView(auth_views.LoginView):
    @method_decorator(login_rate_limit())
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

urlpatterns = [
    path('register/', user_views.register, name='register'),
    path('profile/', user_views.profile, name='profile'),
    path('login/', RateLimitedLoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('password-reset/',
         auth_views.PasswordResetView.as_view(template_name='users/password_reset.html'),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),
         name='password_reset_complete'),
     path('2fa/setup/', user_views.setup_2fa, name='2fa-setup'),
    path('2fa/verify/', user_views.verify_2fa, name='2fa-verify'),
    path('2fa/backup/', user_views.backup_code_verify, name='2fa-backup'),
    path('2fa/disable/', user_views.disable_2fa, name='2fa-disable'),
    path('2fa/backup-codes/', user_views.BackupCodesView.as_view(), name='2fa-backup-codes'), 
    path('verify-email/<str:uidb64>/<str:token>/', user_views.verify_email, name='verify_email'),
    path('email-verification-sent/', user_views.email_verification_sent, name='email_verification_sent'),
]

jwt_patterns = [
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/logout/', LogoutView.as_view(), name='token_logout'),
]

urlpatterns += jwt_patterns