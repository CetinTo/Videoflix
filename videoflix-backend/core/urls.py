"""
URL Configuration for Videoflix project.

Non-API URLs bleiben hier, alle API-spezifischen Routen liegen in ``api.urls``.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
import debug_toolbar


urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Zentrale API-Routen (auth, videos, legal, docs, etc.)
    path('api/', include('api.urls')),

    # Django RQ (Task Queue Dashboard)
    path('django-rq/', include('django_rq.urls')),
]

# Static und Media Files in Development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # Django Debug Toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]

# Admin Site Customization
admin.site.site_header = 'Videoflix Administration'
admin.site.site_title = 'Videoflix Admin'
admin.site.index_title = 'Willkommen im Videoflix Admin Portal'
