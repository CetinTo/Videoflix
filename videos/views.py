from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from django.db.models import Avg
from django.http import HttpResponse, Http404, FileResponse
from django.shortcuts import get_object_or_404
import os
import mimetypes
from pathlib import Path
from .models import Category, Video, VideoComment, VideoRating
from .serializers import (
    CategorySerializer,
    VideoListSerializer,
    VideoListDetailedSerializer,
    VideoDetailSerializer,
    VideoCreateSerializer,
    VideoCommentSerializer,
    VideoRatingSerializer,
    VideoStreamSerializer
)


@extend_schema_view(
    list=extend_schema(description='Listet alle Kategorien auf'),
    retrieve=extend_schema(description='Ruft Kategorie-Details ab'),
)
class VideoHLSView(APIView):
    """
    Gibt die HLS-Master-Playlist für einen bestimmten Film und eine gewählte Auflösung zurück
    
    GET /api/video/<int:movie_id>/<str:resolution>/index.m3u8
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        description='Gibt die HLS-Master-Playlist für einen bestimmten Film und eine gewählte Auflösung zurück. JWT-Authentifizierung erforderlich.',
        responses={
            200: {
                'type': 'string',
                'description': 'HLS-Manifestdatei im M3U8-Format',
                'content': {'application/vnd.apple.mpegurl': {}}
            },
            404: {'description': 'Video oder Manifest nicht gefunden'}
        }
    )
    def get(self, request, movie_id, resolution):
        """
        Gibt HLS M3U8 Playlist zurück (aus dem hls_XXXp Verzeichnis)
        
        Args:
            movie_id: Die ID des Films
            resolution: Gewünschte Auflösung (360p, 480p, 720p, 1080p)
        """
        # Hole Video
        try:
            video = Video.objects.get(id=movie_id, status='published')
        except Video.DoesNotExist:
            raise Http404('Video not found')
        
        # Validiere Auflösung
        valid_resolutions = ['360p', '480p', '720p', '1080p']
        if resolution not in valid_resolutions:
            return Response(
                {'error': f'Invalid resolution. Valid options: {", ".join(valid_resolutions)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Pfad zur M3U8 Datei (aus dem hls_XXXp Verzeichnis)
        video_dir = os.path.dirname(video.original_video.path)
        hls_dir = os.path.join(video_dir, f'hls_{resolution}')
        m3u8_path = os.path.join(hls_dir, 'index.m3u8')
        
        if not os.path.exists(m3u8_path):
            raise Http404(f"M3U8 file not found for {resolution}. Video processing may not be complete yet.")
        
        # M3U8 Datei lesen und zurückgeben
        try:
            with open(m3u8_path, 'r') as f:
                content = f.read()
            
            response = HttpResponse(content, content_type='application/vnd.apple.mpegurl')
            response['Content-Disposition'] = f'inline; filename="index.m3u8"'
            return response
            
        except Exception as e:
            return Response(
                {'error': f'Error reading M3U8 file: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VideoSegmentView(APIView):
    """
    Gibt ein einzelnes HLS-Videosegment für einen bestimmten Film zurück
    
    GET /api/video/<int:movie_id>/<str:resolution>/<str:segment>/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        description='Gibt ein einzelnes HLS-Videosegment für einen bestimmten Film in gewählter Auflösung zurück. JWT-Authentifizierung erforderlich.',
        responses={
            200: {
                'type': 'string',
                'format': 'binary',
                'description': 'Binäre TS-Datei',
                'content': {'video/MP2T': {}}
            },
            404: {'description': 'Video oder Segment nicht gefunden'}
        }
    )
    def get(self, request, movie_id, resolution, segment):
        """
        Gibt HLS .ts Segment zurück
        
        Args:
            movie_id: ID des Films
            resolution: Gewünschte Auflösung (360p, 480p, 720p, 1080p)
            segment: Dateiname des Segments (z.B. '000.ts', '001.ts')
        """
        # Hole Video
        try:
            video = Video.objects.get(id=movie_id, status='published')
        except Video.DoesNotExist:
            raise Http404('Video not found')
        
        # Validiere Auflösung
        valid_resolutions = ['360p', '480p', '720p', '1080p']
        if resolution not in valid_resolutions:
            return Response(
                {'error': f'Invalid resolution. Valid options: {", ".join(valid_resolutions)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validiere Segment-Dateiname (Sicherheit)
        if not segment.endswith('.ts'):
            raise Http404('Invalid segment format')
        
        # Sicherheit: Verhindere Path Traversal
        if '..' in segment or '/' in segment or '\\' in segment:
            raise Http404('Invalid segment name')
        
        # Pfad zum Segment (aus dem hls_XXXp Verzeichnis)
        video_dir = os.path.dirname(video.original_video.path)
        hls_dir = os.path.join(video_dir, f'hls_{resolution}')
        segment_path = os.path.join(hls_dir, segment)
        
        # Prüfe ob Segment existiert
        if not os.path.exists(segment_path):
            raise Http404(f"Segment '{segment}' not found for {resolution}")
        
        # Gebe Segment-Datei zurück
        try:
            response = FileResponse(
                open(segment_path, 'rb'),
                content_type='video/MP2T'
            )
            response['Content-Disposition'] = f'inline; filename="{segment}"'
            response['Accept-Ranges'] = 'bytes'
            
            return response
            
        except IOError:
            raise Http404('Error reading segment file')


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet für Kategorien (nur Lesen)
    
    Bietet Zugriff auf Video-Kategorien
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'


@extend_schema_view(
    list=extend_schema(description='Gibt eine Liste aller verfügbaren Videos zurück. JWT-Authentifizierung erforderlich.'),
    retrieve=extend_schema(description='Ruft Video-Details ab'),
    create=extend_schema(description='Lädt ein neues Video hoch (nur authentifizierte Benutzer)'),
)
class VideoViewSet(viewsets.ModelViewSet):
    """
    ViewSet für Videos
    
    GET /api/video/ - Gibt eine Liste aller verfügbaren Videos zurück
    """
    queryset = Video.objects.filter(status='published')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['categories__slug', 'quality', 'age_rating', 'release_year']
    search_fields = ['title', 'description', 'director', 'cast']
    ordering_fields = ['created_at', 'view_count', 'rating', 'title']
    ordering = ['-created_at']
    lookup_field = 'slug'
    permission_classes = [permissions.IsAuthenticated]  # JWT-Authentifizierung erforderlich
    
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
    
    def retrieve(self, request, *args, **kwargs):
        """Erhöht View Count beim Abrufen eines Videos"""
        instance = self.get_object()
        instance.increment_view_count()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def perform_create(self, serializer):
        """Setzt den Uploader automatisch"""
        serializer.save(uploaded_by=self.request.user)
    
    @extend_schema(
        description='Gibt Featured Videos zurück (hervorgehobene Videos für Hero-Bereich)'
    )
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Returns featured videos for hero section"""
        featured_videos = self.get_queryset().filter(is_featured=True)[:10]
        serializer = VideoListSerializer(featured_videos, many=True, context={'request': request})
        return Response(serializer.data)
    
    @extend_schema(
        description='Gibt ein zufälliges hervorgehobenes Video für den Hero-Bereich zurück'
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
        """Gibt die beliebtesten Videos zurück"""
        trending_videos = self.get_queryset().order_by('-view_count')[:20]
        serializer = VideoListSerializer(trending_videos, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        description='Gibt Video-Stream-URLs zurück (verschiedene Qualitäten)'
    )
    @action(detail=True, methods=['get'])
    def stream(self, request, slug=None):
        """Gibt Video-Stream-URLs zurück"""
        video = self.get_object()
        serializer = VideoStreamSerializer(video)
        return Response(serializer.data)
    
    @extend_schema(
        description='Gibt Videos gruppiert nach Genres/Kategorien zurück (für Dashboard)'
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
    list=extend_schema(description='Listet Kommentare für ein Video auf'),
    create=extend_schema(description='Fügt einen Kommentar zu einem Video hinzu'),
    update=extend_schema(description='Aktualisiert einen Kommentar'),
    destroy=extend_schema(description='Löscht einen Kommentar'),
)
class VideoCommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet für Video-Kommentare
    
    Verwaltet Kommentare zu Videos
    """
    serializer_class = VideoCommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """Filtert Kommentare nach Video"""
        video_slug = self.request.query_params.get('video_slug')
        if video_slug:
            return VideoComment.objects.filter(video__slug=video_slug)
        return VideoComment.objects.all()
    
    def perform_create(self, serializer):
        """Setzt den Benutzer automatisch"""
        serializer.save(user=self.request.user)
    
    def perform_update(self, serializer):
        """Markiert Kommentar als bearbeitet"""
        serializer.save(is_edited=True)


@extend_schema_view(
    list=extend_schema(description='Listet Bewertungen für ein Video auf'),
    create=extend_schema(description='Fügt eine Bewertung zu einem Video hinzu'),
    update=extend_schema(description='Aktualisiert eine Bewertung'),
)
class VideoRatingViewSet(viewsets.ModelViewSet):
    """
    ViewSet für Video-Bewertungen
    
    Verwaltet Bewertungen für Videos
    """
    serializer_class = VideoRatingSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'patch']  # Kein DELETE
    
    def get_queryset(self):
        """Filtert Bewertungen nach Video"""
        video_slug = self.request.query_params.get('video_slug')
        if video_slug:
            return VideoRating.objects.filter(video__slug=video_slug)
        return VideoRating.objects.all()
    
    def perform_create(self, serializer):
        """Setzt den Benutzer automatisch und aktualisiert Video-Rating"""
        rating = serializer.save(user=self.request.user)
        self._update_video_rating(rating.video)
    
    def perform_update(self, serializer):
        """Aktualisiert Video-Rating nach Änderung"""
        rating = serializer.save()
        self._update_video_rating(rating.video)
    
    def _update_video_rating(self, video):
        """Berechnet durchschnittliche Bewertung für ein Video"""
        avg_rating = video.ratings.aggregate(Avg('rating'))['rating__avg']
        if avg_rating:
            video.rating = round(avg_rating, 2)
            video.save(update_fields=['rating'])
    
    @extend_schema(
        description='Gibt die Bewertung des aktuellen Benutzers für ein Video zurück'
    )
    @action(detail=False, methods=['get'])
    def my_rating(self, request):
        """Gibt die Bewertung des aktuellen Benutzers zurück"""
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
                {'message': 'Keine Bewertung gefunden'},
                status=status.HTTP_404_NOT_FOUND
            )
