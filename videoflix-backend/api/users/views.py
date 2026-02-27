import json
import logging
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.utils.decorators import method_decorator

from users.models import User, UserWatchHistory, UserFavorite
from api.users.serializers import (
    UserSerializer,
    RegisterSerializer,
    UserRegistrationSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
    UserWatchHistorySerializer,
    UserFavoriteSerializer,
)
from users.utils import (
    authenticate_user,
    generate_jwt_tokens,
    set_auth_cookies,
    generate_activation_token,
    send_activation_email,
    send_password_reset_email,
    get_user_by_email,
)


def validate_login_credentials(email, password):
    """Validate and authenticate user login credentials."""
    if not email or not password:
        return None, 'Please check your credentials and try again.'
    user = authenticate_user(email, password)
    if not user:
        return None, 'Please check your credentials and try again.'
    if not user.is_active:
        return None, 'Please check your credentials and try again.'
    return user, None


def create_login_response_data(user):
    """Build login response payload."""
    return {
        "detail": "Login successful",
        "user": {"id": user.id, "email": user.email, "username": user.username}
    }


class LoginView(APIView):
    """Authenticate user and return JWT tokens (set via HttpOnly cookies)."""
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        request={'type': 'object', 'properties': {'email': {'type': 'string'}, 'password': {'type': 'string'}}, 'required': ['email', 'password']},
        description='Authenticate user and set HttpOnly cookies.'
    )
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user, error = validate_login_credentials(email, password)
        
        if error:
            status_code = status.HTTP_400_BAD_REQUEST if not email else status.HTTP_401_UNAUTHORIZED
            return Response({'error': error}, status=status_code)
        
        tokens = generate_jwt_tokens(user)
        response = Response(create_login_response_data(user), status=status.HTTP_200_OK)
        set_auth_cookies(response, tokens['access'], tokens['refresh'])
        
        csrf_token = get_token(request)
        response.set_cookie('csrftoken', csrf_token, httponly=False, secure=False, samesite='Lax')
        return response


class LogoutView(APIView):
    """
    Logs out the user by deleting authentication cookies
    POST /api/logout/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
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


def refresh_access_token(refresh_token_str):
    """Refresh JWT access token from refresh token."""
    try:
        refresh = RefreshToken(refresh_token_str)
        return str(refresh.access_token), None
    except TokenError:
        return None, 'Invalid or expired refresh token'


class RefreshTokenView(APIView):
    """Issue a new access token when the current one has expired."""
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(description='Issue a new access token using refresh token from cookie.')
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        
        if not refresh_token:
            return Response({'error': 'Refresh token is missing'}, status=status.HTTP_400_BAD_REQUEST)
        
        access_token, error = refresh_access_token(refresh_token)
        if error:
            return Response({'error': error}, status=status.HTTP_401_UNAUTHORIZED)
        
        response = Response({'detail': 'Token refreshed', 'access': access_token}, status=status.HTTP_200_OK)
        response.set_cookie('access_token', access_token, httponly=True, secure=False, samesite='Lax', max_age=3600)
        return response


class PasswordResetView(APIView):
    """Send a password reset link to the user's email."""
    permission_classes = [permissions.AllowAny]

    @extend_schema(description='Send password reset email if account exists.')
    def post(self, request):
        email = request.data.get('email', '').strip()
        
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
            uid, token = generate_activation_token(user)
            _send_password_reset_safe(user, uid, token)
        except User.DoesNotExist:
            pass
        
        return Response({'detail': 'If an account exists, a reset email has been sent.'}, status=status.HTTP_200_OK)


def decode_uid_from_token_link(uidb64):
    """Decode user ID from base64-encoded token link."""
    try:
        return force_str(urlsafe_base64_decode(uidb64))
    except (TypeError, ValueError, OverflowError):
        return None


def validate_password_reset_token(user, token):
    """Check if password reset token is valid."""
    return default_token_generator.check_token(user, token)


def reset_user_password(user, new_password):
    """Set new password for user and save."""
    try:
        validate_password(new_password, user)
        user.set_password(new_password)
        user.save()
        return True, None
    except Exception as error:
        return False, str(error)


def validate_new_passwords(new_password, confirm_password):
    """Validate that new passwords are provided and match."""
    if not new_password or not confirm_password:
        return False, 'Both password fields are required'
    if new_password != confirm_password:
        return False, 'Passwords do not match'
    return True, None


def _get_user_for_password_reset(uidb64):
    """Resolve user from uidb64. Returns (user, error_response) or (user, None)."""
    uid = decode_uid_from_token_link(uidb64)
    if not uid:
        return None, Response({'error': 'Invalid reset link'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        return User.objects.get(pk=uid), None
    except User.DoesNotExist:
        return None, Response({'error': 'Invalid reset link'}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    """Confirm password change using the token from the email."""
    permission_classes = [permissions.AllowAny]

    @extend_schema(description='Confirm password change using token from email.')
    def post(self, request, uidb64, token):
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        valid, error = validate_new_passwords(new_password, confirm_password)
        if not valid:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        user, err_resp = _get_user_for_password_reset(uidb64)
        if err_resp:
            return err_resp
        if not validate_password_reset_token(user, token):
            return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)

        success, error = reset_user_password(user, new_password)
        if not success:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail': 'Your password has been successfully reset.'}, status=status.HTTP_200_OK)


def extract_registration_data(request):
    """Extract email/password from request (supports multiple formats)."""
    data = getattr(request, 'data', None)
    if not isinstance(data, dict):
        try:
            data = json.loads(request.body.decode('utf-8')) if request.body else {}
        except (TypeError, ValueError, AttributeError):
            data = {}
    
    email = str(data.get('email', '')).strip()
    password = str(data.get('password', '')).strip()
    confirmed = str(data.get('confirmed_password') or data.get('confirm_password') or data.get('password2', '')).strip()
    return {'email': email, 'password': password, 'confirmed_password': confirmed}


def send_activation_email_safe(user, uid, token):
    """Attempt to send activation email. Return success status."""
    try:
        send_activation_email(user, uid, token)
        return True
    except Exception as error:
        logging.getLogger(__name__).exception('Activation email failed: %s', error)
        return False


def _send_password_reset_safe(user, uid, token):
    """Attempt to send password reset email. Swallows exceptions."""
    try:
        send_password_reset_email(user, uid, token)
    except Exception as error:
        logging.getLogger(__name__).exception('Password reset email failed: %s', error)


class RegisterView(APIView):
    """Register a new user with email activation."""
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(request=RegisterSerializer, description='Register new user account.')
    def post(self, request):
        payload = extract_registration_data(request)
        serializer = RegisterSerializer(data=payload)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = serializer.save()
        uid, token = generate_activation_token(user)
        email_sent = send_activation_email_safe(user, uid, token)
        
        detail = ('Registration successful. Please check your email to activate.' 
                  if email_sent else 'Registration successful. Use "Forgot password" to get activation link.')
        return Response({'detail': detail, 'email': user.email, 'email_sent': email_sent}, status=status.HTTP_201_CREATED)


class ActivateAccountView(APIView):
    """Activate a user account via email token."""
    permission_classes = [permissions.AllowAny]

    @extend_schema(description='Activate user account using token from email.')
    def get(self, request, uidb64, token):
        uid = decode_uid_from_token_link(uidb64)
        if not uid:
            return Response({'error': 'Invalid activation link'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(pk=uid)
        except User.DoesNotExist:
            return Response({'error': 'Invalid activation link'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not validate_password_reset_token(user, token):
            return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)
        
        user.is_active = True
        user.is_email_verified = True
        user.save()
        
        return Response({'message': 'Account successfully activated.'}, status=status.HTTP_200_OK)


@extend_schema_view(list=extend_schema(description='List all users'), retrieve=extend_schema(description='Retrieve user details'))
class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for user management (CRUD)."""
    queryset = User.objects.all()
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return UserRegistrationSerializer
        if self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    def get_permissions(self):
        """Allow anyone to register; require auth for other actions."""
        return [permissions.AllowAny()] if self.action == 'create' else [permissions.IsAuthenticated()]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Return current user profile."""
        return Response(self.get_serializer(request.user).data)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Change current user password."""
        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'error': 'Wrong password'}, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        update_session_auth_hash(request, user)
        return Response({'message': 'Password successfully changed.'}, status=status.HTTP_200_OK)


@extend_schema_view(
    list=extend_schema(description='List the user watch history'),
    create=extend_schema(description='Add a video to watch history'),
    update=extend_schema(description='Update watch progress'),
)
class UserWatchHistoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet für Benutzer-Wiedergabe-Historie.
    """
    serializer_class = UserWatchHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return only the history of the current user"""
        return UserWatchHistory.objects.filter(user=self.request.user).order_by('-watched_at')

    def perform_create(self, serializer):
        """Save the history entry for the current user"""
        serializer.save(user=self.request.user)


@extend_schema_view(
    list=extend_schema(description='List the user favorites'),
    create=extend_schema(description='Add a video to favorites'),
    destroy=extend_schema(description='Remove a video from favorites'),
)
class UserFavoriteViewSet(viewsets.ModelViewSet):
    """
    ViewSet für Benutzer-Favoriten.
    """
    serializer_class = UserFavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return only the favorites of the current user"""
        return UserFavorite.objects.filter(user=self.request.user).order_by('-added_at')

    def perform_create(self, serializer):
        """Save the favorite for the current user"""
        serializer.save(user=self.request.user)

