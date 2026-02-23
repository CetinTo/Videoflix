from django.db.models import Avg
from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

import logging
from .models import Category, Video, VideoComment, VideoRating

logger = logging.getLogger(__name__)
from .serializers import (
    CategorySerializer,
    VideoListSerializer,
    VideoListDetailedSerializer,
    VideoDetailSerializer,
    VideoCreateSerializer,
    VideoCommentSerializer,
    VideoRatingSerializer,
    VideoStreamSerializer,
)
from .utils import (
    get_original_video_path,
    get_published_video,
    validate_hls_resolution,
    build_m3u8_path,
    serve_m3u8_or_fallback,
    validate_segment_name,
    serve_original_mp4,
    serve_ts_segment,
)

@extend_schema_view(
    list=extend_schema(description='List all categories'),
    retrieve=extend_schema(description='Retrieve category details'),
)
class VideoHLSView(APIView):
    """
    Return the HLS master playlist (M3U8) for a given video and resolution.

    GET /api/video/<int:movie_id>/<str:resolution>/index.m3u8
    """
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        description='Returns the HLS master playlist (M3U8) for the given video and resolution.',
        responses={
            200: {
                'type': 'string',
                'description': 'HLS-Manifestdatei im M3U8-Format',
                'content': {'application/vnd.apple.mpegurl': {}}
            },
            404: {'description': 'Video or manifest not found'}
        }
    )
    def get(self, request, movie_id, resolution):
        """Return HLS M3U8 playlist for the given video and resolution."""
        video = get_published_video(movie_id)
        invalid_response = validate_hls_resolution(resolution)
        if invalid_response is not None:
            return invalid_response
        original_path = get_original_video_path(video)
        if not original_path:
            raise Http404('Video file not found on disk.')
        m3u8_path = build_m3u8_path(original_path, resolution)
        response = serve_m3u8_or_fallback(m3u8_path, original_path)
        if response is not None:
            return response
        raise Http404(f"M3U8 not found for {resolution}. Video processing may not be complete yet.")


class VideoSegmentView(APIView):
    """
    Return a single HLS video segment for a given video and resolution.

    GET /api/video/<int:movie_id>/<str:resolution>/<str:segment>/
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        description='Returns a single HLS segment (original.mp4 or .ts) for the given video and resolution.',
        responses={
            200: {
                'type': 'string',
                'format': 'binary',
                'description': 'Binary TS or MP4 segment',
                'content': {'video/MP2T': {}}
            },
            404: {'description': 'Video or segment not found'}
        }
    )
    def get(self, request, movie_id, resolution, segment):
        """Return HLS segment (original.mp4 or .ts file) for the given video and resolution."""
        video = get_published_video(movie_id)
        invalid_response = validate_hls_resolution(resolution)
        if invalid_response is not None:
            return invalid_response
        validate_segment_name(segment)
        original_path = get_original_video_path(video)
        if not original_path:
            raise Http404('Video file not found on disk.')
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
        """Return list of videos as JSON array; on error return empty array."""
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            data = list(serializer.data)  # Liste erzwingen, falls Lazy-Evaluation Probleme macht
            return Response(data)
        except Exception as e:
            logger.exception('Video list error: %s', e)
        return Response([], status=status.HTTP_200_OK)
    
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
    
    @extend_schema(
        description='Return videos grouped by category (for dashboard)'
    )
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Returns videos grouped by categories for dashboard"""
        from django.db.models import Prefetch
        
        categories = Category.objects.prefetch_related(
            Prefetch(
                'videos',
                queryset=self.get_queryset().order_by('-created_at')[:20]
            )
        ).all()
        
        result = []
        for category in categories:
            category_videos = category.videos.all()
            if category_videos:
                result.append({
                    'category': CategorySerializer(category).data,
                    'videos': VideoListSerializer(
                        category_videos,
                        many=True,
                        context={'request': request}
                    ).data
                })
        
        return Response(result)
    
    @extend_schema(
        description='Returns HLS stream URLs for video playback in all available qualities',
        responses={200: VideoStreamSerializer}
    )
    @action(detail=True, methods=['get'], url_path='stream')
    def stream(self, request, pk=None):
        """Returns HLS streaming URLs for video player"""
        video = self.get_object()
        serializer = VideoStreamSerializer(video, context={'request': request})
        return Response(serializer.data)
    
    @extend_schema(
        description='Gibt ähnliche Videos basierend auf Kategorien zurück'
    )
    @action(detail=True, methods=['get'])
    def similar(self, request, slug=None):
        """Gibt ähnliche Videos zurück"""
        video = self.get_object()
        similar_videos = Video.objects.filter(
            categories__in=video.categories.all(),
            status='published'
        ).exclude(id=video.id).distinct()[:10]
        
        serializer = VideoListSerializer(similar_videos, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(description='List comments for a video'),
    create=extend_schema(description='Add a comment to a video'),
    update=extend_schema(description='Update a comment'),
    destroy=extend_schema(description='Delete a comment'),
)
class VideoCommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for video comments.
    """
    serializer_class = VideoCommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """Filter comments by video (query param video_slug)."""
        video_slug = self.request.query_params.get('video_slug')
        if video_slug:
            return VideoComment.objects.filter(video__slug=video_slug)
        return VideoComment.objects.all()

    def perform_create(self, serializer):
        """Set the current user as comment author."""
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """Mark comment as edited."""
        serializer.save(is_edited=True)


@extend_schema_view(
    list=extend_schema(description='List ratings for a video'),
    create=extend_schema(description='Add a rating to a video'),
    update=extend_schema(description='Update a rating'),
)
class VideoRatingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for video ratings.
    """
    serializer_class = VideoRatingSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'patch']

    def get_queryset(self):
        """Filter ratings by video (query param video_slug)."""
        video_slug = self.request.query_params.get('video_slug')
        if video_slug:
            return VideoRating.objects.filter(video__slug=video_slug)
        return VideoRating.objects.all()
    
    def perform_create(self, serializer):
        """Set current user and update video average rating."""
        rating = serializer.save(user=self.request.user)
        self._update_video_rating(rating.video)

    def perform_update(self, serializer):
        """Update video average rating after rating change."""
        rating = serializer.save()
        self._update_video_rating(rating.video)

    def _update_video_rating(self, video):
        """Recalculate and save the video's average rating."""
        avg_rating = video.ratings.aggregate(Avg('rating'))['rating__avg']
        if avg_rating:
            video.rating = round(avg_rating, 2)
            video.save(update_fields=['rating'])
    
    @extend_schema(
        description='Return the current user\'s rating for a video'
    )
    @action(detail=False, methods=['get'])
    def my_rating(self, request):
        """Return the current user's rating for the given video_slug."""
        video_slug = request.query_params.get('video_slug')
        
        if not video_slug:
            return Response(
                {'error': 'video_slug Parameter erforderlich'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            rating = VideoRating.objects.get(
                user=request.user,
                video__slug=video_slug
            )
            serializer = self.get_serializer(rating)
            return Response(serializer.data)
        except VideoRating.DoesNotExist:
            return Response(
                {'message': 'No rating found'},
                status=status.HTTP_404_NOT_FOUND
            )
