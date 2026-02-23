from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, VideoViewSet, VideoCommentViewSet, VideoRatingViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'videos', VideoViewSet, basename='video')
router.register(r'comments', VideoCommentViewSet, basename='comment')
router.register(r'ratings', VideoRatingViewSet, basename='rating')

app_name = 'videos'

urlpatterns = [
    path('', include(router.urls)),
]
