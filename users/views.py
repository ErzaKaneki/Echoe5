from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.views import LoginView
from django.views.generic import TemplateView
from django.db import transaction
from .forms import (
    UserRegisterForm,
    UserUpdateForm,
    ProfileUpdateForm,
    TwoFactorVerificationForm,
    TwoFactorBackupForm
)
from .models import Profile, UserSecurityProfile
from .rate_limiting import (
    registration_rate_limit,
    profile_update_rate_limit,
    login_rate_limit
)
from .decorators import check_account_lockout, require_2fa
import qrcode
import qrcode.image.svg
from io import BytesIO
import base64
import logging

logger = logging.getLogger(__name__)

class RateLimitedLoginView(LoginView):
    """Custom login view with rate limiting and security features"""
    
    @method_decorator(login_rate_limit())
    @method_decorator(check_account_lockout)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        """Handle successful login attempt"""
        user = form.get_user()
        security_profile = user.usersecurityprofile
        
        # Reset failed login attempts on successful login
        security_profile.reset_login_attempts()
        
        # Check if password change is required
        if security_profile.should_change_password():
            messages.warning(
                self.request,
                'Your password needs to be updated. Please change it now.'
            )
            return redirect('password_change')
        
        # Check if 2FA is required
        if security_profile.two_factor_enabled:
            self.request.session['partial_login_user_id'] = user.id
            return redirect('2fa-verify')
        
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Handle failed login attempt"""
        try:
            username = form.cleaned_data.get('username') if form.cleaned_data else None
            if username:
                try:
                    user = User.objects.get(username=username)
                    security_profile = user.usersecurityprofile
                    security_profile.record_failed_login()
                    
                    if security_profile.is_account_locked():
                        messages.error(
                            self.request,
                            'Account temporarily locked due to multiple failed attempts.'
                        )
                        logger.warning(f"Account locked for user {username}")
                except User.DoesNotExist:
                    # Don't reveal whether username exists
                    logger.info(f"Failed login attempt for non-existent user: {username}")
                    pass
        except Exception as e:
            logger.error(f"Error in login attempt: {str(e)}")
            
        return super().form_invalid(form)

@registration_rate_limit()
def register(request):
    """User registration with security features"""
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save(commit=False)
                    user.is_active = False  # Require email verification
                    user.save()
                    
                    messages.success(
                        request,
                        'Account created! Please check your email to verify your account.'
                    )
                    logger.info(f"Successfully registered user: {user.username}")
                    return redirect('login')
                    
            except Exception as e:
                logger.error(f"Registration error: {str(e)}")
                messages.error(
                    request,
                    'An error occurred during registration. Please try again.'
                )
    else:
        form = UserRegisterForm()
    
    return render(request, 'users/register.html', {'form': form})

@login_required
@profile_update_rate_limit()
@require_2fa
def profile(request):
    """User profile management with 2FA requirement"""
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=request.user.profile
        )

        if u_form.is_valid() and p_form.is_valid():
            try:
                u_form.save()
                profile = p_form.save()
                messages.success(request, 'Your account has been updated!')
                logger.info(f"Profile updated for user {request.user.username}")
                return redirect('profile')
            except Exception as e:
                logger.error(f"Profile update error for {request.user.username}: {str(e)}")
                messages.error(request, 'Error updating profile. Please try again.')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'two_factor_enabled': request.user.usersecurityprofile.two_factor_enabled
    }
    return render(request, 'users/profile.html', context)

@login_required
def setup_2fa(request):
    """2FA setup with QR code generation"""
    security_profile = request.user.usersecurityprofile
    
    # Redirect if 2FA already enabled
    if security_profile.two_factor_enabled:
        messages.info(request, '2FA is already enabled for your account.')
        return redirect('profile')

    if request.method == 'POST':
        form = TwoFactorVerificationForm(request.POST)
        if form.is_valid():
            token = form.cleaned_data['token']
            
            if security_profile.verify_2fa_token(token):
                backup_codes = security_profile.generate_backup_codes()
                security_profile.two_factor_enabled = True
                security_profile.save()
                
                request.session['backup_codes'] = backup_codes
                messages.success(request, '2FA has been enabled for your account.')
                return redirect('2fa-backup-codes')
            else:
                messages.error(request, 'Invalid verification code.')
    else:
        form = TwoFactorVerificationForm()
        
        # Generate new secret if none exists
        if not security_profile.two_factor_secret:
            security_profile.generate_2fa_secret()
        
        try:
            # Generate QR code
            uri = security_profile.get_2fa_uri()
            img = qrcode.make(uri, image_factory=qrcode.image.svg.SvgImage)
            buffer = BytesIO()
            img.save(buffer)
            qr_code = base64.b64encode(buffer.getvalue()).decode()
        except Exception as e:
            logger.error(f"QR code generation error: {str(e)}")
            messages.error(request, 'Error generating QR code.')
            return redirect('profile')

    return render(request, 'users/2fa_setup.html', {
        'form': form,
        'qr_code': qr_code,
        'secret': security_profile.two_factor_secret
    })

@login_required
def verify_2fa(request):
    """2FA verification during login"""
    user_id = request.session.get('partial_login_user_id')
    
    if not user_id:
        return redirect('login')
        
    if request.method == 'POST':
        form = TwoFactorVerificationForm(request.POST)
        if form.is_valid():
            token = form.cleaned_data['token']
            security_profile = request.user.usersecurityprofile
            
            if security_profile.verify_2fa_token(token):
                request.session['2fa_verified'] = True
                del request.session['partial_login_user_id']
                messages.success(request, 'Successfully verified!')
                return redirect(request.GET.get('next', 'profile'))
            else:
                messages.error(request, 'Invalid verification code.')
    else:
        form = TwoFactorVerificationForm()
    
    return render(request, 'users/2fa_verify.html', {
        'form': form,
        'show_backup_code_option': True
    })

@login_required
def backup_code_verify(request):
    """Backup code verification as 2FA alternative"""
    user_id = request.session.get('partial_login_user_id')
    
    if not user_id:
        return redirect('login')
    
    if request.method == 'POST':
        form = TwoFactorBackupForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['backup_code']
            security_profile = request.user.usersecurityprofile
            
            if security_profile.verify_backup_code(code):
                request.session['2fa_verified'] = True
                del request.session['partial_login_user_id']
                messages.success(
                    request,
                    'Successfully verified with backup code! Please generate new backup codes.'
                )
                return redirect(request.GET.get('next', 'profile'))
            else:
                messages.error(request, 'Invalid backup code.')
    else:
        form = TwoFactorBackupForm()
    
    return render(request, 'users/backup_code_verify.html', {'form': form})

class BackupCodesView(TemplateView):
    """Display backup codes after 2FA setup"""
    template_name = 'users/backup_codes.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['backup_codes'] = self.request.session.get('backup_codes', [])
        
        if 'backup_codes' in self.request.session:
            del self.request.session['backup_codes']
        
        return context

@login_required
@require_2fa
def disable_2fa(request):
    """Disable 2FA for user account"""
    if request.method == 'POST':
        security_profile = request.user.usersecurityprofile
        security_profile.two_factor_enabled = False
        security_profile.two_factor_secret = None
        security_profile.backup_codes = []
        security_profile.save()
        
        messages.success(request, '2FA has been disabled for your account.')
        return redirect('profile')
    
    return render(request, 'users/2fa_disable.html')