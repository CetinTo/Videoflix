from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.api.views import (
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

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'watch-history', UserWatchHistoryViewSet, basename='watch-history')
router.register(r'favorites', UserFavoriteViewSet, basename='favorite')

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('activate/<str:uidb64>/<str:token>/', ActivateAccountView.as_view(), name='activate'),
    path('token/refresh/', RefreshTokenView.as_view(), name='token_refresh_cookie'),
    path('password_reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password_confirm/<str:uidb64>/<str:token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('', include(router.urls)),
]
