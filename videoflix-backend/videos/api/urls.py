from django.urls import path, include
from rest_framework.routers import DefaultRouter

from videos.api.views import (
    CategoryViewSet,
    VideoViewSet,
    VideoCommentViewSet,
    VideoRatingViewSet,
    VideoHLSView,
    VideoSegmentView,
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'video', VideoViewSet, basename='video')
router.register(r'comments', VideoCommentViewSet, basename='comment')
router.register(r'ratings', VideoRatingViewSet, basename='rating')

urlpatterns = [
    # HLS streaming (vor Router, damit video/1/480p/index.m3u8 nicht vom VideoViewSet abgefangen wird)
    path('video/<int:movie_id>/<str:resolution>/index.m3u8', VideoHLSView.as_view(), name='video_hls'),
    path('video/<int:movie_id>/<str:resolution>/<str:segment>', VideoSegmentView.as_view(), name='video_segment'),
    path('', include(router.urls)),
]
