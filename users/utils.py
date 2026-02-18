"""
Utility functions for user authentication and management
"""
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from .models import User
from .email_templates import (
    get_activation_email_html,
    get_activation_email_text,
    get_password_reset_email_html,
    get_password_reset_email_text
)


def get_user_by_email(email):
    """Retrieve user by email address"""
    try:
        return User.objects.get(email=email)
    except User.DoesNotExist:
        return None


def authenticate_user(email, password):
    """Authenticate user with email and password"""
    user = get_user_by_email(email)
    if not user:
        return None
    
    # Check password directly
    if user.check_password(password):
        return user
    
    return None


def generate_jwt_tokens(user):
    """Generate JWT access and refresh tokens for user"""
    refresh = RefreshToken.for_user(user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh)
    }


def set_auth_cookies(response, access_token, refresh_token):
    """Set HTTP-only authentication cookies on response"""
    response.set_cookie(
        key='access_token',
        value=access_token,
        httponly=True,
        secure=False,
        samesite='Lax',
        max_age=3600
    )
    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite='Lax',
        max_age=604800
    )


def generate_activation_token(user):
    """Generate email activation token for user"""
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    return uid, token


def send_activation_email(user, uid, token):
    """Send HTML activation email to user"""
    activation_link = _build_activation_link(uid, token)
    
    subject = 'Aktiviere dein Videoflix-Konto'
    text_content = get_activation_email_text(activation_link)
    html_content = get_activation_email_html(activation_link, user.email)
    
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email]
    )
    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=False)


def send_password_reset_email(user, uid, token):
    """Send HTML password reset email to user"""
    reset_link = _build_password_reset_link(uid, token)
    
    subject = 'Passwort zurücksetzen - Videoflix'
    text_content = get_password_reset_email_text(reset_link)
    html_content = get_password_reset_email_html(reset_link, user.email)
    
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email]
    )
    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=False)


def _build_activation_link(uid, token):
    """Build activation URL"""
    base_url = _get_frontend_url()
    return f"{base_url}/activate/{uid}/{token}/"


def _build_password_reset_link(uid, token):
    """Build password reset URL"""
    base_url = _get_frontend_url()
    return f"{base_url}/password-reset-confirm/{uid}/{token}/"


def _get_frontend_url():
    """Get frontend base URL from settings"""
    if hasattr(settings, 'FRONTEND_URL'):
        return settings.FRONTEND_URL
    return "http://localhost:4200"
