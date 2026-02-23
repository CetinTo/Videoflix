import json
import logging
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
    Authenticate user and return JWT tokens (set via HttpOnly cookies).

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
        description='Authenticate user and set HttpOnly cookies (access_token & refresh_token).'
    )
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response(
                {'error': 'Please check your credentials and try again.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate_user(email, password)
        if not user:
            return Response(
                {'error': 'Please check your credentials and try again.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return Response(
                {'error': 'Please check your credentials and try again.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        tokens = generate_jwt_tokens(user)
        response = self._create_login_response(user)
        set_auth_cookies(response, tokens['access'], tokens['refresh'])
        return response
    
    def _create_login_response(self, user):
        """Create successful login response"""
        data = {
            "detail": "Login successful",
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
            {'detail': 'Successfully logged out'},
            status=status.HTTP_200_OK
        )
        
        # Delete HTTP-only cookies
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        
        return response


class RefreshTokenView(APIView):
    """
    Issue a new access token when the current one has expired
    
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
            401: {'description': 'Invalid refresh token'}
        },
        description='Issue a new access token and set access_token cookie. refresh_token must be present and valid in cookie.'
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
            refresh = RefreshToken(refresh_token)
            new_access_token = str(refresh.access_token)
            response_data = {
                "detail": "Token refreshed",
                "access": new_access_token
            }
            response = Response(response_data, status=status.HTTP_200_OK)
            response.set_cookie(
                key='access_token',
                value=new_access_token,
                httponly=True,
                secure=False,
                samesite='Lax',
                max_age=3600
            )
            
            return response
            
        except TokenError as e:
            return Response(
                {'error': 'Invalid or expired refresh token'},
                status=status.HTTP_401_UNAUTHORIZED
            )


class PasswordResetView(APIView):
    """
    Send a password reset link to the user's email
    
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
        description='Send a password reset link to the given email if an account exists.'
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
            {'detail': 'If an account with this email exists, a password reset message has been sent.'},
            status=status.HTTP_200_OK
        )


class PasswordResetConfirmView(APIView):
    """
    Confirm password change using the token from the email.

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
        description='Confirm password change using the token from the email.'
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
        
        try:
            validate_password(new_password, user)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.set_password(new_password)
        user.save()
        
        return Response(
            {'detail': 'Your password has been successfully reset.'},
            status=status.HTTP_200_OK
        )


class RegisterView(APIView):
    """
    Register a new user with email activation
    
    POST /api/register/
    """
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        request=RegisterSerializer,
        responses={201: UserSerializer},
        description='Registriert einen neuen Benutzer. Konto bleibt inaktiv bis E-Mail bestätigt wurde.'
    )
    def post(self, request):
        try:
            data = getattr(request, 'data', None)
            if not data:
                try:
                    if getattr(request, 'body', None):
                        data = json.loads(request.body.decode('utf-8') or '{}')
                    else:
                        data = {}
                except (TypeError, ValueError, AttributeError):
                    data = {}
            if not isinstance(data, dict):
                data = {}
            def _v(key, *alt_keys):
                for k in (key,) + alt_keys:
                    val = data.get(k)
                    if val is None:
                        continue
                    if isinstance(val, list):
                        val = val[0] if val else ''
                    return (val.strip() if isinstance(val, str) else str(val)) if val else ''
                return ''
            payload = {
                'email': _v('email', 'Email').strip(),
                'password': _v('password', 'Password'),
                'confirmed_password': _v(
                    'confirmed_password', 'confirm_password', 'password2', 'Password2'
                ),
            }
            serializer = RegisterSerializer(data=payload)
            if not serializer.is_valid():
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
            user = serializer.save()
            uid, token = generate_activation_token(user)
            email_sent = True
            try:
                send_activation_email(user, uid, token)
            except Exception as mail_err:
                logging.getLogger(__name__).exception(
                    'Activation email could not be sent: %s', mail_err
                )
                email_sent = False
            detail = (
                'Registration successful. Please check your email to activate your account.'
                if email_sent
                else 'Registration successful. Activation email could not be sent – use "Forgot password" to get a link.'
            )
            return Response(
                {
                    'detail': detail,
                    'email': user.email,
                    'email_sent': email_sent,
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {
                    'error': 'Please check your input and try again.',
                    'detail': str(e),
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class ActivateAccountView(APIView):
    """
    Activate a user account via email token.

    GET /api/activate/<uidb64>/<token>/
    URL params: uidb64 (base64 user id), token (activation token).
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        description='Activate the user account using the token sent by email.',
        responses={
            200: {"description": "Account successfully activated"},
            400: {"description": "Activation failed"}
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
    list=extend_schema(description='List all users (admin only)'),
    retrieve=extend_schema(description='Retrieve user details'),
    create=extend_schema(description='Register a new user (legacy)'),
    update=extend_schema(description='Update user information'),
    partial_update=extend_schema(description='Partially update user information'),
)
class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user management (CRUD).
    """
    queryset = User.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    def get_permissions(self):
        """Allow anyone for create; require auth for other actions."""
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    
    @extend_schema(
        description='Return the currently authenticated user profile'
    )
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Return the current user profile."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @extend_schema(
        request=ChangePasswordSerializer,
        description='Change the current user password'
    )
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Change the current user password."""
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {'old_password': ['Wrong password.']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            update_session_auth_hash(request, user)
            
            return Response(
                {'message': 'Password successfully changed.'},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(description='List the user watch history'),
    create=extend_schema(description='Add a video to watch history'),
    update=extend_schema(description='Update watch progress'),
)
class UserWatchHistoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user watch history.
    """
    serializer_class = UserWatchHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return watch history for the current user only."""
        return UserWatchHistory.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Set the current user on the watch history entry."""
        serializer.save(user=self.request.user)


@extend_schema_view(
    list=extend_schema(description='List the user favorites'),
    create=extend_schema(description='Add a video to favorites'),
    destroy=extend_schema(description='Remove a video from favorites'),
)
class UserFavoriteViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user favorites.
    """
    serializer_class = UserFavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        """Return favorites for the current user only."""
        return UserFavorite.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Set the current user on the favorite entry."""
        serializer.save(user=self.request.user)

    @extend_schema(
        description='Check whether a video is in the user favorites'
    )
    @action(detail=False, methods=['get'])
    def check(self, request):
        """Check if a video is in the user favorites."""
        video_id = request.query_params.get('video_id')

        if not video_id:
            return Response(
                {'error': 'video_id parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        exists = self.get_queryset().filter(video_id=video_id).exists()
        return Response({'is_favorite': exists})
