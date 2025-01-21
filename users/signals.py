from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile, UserSecurityProfile
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Create a Profile for new users"""
    if created:
        try:
            Profile.objects.create(user=instance, profile_picture='profile_pics/default.png')
            logger.info(f"Created profile for user: {instance.username}")
        except Exception as e:
            logger.error(f"Error creating profile for user {instance.username}: {str(e)}")
            raise

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    """Save Profile changes"""
    try:
        instance.profile.save()
        logger.info(f"Saved profile for user: {instance.username}")
    except Exception as e:
        logger.error(f"Error saving profile for user {instance.username}: {str(e)}")
        raise

@receiver(post_save, sender=User)
def create_security_profile(sender, instance, created, **kwargs):
    """Create a UserSecurityProfile for new users"""
    if created:
        try:
            UserSecurityProfile.objects.create(user=instance)
            logger.info(f"Created security profile for user: {instance.username}")
        except Exception as e:
            logger.error(f"Error creating security profile for user {instance.username}: {str(e)}")
            raise

@receiver(post_save, sender=User)
def save_security_profile(sender, instance, **kwargs):
    """Save UserSecurityProfile changes"""
    try:
        if hasattr(instance, 'usersecurityprofile'):
            instance.usersecurityprofile.save()
            logger.info(f"Saved security profile for user: {instance.username}")
    except Exception as e:
        logger.error(f"Error saving security profile for user {instance.username}: {str(e)}")
        raise