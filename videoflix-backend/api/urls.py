"""
Central API URL configuration for Videoflix.

All API endpoints (auth, videos, legal, docs, etc.) are collected here.
The project root routes include this module under the ``/api/`` prefix.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from api.users.views import (
    UserViewSet,
    UserWatchHistoryViewSet,
    UserFavoriteViewSet,
    LoginView,
    LogoutView,
    RegisterView,
    ActivateAccountView,
    RefreshTokenView,
    PasswordResetView,
    PasswordResetConfirmView,
)
from api.videos.views import (
    CategoryViewSet,
    VideoViewSet,
    VideoCommentViewSet,
    VideoRatingViewSet,
    VideoHLSView,
    VideoSegmentView,
)
from api.info.views import LegalPageViewSet


# DRF router for REST resources
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'watch-history', UserWatchHistoryViewSet, basename='watch-history')
router.register(r'favorites', UserFavoriteViewSet, basename='favorite')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'video', VideoViewSet, basename='video')
router.register(r'comments', VideoCommentViewSet, basename='comment')
router.register(r'ratings', VideoRatingViewSet, basename='rating')
router.register(r'legal', LegalPageViewSet, basename='legal')


urlpatterns = [
    # Auth & registration (cookie-based JWT)
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('activate/<str:uidb64>/<str:token>/', ActivateAccountView.as_view(), name='activate'),
    path('token/refresh/', RefreshTokenView.as_view(), name='token_refresh_cookie'),
    path('password_reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password_confirm/<str:uidb64>/<str:token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    # Legacy JWT endpoints (not cookie-based)
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # HLS streaming (vor Router, damit video/1/480p/index.m3u8 nicht vom VideoViewSet abgefangen wird)
    path('video/<int:movie_id>/<str:resolution>/index.m3u8', VideoHLSView.as_view(), name='video_hls'),
    path('video/<int:movie_id>/<str:resolution>/<str:segment>', VideoSegmentView.as_view(), name='video_segment'),

    # REST resources
    path('', include(router.urls)),

    # API schema & docs
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

