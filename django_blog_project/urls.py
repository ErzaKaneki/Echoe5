from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
import logging

logger = logging.getLogger(__name__)

schema_view = get_schema_view(
    openapi.Info(
        title="Blog API",
        default_version='v1',
        description="API documentation for the blog application",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls')), # This will include all those blog-specific URLs
    path('', include('users.urls')),  # This will include all those user-specific URLs
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0)),
    path('redoc/', schema_view.with_ui('redoc', cache_tiemout=0)),
]

if settings.DEBUG:
    logger.info(f"Setting up static files serving with STATIC_URL: {settings.STATIC_URL}")
    logger.info(f"STATICFILES_DIRS: {settings.STATICFILES_DIRS}")
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)