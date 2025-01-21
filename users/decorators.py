from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

def check_account_lockout(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            security_profile = request.user.usersecurityprofile
            if security_profile.account_locked_until:
                if timezone.now() < security_profile.account_locked_until:
                    messages.error(
                        request,
                        'Account is temporarily locked. Please try again later.'
                    )
                    return redirect('login')
                else:
                    # Reset lockout if time has expired
                    security_profile.account_locked_until = None
                    security_profile.failed_login_attempts = 0
                    security_profile.save()
        return view_func(request, *args, **kwargs)
    return wrapper

def require_2fa(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            security_profile = request.user.usersecurityprofile
            if security_profile.two_factor_enabled:
                if not request.session.get('2fa_verified'):
                    return redirect('2fa-verify')
        return view_func(request, *args, **kwargs)
    return wrapper