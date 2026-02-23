from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .models import User, UserWatchHistory, UserFavorite


def _validate_password_min_length(value):
    """Mindestlänge 8 für Registrierung (locker, damit Frontend nicht angepasst werden muss)."""
    if len(value) < 8:
        raise serializers.ValidationError("Passwort muss mindestens 8 Zeichen haben.")
    return value


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer für Benutzer-Registrierung mit E-Mail-Aktivierung"""

    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    confirmed_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'confirmed_password']
        read_only_fields = ['id']
        extra_kwargs = {'email': {'required': True}}

    def validate_email(self, value):
        """Check if email already exists"""
        value = (value or '').strip()
        if not value:
            raise serializers.ValidationError("E-Mail ist erforderlich.")
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Diese E-Mail ist bereits registriert.")
        return value

    def validate_password(self, value):
        """Nur Mindestlänge prüfen (keine strengen Django-Validatoren)."""
        return _validate_password_min_length(value)

    def validate(self, attrs):
        """Validate that both passwords match"""
        if attrs.get('password') != attrs.get('confirmed_password'):
            raise serializers.ValidationError({
                'confirmed_password': ['Die Passwörter stimmen nicht überein.']
            })
        return attrs

    def create(self, validated_data):
        """Creates a new inactive user"""
        validated_data.pop('confirmed_password')
        email = validated_data['email']
        base_username = email.split('@')[0]
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        user = User.objects.create_user(
            username=username,
            email=email,
            password=validated_data['password'],
            is_active=False  # Account is inactive until email is confirmed
        )
        return user


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer für Benutzer-Registrierung (Legacy - kompatibel mit bestehendem Code)"""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        label='Passwort bestätigen'
    )

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'password', 'password2',
            'first_name', 'last_name', 'phone', 'birth_date'
        ]
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, attrs):
        """Validiert, dass beide Passwörter übereinstimmen"""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                "password": "Passwörter stimmen nicht überein."
            })
        return attrs

    def create(self, validated_data):
        """Erstellt einen neuen Benutzer"""
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer für Benutzer-Informationen"""
    
    full_name = serializers.ReadOnlyField()
    has_premium = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'phone', 'birth_date', 'profile_picture',
            'subscription_type', 'has_premium', 'is_email_verified',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_email_verified', 'created_at', 'updated_at']

    def get_has_premium(self, obj):
        """Gibt zurück, ob der Benutzer ein Premium-Abo hat"""
        return obj.has_premium_subscription()


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer für Benutzer-Aktualisierung"""
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone', 'birth_date',
            'profile_picture'
        ]


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer für Passwort-Änderung"""
    
    old_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password2 = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        label='Neues Passwort bestätigen'
    )

    def validate(self, attrs):
        """Validiert, dass beide neuen Passwörter übereinstimmen"""
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({
                "new_password": "Passwörter stimmen nicht überein."
            })
        return attrs


class UserWatchHistorySerializer(serializers.ModelSerializer):
    """Serializer für Wiedergabe-Historie"""
    
    video_title = serializers.CharField(source='video.title', read_only=True)
    video_thumbnail = serializers.ImageField(source='video.thumbnail', read_only=True)
    video_slug = serializers.SlugField(source='video.slug', read_only=True)

    class Meta:
        model = UserWatchHistory
        fields = [
            'id', 'video', 'video_title', 'video_thumbnail', 'video_slug',
            'watched_at', 'progress', 'completed'
        ]
        read_only_fields = ['id', 'watched_at']


class UserFavoriteSerializer(serializers.ModelSerializer):
    """Serializer für Favoriten"""
    
    video_title = serializers.CharField(source='video.title', read_only=True)
    video_thumbnail = serializers.ImageField(source='video.thumbnail', read_only=True)
    video_slug = serializers.SlugField(source='video.slug', read_only=True)
    video_description = serializers.CharField(source='video.description', read_only=True)

    class Meta:
        model = UserFavorite
        fields = [
            'id', 'video', 'video_title', 'video_thumbnail',
            'video_slug', 'video_description', 'added_at'
        ]
        read_only_fields = ['id', 'added_at']
