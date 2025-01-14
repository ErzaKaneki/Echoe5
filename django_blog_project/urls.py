from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
import logging

logger = logging.getLogger(__name__)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls')), # This will include all those blog-specific URLs
    path('', include('users.urls')),  # This will include all those user-specific URLs
]

if settings.DEBUG:
    logger.info(f"Setting up static files serving with STATIC_URL: {settings.STATIC_URL}")
    logger.info(f"STATICFILES_DIRS: {settings.STATICFILES_DIRS}")
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)