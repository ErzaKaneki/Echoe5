from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.core.validators import MinLengthValidator
from django.utils import timezone
from django.conf import settings
from PIL import Image
import secrets
import boto3
import io
import os
import sys
import pyotp
import logging

logger = logging.getLogger(__name__)
IS_DEVELOPMENT = 'dev' in sys.prefix.lower()

class Profile(models.Model):
    """User profile model with auto-resizing profile picture"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(
        default='profile_pics/default.png',
        upload_to='profile_pics'
    )

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        """Save profile and process profile picture if it exists"""
        super().save(*args, **kwargs)

        if self.profile_picture and self.profile_picture.name != 'profile_pics/default.png':
            try:
                if IS_DEVELOPMENT:
                    # Local development handling
                    image_path = os.path.join(settings.MEDIA_ROOT, self.profile_picture.name)
                    with Image.open(self.profile_picture.path) as img:
                        if img.height > 300 or img.width > 300:
                            output_size = (300, 300)
                            img.thumbnail(output_size)
                            img.save(self.profile_picture.path)
                            logger.info(f"Resized profile picture locally for user {self.user.username}")
                else:
                    # Production S3 handling
                    s3_file = default_storage.open(self.profile_picture.name, 'rb')
                    with Image.open(s3_file) as img:
                        if img.height > 300 or img.width > 300:
                            output_size = (300, 300)
                            img.thumbnail(output_size)
                            
                            # Save the resized image to bytes buffer
                            buffer = io.BytesIO()
                            img.save(buffer, format=img.format)
                            buffer.seek(0)
                            
                            # Upload resized image back to S3
                            default_storage.save(self.profile_picture.name, buffer)
                            logger.info(f"Resized and uploaded profile picture to S3 for user {self.user.username}")
                    
                    s3_file.close()

            except Exception as e:
                logger.error(f"Error processing profile picture for user {self.user.username}: {str(e)}")


class UserSecurityProfile(models.Model):
    """Security profile for managing 2FA and account security settings"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    api_key = models.CharField(max_length=64, blank=True, null=True, unique=True)
    
    # Two-Factor Authentication fields
    two_factor_secret = models.CharField(max_length=32, blank=True, null=True)
    two_factor_enabled = models.BooleanField(default=False)
    backup_codes = models.JSONField(default=list, blank=True)
    
    # Account security fields
    failed_login_attempts = models.IntegerField(default=0)
    last_failed_login = models.DateTimeField(null=True, blank=True)
    account_locked_until = models.DateTimeField(null=True, blank=True)
    password_last_changed = models.DateTimeField(auto_now_add=True)
    
    # Security preferences
    require_password_change = models.BooleanField(default=False)
    notify_on_login = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "User Security Profile"
        verbose_name_plural = "User Security Profiles"

    def __str__(self):
        return f"{self.user.username}'s Security Profile"

    def generate_api_key(self):
        """Generate a new API key for the user"""
        try:
            self.api_key = secrets.token_urlsafe(32)
            self.save()
            logger.info(f"Generated new API key for user {self.user.username}")
            return self.api_key
        except Exception as e:
            logger.error(f"Error generating API key: {str(e)}")
            raise

    def generate_2fa_secret(self):
        """Generate a new 2FA secret key"""
        try:
            self.two_factor_secret = pyotp.random_base32()
            self.save()
            logger.info(f"Generated new 2FA secret for user {self.user.username}")
            return self.two_factor_secret
        except Exception as e:
            logger.error(f"Error generating 2FA secret: {str(e)}")
            raise

    def verify_2fa_token(self, token):
        """Verify a 2FA token"""
        if not self.two_factor_secret:
            return False
        try:
            totp = pyotp.TOTP(self.two_factor_secret)
            is_valid = totp.verify(token)
            if is_valid:
                logger.info(f"Successful 2FA verification for user {self.user.username}")
            else:
                logger.warning(f"Failed 2FA verification for user {self.user.username}")
            return is_valid
        except Exception as e:
            logger.error(f"Error verifying 2FA token: {str(e)}")
            return False

    def get_2fa_uri(self):
        """Get the URI for QR code generation"""
        if not self.two_factor_secret:
            return None
        try:
            totp = pyotp.TOTP(self.two_factor_secret)
            return totp.provisioning_uri(
                self.user.email,
                issuer_name="Echoe5"
            )
        except Exception as e:
            logger.error(f"Error generating 2FA URI: {str(e)}")
            return None

    def generate_backup_codes(self, count=8):
        """Generate new backup codes for 2FA recovery"""
        try:
            codes = []
            for _ in range(count):
                code = pyotp.random_base32()[:8]
                codes.append(code)
            self.backup_codes = codes
            self.save()
            logger.info(f"Generated new backup codes for user {self.user.username}")
            return codes
        except Exception as e:
            logger.error(f"Error generating backup codes: {str(e)}")
            raise

    def verify_backup_code(self, code):
        """Verify and consume a backup code"""
        try:
            if code in self.backup_codes:
                self.backup_codes.remove(code)
                self.save()
                logger.info(f"Backup code used for user {self.user.username}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error verifying backup code: {str(e)}")
            return False

    def record_failed_login(self):
        """Record a failed login attempt and handle account lockout"""
        try:
            self.failed_login_attempts += 1
            self.last_failed_login = timezone.now()
            
            # Lock account after 5 failed attempts
            if self.failed_login_attempts >= 5:
                self.account_locked_until = timezone.now() + timezone.timedelta(minutes=30)
                logger.warning(
                    f"Account locked for user {self.user.username} due to multiple failed attempts"
                )
            
            self.save()
        except Exception as e:
            logger.error(f"Error recording failed login: {str(e)}")
            raise

    def reset_login_attempts(self):
        """Reset failed login attempts after successful login"""
        try:
            self.failed_login_attempts = 0
            self.last_failed_login = None
            self.account_locked_until = None
            self.save()
            logger.info(f"Reset login attempts for user {self.user.username}")
        except Exception as e:
            logger.error(f"Error resetting login attempts: {str(e)}")
            raise

    def is_account_locked(self):
        """Check if the account is currently locked"""
        if not self.account_locked_until:
            return False
        is_locked = timezone.now() < self.account_locked_until
        if not is_locked:
            # Reset if lock has expired
            self.reset_login_attempts()
        return is_locked

    def should_change_password(self):
        """Check if password change is required (e.g., every 90 days)"""
        if self.require_password_change:
            return True
        days_since_change = (timezone.now() - self.password_last_changed).days
        return days_since_change >= 90