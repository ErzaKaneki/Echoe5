from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class EmailVerifier:
    @staticmethod
    def send_verification_email(user, domain, uid, token):
        """
        Send verification email to user
        """
        try:
            context = {
                'user': user,
                'domain': domain,
                'uid': uid,
                'token': token,
                'protocol': 'https' if not settings.DEBUG else 'http'
            }
            
            # Render email templates
            html_content = render_to_string(
                'users/email/verification_email.html',
                context
            )
            text_content = strip_tags(html_content)
            
            # Create email
            subject = 'Verify your Echoe5 account'
            from_email = settings.EMAIL_HOST_USER
            to_email = user.email
            
            # Create message with both HTML and plain text versions
            msg = EmailMultiAlternatives(
                subject,
                text_content,
                from_email,
                [to_email]
            )
            msg.attach_alternative(html_content, "text/html")
            
            # Send email
            msg.send()
            logger.info(f"Verification email sent to {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending verification email: {str(e)}")
            return False

    @staticmethod
    def verify_token(uidb64, token):
        """
        Verify the email verification token
        """
        try:
            # Decode the user id
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            
            # Verify token and activate user
            if default_token_generator.check_token(user, token):
                user.is_active = True
                user.save()
                logger.info(f"Email verified for user {user.username}")
                return True, user
            
            logger.warning(f"Invalid verification token for user ID {uid}")
            return False, None
            
        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
            logger.error(f"Token verification error: {str(e)}")
            return False, None
        except Exception as e:
            logger.error(f"Unexpected error in token verification: {str(e)}")
            return False, None