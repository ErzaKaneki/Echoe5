from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.core.exceptions import ValidationError
from .models import Profile
import re
import logging

logger = logging.getLogger(__name__)

class UserRegisterForm(UserCreationForm):
    """Enhanced user registration form with additional validation"""
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def clean_password1(self):
        """Validate password complexity requirements"""
        password = self.cleaned_data.get('password1')
        
        if not password:
            raise ValidationError('Password is required.')
            
        # Length check
        if len(password) < 12:
            logger.warning("Password length requirement not met")
            raise ValidationError('Password must be at least 12 characters long.')
            
        # Complexity requirements
        if not re.search(r'[A-Z]', password):
            logger.warning("Password uppercase requirement not met")
            raise ValidationError('Password must contain at least one uppercase letter.')
        if not re.search(r'[a-z]', password):
            logger.warning("Password lowercase requirement not met")
            raise ValidationError('Password must contain at least one lowercase letter.')
        if not re.search(r'[0-9]', password):
            logger.warning("Password number requirement not met")
            raise ValidationError('Password must contain at least one number.')
        if not re.search(r'[!@#$%^&*(),._?":{}|<>]', password):
            logger.warning("Password special character requirement not met")
            raise ValidationError('Password must contain at least one special character.')
            
        # Check for common patterns
        common_patterns = [
            r'\b(123|321|abc|cba|password|qwerty|admin)\b',
        ]
        
        username = self.cleaned_data.get('username', '')
        email = self.cleaned_data.get('email', '').split('@')[0] if self.cleaned_data.get('email') else ''
        
        if username:
            common_patterns.append(re.escape(username))
        if email:
            common_patterns.append(re.escape(email))
        
        for pattern in common_patterns:
            if re.search(pattern, password.lower()):
                logger.warning("Password contains common pattern or personal info")
                raise ValidationError('Password contains common patterns or personal information.')
        
        logger.info("Password complexity validation successful")
        return password

    def clean_email(self):
        """Validate email uniqueness and format"""
        email = self.cleaned_data.get('email')
        
        if not email:
            raise ValidationError('Email is required.')
        
        # Check for existing email
        if User.objects.filter(email=email).exists():
            logger.warning(f"Registration attempt with existing email: {email}")
            raise ValidationError('This email is already registered.')
        
        # Additional email validation
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            logger.warning(f"Invalid email format attempt: {email}")
            raise ValidationError('Please enter a valid email address.')
        
        # Check for disposable email providers
        disposable_domains = ['tempmail.com', 'throwaway.com']  # Add more as needed
        domain = email.split('@')[1]
        if domain in disposable_domains:
            logger.warning(f"Registration attempt with disposable email domain: {domain}")
            raise ValidationError('Disposable email addresses are not allowed.')
        
        logger.info(f"Email validation successful for: {email}")
        return email

class UserUpdateForm(forms.ModelForm):
    """Form for updating user information"""
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username', 'email']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.original_email = self.instance.email
    
    def clean_email(self):
        """Validate email changes"""
        email = self.cleaned_data.get('email')
        
        if not email:
            raise ValidationError('Email is required.')
        
        # Only check for uniqueness if email has changed
        if email != self.original_email:
            if User.objects.filter(email=email).exists():
                logger.warning(f"Update attempt with existing email: {email}")
                raise ValidationError('This email is already registered.')
                
            # Additional email validation
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                logger.warning(f"Invalid email format in update: {email}")
                raise ValidationError('Please enter a valid email address.')
            
            # Check for disposable email providers
            disposable_domains = ['tempmail.com', 'throwaway.com']
            domain = email.split('@')[1]
            if domain in disposable_domains:
                logger.warning(f"Update attempt with disposable email domain: {domain}")
                raise ValidationError('Disposable email addresses are not allowed.')
        
        logger.info(f"Email update validation successful for: {email}")
        return email

class ProfileUpdateForm(forms.ModelForm):
    """Form for updating profile information"""
    class Meta:
        model = Profile
        fields = ['profile_picture']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['profile_picture'].widget.attrs.update({
            'class': 'form-control',
            'accept': 'image/*'
        })
        self.fields['profile_picture'].help_text = 'Upload an image (max 5MB). Allowed formats: PNG, JPG, JPEG'
    
    def clean_profile_picture(self):
        """Validate profile picture uploads"""
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture:
            # Check file size
            if profile_picture.size > 5 * 1024 * 1024:  # 5MB limit
                logger.warning(f"Profile picture upload exceeds size limit: {profile_picture.size} bytes")
                raise ValidationError('Image file size must be less than 5MB.')
            
            # Check file type
            allowed_types = ['image/jpeg', 'image/png', 'image/jpg']
            if profile_picture.content_type not in allowed_types:
                logger.warning(f"Invalid profile picture type attempted: {profile_picture.content_type}")
                raise ValidationError('Only JPEG, JPG, and PNG files are allowed.')
            
            logger.info("Profile picture validation successful")
        return profile_picture

class TwoFactorVerificationForm(forms.Form):
    """Form for 2FA token verification"""
    token = forms.CharField(
        max_length=6,
        min_length=6,
        required=True,
        widget=forms.TextInput(attrs={
            'type': 'number',
            'class': 'form-control',
            'placeholder': 'Enter 6-digit code',
            'autocomplete': 'off'
        })
    )
    
    def clean_token(self):
        """Validate 2FA token format"""
        token = self.cleaned_data.get('token')
        
        if not token:
            raise ValidationError('Token is required.')
            
        # Check if token is numeric
        if not token.isdigit():
            logger.warning("Invalid 2FA token format attempted")
            raise ValidationError('Token must contain only numbers.')
            
        return token

class TwoFactorBackupForm(forms.Form):
    """Form for 2FA backup code verification"""
    backup_code = forms.CharField(
        max_length=8,
        min_length=8,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter backup code',
            'autocomplete': 'off'
        })
    )
    
    def clean_backup_code(self):
        """Validate backup code format"""
        code = self.cleaned_data.get('backup_code')
        
        if not code:
            raise ValidationError('Backup code is required.')
            
        # Check if code contains valid characters
        if not re.match(r'^[A-Z2-7]+$', code):
            logger.warning("Invalid backup code format attempted")
            raise ValidationError('Invalid backup code format.')
            
        return code

class SecurityPreferencesForm(forms.Form):
    """Form for managing security preferences"""
    notify_on_login = forms.BooleanField(
        required=False,
        label='Notify me of new login attempts'
    )
    require_2fa = forms.BooleanField(
        required=False,
        label='Require 2FA for all logins'
    )
    auto_logout_time = forms.ChoiceField(
        choices=[
            (15, '15 minutes'),
            (30, '30 minutes'),
            (60, '1 hour'),
            (120, '2 hours')
        ],
        label='Auto-logout after inactivity'
    )

class EnhancedPasswordChangeForm(PasswordChangeForm):
    """Enhanced password change form with additional validation"""
    def clean_new_password1(self):
        """Validate new password complexity"""
        password = self.cleaned_data.get('new_password1')
        
        if not password:
            raise ValidationError('New password is required.')
            
        # Length check
        if len(password) < 12:
            logger.warning("Password change length requirement not met")
            raise ValidationError('Password must be at least 12 characters long.')
            
        # Complexity requirements
        if not re.search(r'[A-Z]', password):
            logger.warning("Password change uppercase requirement not met")
            raise ValidationError('Password must contain at least one uppercase letter.')
        if not re.search(r'[a-z]', password):
            logger.warning("Password change lowercase requirement not met")
            raise ValidationError('Password must contain at least one lowercase letter.')
        if not re.search(r'[0-9]', password):
            logger.warning("Password change number requirement not met")
            raise ValidationError('Password must contain at least one number.')
        if not re.search(r'[!@#$%^&*(),._?":{}|<>]', password):
            logger.warning("Password change special character requirement not met")
            raise ValidationError('Password must contain at least one special character.')
        
        # Check for similarity with old password
        if self.user.check_password(password):
            logger.warning("Password change attempted with same password")
            raise ValidationError('New password cannot be the same as your current password.')
        
        return password