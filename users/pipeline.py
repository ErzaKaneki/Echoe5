from social_core.pipeline.partial import partial
from django.shortcuts import redirect

@partial
def require_email_validation(strategy, backend, user, is_new=False, *args, **kwargs):
    if is_new and not user.email:
        email = kwargs.get('details', {}).get('email')
        if not email:
            return redirect('email_verification_required')
        user.email = email
        user.save()