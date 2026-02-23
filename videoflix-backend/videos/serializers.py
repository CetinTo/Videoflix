import os
from rest_framework import serializers
from .models import Category, Video, VideoComment, VideoRating


class CategorySerializer(serializers.ModelSerializer):
    """Serializer für Kategorien"""
    
    video_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'video_count', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_video_count(self, obj):
        """Gibt die Anzahl der Videos in dieser Kategorie zurück"""
        return obj.videos.filter(status='published').count()


class VideoListSerializer(serializers.ModelSerializer):
    """Serializer für Video-Liste (API-Spezifikation)"""
    
    thumbnail_url = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = [
            'id',
            'created_at',
            'title',
            'description',
            'thumbnail_url',
            'category'
        ]
        read_only_fields = ['id', 'created_at']
    
    _PLACEHOLDER_IMG = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"

    def get_thumbnail_url(self, obj):
        """Thumbnail-URL nur wenn Datei existiert, sonst Platzhalter – so werden Thumbnails immer angezeigt."""
        try:
            if obj.thumbnail:
                path = getattr(obj.thumbnail, 'path', None)
                if path and os.path.exists(path):
                    request = self.context.get('request')
                    if request:
                        return request.build_absolute_uri(obj.thumbnail.url)
                    return obj.thumbnail.url
        except Exception:
            pass
        return self._PLACEHOLDER_IMG

    def get_category(self, obj):
        """Gibt die erste Kategorie zurück (singular). Wirft nie."""
        try:
            first = obj.categories.first()
            return first.name if first else ""
        except Exception:
            return ""


class VideoListDetailedSerializer(serializers.ModelSerializer):
    """Serializer für Video-Liste (erweiterte Ansicht)"""
    
    categories = CategorySerializer(many=True, read_only=True)
    formatted_duration = serializers.ReadOnlyField()

    class Meta:
        model = Video
        fields = [
            'id', 'title', 'slug', 'description', 'thumbnail',
            'categories', 'duration', 'formatted_duration', 'quality',
            'view_count', 'rating', 'is_featured', 'age_rating',
            'release_year', 'created_at'
        ]
        read_only_fields = ['id', 'view_count', 'rating', 'created_at']


class VideoDetailSerializer(serializers.ModelSerializer):
    """Serializer für Video-Details (vollständige Ansicht)"""
    
    categories = CategorySerializer(many=True, read_only=True)
    formatted_duration = serializers.ReadOnlyField()
    formatted_file_size = serializers.ReadOnlyField()
    comment_count = serializers.SerializerMethodField()
    rating_count = serializers.SerializerMethodField()
    uploaded_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = [
            'id', 'title', 'slug', 'description', 'categories',
            'original_video', 'video_360p', 'video_480p', 'video_720p', 'video_1080p',
            'thumbnail', 'duration', 'formatted_duration', 'quality',
            'file_size', 'formatted_file_size', 'status', 'is_featured',
            'published_at', 'view_count', 'rating', 'rating_count',
            'comment_count', 'director', 'cast', 'release_year',
            'language', 'age_rating', 'uploaded_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'view_count', 'rating', 'file_size',
            'created_at', 'updated_at'
        ]

    def get_comment_count(self, obj):
        """Gibt die Anzahl der Kommentare zurück"""
        return obj.comments.count()

    def get_rating_count(self, obj):
        """Gibt die Anzahl der Bewertungen zurück"""
        return obj.ratings.count()

    def get_uploaded_by_name(self, obj):
        """Gibt den Namen des Uploaders zurück"""
        if obj.uploaded_by:
            return obj.uploaded_by.full_name or obj.uploaded_by.username
        return None


class VideoCreateSerializer(serializers.ModelSerializer):
    """Serializer für Video-Upload"""
    
    category_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Video
        fields = [
            'id', 'title', 'slug', 'description', 'category_ids',
            'original_video', 'thumbnail', 'quality', 'director',
            'cast', 'release_year', 'language', 'age_rating',
            'status', 'is_featured'
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        """Erstellt ein neues Video"""
        category_ids = validated_data.pop('category_ids', [])
        video = Video.objects.create(**validated_data)
        
        if category_ids:
            categories = Category.objects.filter(id__in=category_ids)
            video.categories.set(categories)
        
        return video


class VideoCommentSerializer(serializers.ModelSerializer):
    """Serializer für Video-Kommentare"""
    
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = VideoComment
        fields = [
            'id', 'video', 'user', 'user_name', 'user_email',
            'content', 'is_edited', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'is_edited', 'created_at', 'updated_at']


class VideoRatingSerializer(serializers.ModelSerializer):
    """Serializer für Video-Bewertungen"""
    
    user_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = VideoRating
        fields = [
            'id', 'video', 'user', 'user_name', 'rating',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate_rating(self, value):
        """Validiert, dass die Bewertung zwischen 1 und 5 liegt"""
        if value < 1 or value > 5:
            raise serializers.ValidationError(
                "Bewertung muss zwischen 1 und 5 liegen."
            )
        return value


class VideoStreamSerializer(serializers.ModelSerializer):
    """Serializer for video playback with HLS stream URLs"""
    
    available_qualities = serializers.SerializerMethodField()
    hls_streams = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = [
            'id', 'title', 'description', 'thumbnail_url',
            'duration', 'formatted_duration',
            'available_qualities', 'hls_streams'
        ]

    def get_available_qualities(self, obj):
        """Returns list of available quality options"""
        return ['360p', '480p', '720p', '1080p']
    
    def get_hls_streams(self, obj):
        """Returns HLS M3U8 URLs for all qualities"""
        request = self.context.get('request')
        base_url = request.build_absolute_uri('/') if request else 'http://localhost:8000/'
        
        return {
            '360p': f'{base_url}api/video/{obj.id}/360p/index.m3u8',
            '480p': f'{base_url}api/video/{obj.id}/480p/index.m3u8',
            '720p': f'{base_url}api/video/{obj.id}/720p/index.m3u8',
            '1080p': f'{base_url}api/video/{obj.id}/1080p/index.m3u8',
        }
    
    def get_thumbnail_url(self, obj):
        """Returns full thumbnail URL"""
        if obj.thumbnail:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.thumbnail.url) if request else obj.thumbnail.url
        return None
