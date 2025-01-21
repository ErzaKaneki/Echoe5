from django.contrib import admin
from .models import Profile, UserSecurityProfile

admin.site.register(Profile)
admin.site.register(UserSecurityProfile)