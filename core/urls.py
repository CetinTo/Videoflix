"""
URL Configuration for Videoflix project
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
import debug_toolbar
from users.views import (
    UserViewSet,
    UserWatchHistoryViewSet,
    UserFavoriteViewSet,
    LoginView,
    RegisterView,
    ActivateAccountView,
    RefreshTokenView,
    PasswordResetView,
    PasswordResetConfirmView
)
from videos.views import (
    CategoryViewSet,
    VideoViewSet,
    VideoCommentViewSet,
    VideoRatingViewSet,
    VideoHLSView,
    VideoSegmentView
)


# API Router
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'watch-history', UserWatchHistoryViewSet, basename='watch-history')
router.register(r'favorites', UserFavoriteViewSet, basename='favorite')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'video', VideoViewSet, basename='video')  # Singular: /api/video/
router.register(r'comments', VideoCommentViewSet, basename='comment')
router.register(r'ratings', VideoRatingViewSet, basename='rating')


urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Authentication & Registration
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/activate/<str:uidb64>/<str:token>/', ActivateAccountView.as_view(), name='activate'),
    path('api/token/refresh/', RefreshTokenView.as_view(), name='token_refresh_cookie'),
    path('api/password_reset/', PasswordResetView.as_view(), name='password_reset'),
    path('api/password_confirm/<str:uidb64>/<str:token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Legacy JWT
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Legacy JWT
    
    # API Routes
    path('api/', include(router.urls)),
    
    # HLS Streaming
    path('api/video/<int:movie_id>/<str:resolution>/index.m3u8', VideoHLSView.as_view(), name='video_hls'),
    path('api/video/<int:movie_id>/<str:resolution>/<str:segment>/', VideoSegmentView.as_view(), name='video_segment'),
    
    # Django RQ (Task Queue Dashboard)
    path('django-rq/', include('django_rq.urls')),
    
    # API Documentation (Swagger/OpenAPI)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
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
