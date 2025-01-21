from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile, UserSecurityProfile
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def create_user_profiles(sender, instance, created, **kwargs):
    """Create both Profile and UserSecurityProfile for new users"""
    if created:
        try:
            # Create Profile
            Profile.objects.get_or_create(
                user=instance,
                defaults={'profile_picture': 'profile_pics/default.jpg'}
            )
            logger.info(f"Created Profile for user {instance.username}")
            
            # Create UserSecurityProfile
            UserSecurityProfile.objects.get_or_create(user=instance)
            logger.info(f"Created UserSecurityProfile for user {instance.username}")
            
        except Exception as e:
            logger.error(f"Error creating profiles for user {instance.username}: {str(e)}")
            raise

@receiver(post_save, sender=User)
def save_user_profiles(sender, instance, **kwargs):
    """Save both profiles when user is saved"""
    try:
        instance.profile.save()
        instance.usersecurityprofile.save()
    except Exception as e:
        logger.error(f"Error saving profiles for user {instance.username}: {str(e)}")
        raise