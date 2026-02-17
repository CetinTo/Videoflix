from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import User, UserWatchHistory, UserFavorite
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    UserRegistrationSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
    UserWatchHistorySerializer,
    UserFavoriteSerializer
)
from .utils import (
    authenticate_user,
    generate_jwt_tokens,
    set_auth_cookies,
    generate_activation_token,
    send_activation_email,
    send_password_reset_email,
    get_user_by_email
)


class LoginView(APIView):
    """
    Authentifiziert den Benutzer und gibt JWT-Tokens zurück
    
    POST /api/login/
    """
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        request={
            'type': 'object',
            'properties': {
                'email': {'type': 'string', 'format': 'email'},
                'password': {'type': 'string', 'format': 'password'}
            },
            'required': ['email', 'password']
        },
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'detail': {'type': 'string'},
                    'user': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                            'username': {'type': 'string'}
                        }
                    }
                }
            }
        },
        description='Authentifiziert den Benutzer und setzt HttpOnly-Cookies (access_token & refresh_token).'
    )
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response(
                {'error': 'Bitte überprüfe deine Anmeldedaten und versuche es erneut.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate_user(email, password)
        if not user:
            return Response(
                {'error': 'Bitte überprüfe deine Anmeldedaten und versuche es erneut.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not user.is_active:
            return Response(
                {'error': 'Bitte überprüfe deine Anmeldedaten und versuche es erneut.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        tokens = generate_jwt_tokens(user)
        response = self._create_login_response(user)
        set_auth_cookies(response, tokens['access'], tokens['refresh'])
        return response
    
    def _create_login_response(self, user):
        """Create successful login response"""
        data = {
            "detail": "Anmeldung erfolgreich",
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username
            }
        }
        return Response(data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    Logs out the user by deleting authentication cookies
    
    POST /api/logout/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        request=None,
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'detail': {'type': 'string'}
                }
            }
        },
        description='Logs out user by removing HTTP-only cookies and invalidating tokens.'
    )
    def post(self, request):
        response = Response(
            {'detail': 'Erfolgreich abgemeldet'},
            status=status.HTTP_200_OK
        )
        
        # Delete HTTP-only cookies
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        
        return response


class RefreshTokenView(APIView):
    """
    Gibt ein neues Zugangstoken aus, wenn der alte Access-Token abgelaufen ist
    
    POST /api/token/refresh/
    """
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        request={
            'type': 'object',
            'properties': {}
        },
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'detail': {'type': 'string'},
                    'access': {'type': 'string'}
                }
            },
            400: {'description': 'Refresh-Token fehlt'},
            401: {'description': 'Ungültiger Refresh-Token'}
        },
        description='Gibt ein neues Zugangstoken aus. Setzt neuen access_token-Cookie. Der refresh_token muss im Cookie vorhanden und gültig sein.'
    )
    def post(self, request):
        # Lese refresh_token aus Cookie
        refresh_token = request.COOKIES.get('refresh_token')
        
        if not refresh_token:
            return Response(
                {'error': 'Refresh token is missing'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Validiere und erstelle neuen Access Token
            refresh = RefreshToken(refresh_token)
            new_access_token = str(refresh.access_token)
            
            # Response
            response_data = {
                "detail": "Token refreshed",
                "access": new_access_token
            }
            
            response = Response(response_data, status=status.HTTP_200_OK)
            
            # Setze neuen Access Token Cookie
            response.set_cookie(
                key='access_token',
                value=new_access_token,
                httponly=True,
                secure=False,  # True in Production mit HTTPS
                samesite='Lax',
                max_age=3600  # 1 Stunde
            )
            
            return response
            
        except TokenError as e:
            return Response(
                {'error': 'Invalid or expired refresh token'},
                status=status.HTTP_401_UNAUTHORIZED
            )


class PasswordResetView(APIView):
    """
    Sendet einen Link zum Zurücksetzen des Passworts an die E-Mail des Benutzers
    
    POST /api/password_reset/
    """
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        request={
            'type': 'object',
            'properties': {
                'email': {'type': 'string', 'format': 'email'}
            },
            'required': ['email']
        },
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'detail': {'type': 'string'}
                }
            }
        },
        description='Sendet einen Link zum Zurücksetzen des Passworts an die E-Mail des Benutzers. Nur möglich, wenn ein Benutzer mit dieser E-Mail existiert.'
    )
    def post(self, request):
        email = request.data.get('email')
        
        if not email:
            return Response(
                {'error': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(email=email)
            uid, token = generate_activation_token(user)
            send_password_reset_email(user, uid, token)
        except User.DoesNotExist:
            pass
        except Exception as e:
            pass
        
        return Response(
            {'detail': 'Falls ein Konto mit dieser E-Mail existiert, wurde eine Nachricht zum Zurücksetzen des Passworts gesendet.'},
            status=status.HTTP_200_OK
        )


class PasswordResetConfirmView(APIView):
    """
    Bestätigt die Passwortänderung mit dem in der E-Mail enthaltenen Token
    
    POST /api/password_confirm/<uidb64>/<token>/
    """
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        request={
            'type': 'object',
            'properties': {
                'new_password': {'type': 'string', 'format': 'password'},
                'confirm_password': {'type': 'string', 'format': 'password'}
            },
            'required': ['new_password', 'confirm_password']
        },
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'detail': {'type': 'string'}
                }
            },
            400: {'description': 'Validation error or invalid token'}
        },
        description='Bestätigt die Passwortänderung mit dem in der E-Mail enthaltenen Token.'
    )
    def post(self, request, uidb64, token):
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        
        if not new_password or not confirm_password:
            return Response(
                {'error': 'Both password fields are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if new_password != confirm_password:
            return Response(
                {'error': 'Passwords do not match'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {'error': 'Invalid reset link'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not default_token_generator.check_token(user, token):
            return Response(
                {'error': 'Invalid or expired token'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validiere Passwort
        try:
            validate_password(new_password, user)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Setze neues Passwort
        user.set_password(new_password)
        user.save()
        
        return Response(
            {'detail': 'Your Password has been successfully reset.'},
            status=status.HTTP_200_OK
        )


class RegisterView(APIView):
    """
    Registriert einen neuen Benutzer mit E-Mail-Aktivierung
    
    POST /api/register/
    """
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        request=RegisterSerializer,
        responses={201: UserSerializer},
        description='Registriert einen neuen Benutzer. Konto bleibt inaktiv bis E-Mail bestätigt wurde.'
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {'error': 'Bitte überprüfe deine Eingaben und versuche es erneut.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = serializer.save()
            uid, token = generate_activation_token(user)
            send_activation_email(user, uid, token)
            
            return Response(
                {
                    'detail': 'Registrierung erfolgreich. Bitte prüfe deine E-Mails zur Aktivierung.',
                    'email': user.email
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': 'Bitte überprüfe deine Eingaben und versuche es erneut.'},
                status=status.HTTP_400_BAD_REQUEST
            )


class ActivateAccountView(APIView):
    """
    Aktiviert einen Benutzer-Account via E-Mail-Token
    
    GET /api/activate/<uidb64>/<token>/
    
    URL Parameters:
        uidb64: Base64-codierte Benutzer-ID
        token: Aktivierungstoken
    """
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        description='Aktiviert das Benutzerkonto mithilfe des per E-Mail gesendeten Tokens.',
        responses={
            200: {"description": "Account erfolgreich aktiviert"},
            400: {"description": "Aktivierung fehlgeschlagen"}
        }
    )
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {'error': 'Invalid activation link'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.is_email_verified = True
            user.save()
            
            return Response(
                {'message': 'Account successfully activated.'},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'error': 'Invalid or expired token'},
                status=status.HTTP_400_BAD_REQUEST
            )


@extend_schema_view(
    list=extend_schema(description='Listet alle Benutzer auf (nur Admin)'),
    retrieve=extend_schema(description='Ruft Benutzer-Details ab'),
    create=extend_schema(description='Registriert einen neuen Benutzer (Legacy)'),
    update=extend_schema(description='Aktualisiert Benutzer-Informationen'),
    partial_update=extend_schema(description='Aktualisiert Benutzer-Informationen teilweise'),
)
class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet für Benutzer-Verwaltung
    
    Bietet CRUD-Operationen für Benutzer
    """
    queryset = User.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    def get_permissions(self):
        """
        Registrierung ist öffentlich, alles andere erfordert Authentifizierung
        """
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    
    @extend_schema(
        description='Gibt das Profil des aktuell angemeldeten Benutzers zurück'
    )
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Gibt das Profil des aktuell angemeldeten Benutzers zurück"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @extend_schema(
        request=ChangePasswordSerializer,
        description='Ändert das Passwort des aktuell angemeldeten Benutzers'
    )
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Ändert das Passwort des Benutzers"""
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            user = request.user
            
            # Prüfe altes Passwort
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {'old_password': ['Wrong password.']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Setze neues Passwort
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            # Session aktualisieren
            update_session_auth_hash(request, user)
            
            return Response(
                {'message': 'Password successfully changed.'},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(description='Listet die Wiedergabe-Historie des Benutzers auf'),
    create=extend_schema(description='Fügt ein Video zur Wiedergabe-Historie hinzu'),
    update=extend_schema(description='Aktualisiert den Wiedergabe-Fortschritt'),
)
class UserWatchHistoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet für Wiedergabe-Historie
    
    Verwaltet die Wiedergabe-Historie eines Benutzers
    """
    serializer_class = UserWatchHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Gibt nur die Historie des aktuellen Benutzers zurück"""
        return UserWatchHistory.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Setzt den Benutzer automatisch"""
        serializer.save(user=self.request.user)


@extend_schema_view(
    list=extend_schema(description='Listet die Favoriten des Benutzers auf'),
    create=extend_schema(description='Fügt ein Video zu den Favoriten hinzu'),
    destroy=extend_schema(description='Entfernt ein Video aus den Favoriten'),
)
class UserFavoriteViewSet(viewsets.ModelViewSet):
    """
    ViewSet für Favoriten
    
    Verwaltet die Favoriten eines Benutzers
    """
    serializer_class = UserFavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']  # Nur GET, POST, DELETE
    
    def get_queryset(self):
        """Gibt nur die Favoriten des aktuellen Benutzers zurück"""
        return UserFavorite.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Setzt den Benutzer automatisch"""
        serializer.save(user=self.request.user)
    
    @extend_schema(
        description='Prüft, ob ein Video in den Favoriten ist'
    )
    @action(detail=False, methods=['get'])
    def check(self, request):
        """Prüft, ob ein Video in den Favoriten ist"""
        video_id = request.query_params.get('video_id')
        
        if not video_id:
            return Response(
                {'error': 'video_id Parameter erforderlich'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        exists = self.get_queryset().filter(video_id=video_id).exists()
        return Response({'is_favorite': exists})
