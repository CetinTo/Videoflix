"""
URL Configuration for Videoflix project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth & User endpoints
    path('api/', include('users.api.urls')),

    # Video endpoints
    path('api/', include('videos.api.urls')),

    # Legal endpoints
    path('api/', include('info.urls')),

    # API Schema & Docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # Django RQ (Task Queue Dashboard)
    path('django-rq/', include('django_rq.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]

admin.site.site_header = 'Videoflix Administration'
admin.site.site_title = 'Videoflix Admin'
admin.site.index_title = 'Willkommen im Videoflix Admin Portal'
