from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, UserWatchHistoryViewSet, UserFavoriteViewSet

router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')
router.register(r'watch-history', UserWatchHistoryViewSet, basename='watch-history')
router.register(r'favorites', UserFavoriteViewSet, basename='favorite')

app_name = 'users'

urlpatterns = [
    path('', include(router.urls)),
]
