from django.db.models import Avg, Prefetch
from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

import logging
from videos.models import Category, Video, VideoComment, VideoRating

logger = logging.getLogger(__name__)
from api.videos.serializers import (
    CategorySerializer,
    VideoListSerializer,
    VideoListDetailedSerializer,
    VideoDetailSerializer,
    VideoCreateSerializer,
    VideoCommentSerializer,
    VideoRatingSerializer,
    VideoStreamSerializer,
)
from videos.utils import (
    get_original_video_path,
    get_published_video,
    validate_hls_resolution,
    build_m3u8_path,
    serve_m3u8_or_fallback,
    validate_segment_name,
    serve_original_mp4,
    serve_ts_segment,
)


def validate_video_and_resolution(video, resolution):
    """Validate video exists and resolution is valid."""
    invalid_response = validate_hls_resolution(resolution)
    return invalid_response if invalid_response else (video, None)


def get_video_stream_response(movie_id, resolution):
    """Get HLS M3U8 response for video and resolution. Raises Http404 if not found."""
    video = get_published_video(movie_id)
    invalid_response = validate_hls_resolution(resolution)
    if invalid_response:
        return invalid_response
    original_path = get_original_video_path(video)
    if not original_path:
        raise Http404('Video file not found')
    m3u8_path = build_m3u8_path(original_path, resolution)
    response = serve_m3u8_or_fallback(m3u8_path, original_path)
    if not response:
        raise Http404(f'M3U8 not found for {resolution}')
    return response


class VideoHLSView(APIView):
    """Return HLS master playlist (M3U8) for video and resolution."""
    permission_classes = [permissions.AllowAny]

    def get(self, request, movie_id, resolution):
        """Return HLS M3U8 playlist."""
        return get_video_stream_response(movie_id, resolution)


def get_segment_response(movie_id, resolution, segment):
    """Get HLS segment response (original.mp4 or .ts file)."""
    video = get_published_video(movie_id)
    invalid_response = validate_hls_resolution(resolution)
    if invalid_response:
        return invalid_response
    
    validate_segment_name(segment)
    original_path = get_original_video_path(video)
    if not original_path:
        raise Http404('Video file not found')
    
    return serve_original_mp4 if segment == 'original.mp4' else serve_ts_segment


class VideoSegmentView(APIView):
    """Return a single HLS video segment for given video and resolution."""
    permission_classes = [permissions.AllowAny]

    def get(self, request, movie_id, resolution, segment):
        """Return HLS segment (original.mp4 or .ts file)."""
        video = get_published_video(movie_id)
        invalid_response = validate_hls_resolution(resolution)
        if invalid_response:
            return invalid_response
        
        validate_segment_name(segment)
        original_path = get_original_video_path(video)
        if not original_path:
            raise Http404('Video file not found')
        
        if segment == 'original.mp4':
            return serve_original_mp4(request, original_path)
        return serve_ts_segment(original_path, resolution, segment)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only ViewSet for video categories.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'


@extend_schema_view(
    list=extend_schema(description='List all published videos'),
    retrieve=extend_schema(description='Retrieve video details'),
    create=extend_schema(description='Upload a new video (authenticated users only)'),
)
class VideoViewSet(viewsets.ModelViewSet):
    """
    ViewSet for videos. GET /api/video/ returns the list of published videos.
    """
    queryset = Video.objects.filter(status='published')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['categories__slug', 'quality', 'age_rating', 'release_year']
    search_fields = ['title', 'description', 'director', 'cast']
    ordering_fields = ['created_at', 'view_count', 'rating', 'title']
    ordering = ['-created_at']
    lookup_field = 'slug'
    permission_classes = [permissions.AllowAny]  # Liste und Abspielen ohne Login
    pagination_class = None  # Frontend erwartet Array, keine Paginierung
    
    def get_serializer_class(self):
        if self.action == 'list':
            return VideoListSerializer
        elif self.action == 'create':
            return VideoCreateSerializer
        elif self.action == 'stream':
            return VideoStreamSerializer
        return VideoDetailSerializer
    
    def get_serializer_context(self):
        """Fügt request zum Serializer-Context hinzu für absolute URLs"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def list(self, request, *args, **kwargs):
        """Return list of videos as JSON array."""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        """Increment view count when retrieving a video."""
        instance = self.get_object()
        instance.increment_view_count()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def perform_create(self, serializer):
        """Setzt den Uploader automatisch"""
        serializer.save(uploaded_by=self.request.user)
    
    @extend_schema(
        description='Return featured videos for the hero section'
    )
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Returns featured videos for hero section"""
        featured_videos = self.get_queryset().filter(is_featured=True)[:10]
        serializer = VideoListSerializer(featured_videos, many=True, context={'request': request})
        return Response(serializer.data)
    
    @extend_schema(
        description='Return a random featured video for the hero section'
    )
    @action(detail=False, methods=['get'])
    def hero(self, request):
        """Returns random featured video for hero section"""
        hero_video = self.get_queryset().filter(is_featured=True).order_by('?').first()
        if not hero_video:
            hero_video = self.get_queryset().order_by('-view_count').first()
        
        if hero_video:
            serializer = VideoDetailSerializer(hero_video, context={'request': request})
            return Response(serializer.data)
        
        return Response({'detail': 'No videos available'}, status=status.HTTP_404_NOT_FOUND)
    
    @extend_schema(
        description='Gibt die beliebtesten Videos (nach Views) zurück'
    )
    @action(detail=False, methods=['get'])
    def trending(self, request):
        """Return trending videos by view count."""
        trending_videos = self.get_queryset().order_by('-view_count')[:20]
        serializer = VideoListSerializer(trending_videos, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        description='Return HLS stream URLs for all available qualities'
    )
    @action(detail=True, methods=['get'])
    def stream(self, request, slug=None):
        """Return HLS stream URLs for the video."""
        video = self.get_object()
        serializer = VideoStreamSerializer(video)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Return videos grouped by categories for dashboard."""
        categories = Category.objects.prefetch_related(
            Prefetch('videos', queryset=self.get_queryset().order_by('-created_at')[:20])
        )
        
        result = []
        for category in categories:
            if category.videos.exists():
                result.append({
                    'category': CategorySerializer(category).data,
                    'videos': VideoListSerializer(category.videos.all(), many=True, context={'request': request}).data
                })
        
        return Response(result)


class VideoCommentViewSet(viewsets.ModelViewSet):
    """ViewSet für Video-Kommentare (CRUD)."""
    serializer_class = VideoCommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return VideoComment.objects.all().select_related('user', 'video').order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class VideoRatingViewSet(viewsets.ModelViewSet):
    """ViewSet für Video-Bewertungen (CRUD)."""
    serializer_class = VideoRatingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return VideoRating.objects.all().select_related('user', 'video').order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

