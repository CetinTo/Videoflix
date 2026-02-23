"""
Custom JWT Authentication from Cookies.
On invalid/expired token or user not found we return None so that AllowAny views
(register, login) still work when the browser sends old or stale cookies.
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework.exceptions import AuthenticationFailed


class JWTCookieAuthentication(JWTAuthentication):
    """
    JWT from cookie first, then Authorization header.
    Invalid/expired token or user_not_found → return None (request as anonymous).
    """

    def authenticate(self, request):
        raw_token = request.COOKIES.get('access_token')
        if raw_token is None:
            header = self.get_header(request)
            if header is None:
                return None
            raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None
        try:
            validated_token = self.get_validated_token(raw_token)
            return self.get_user(validated_token), validated_token
        except (InvalidToken, AuthenticationFailed):
            return None
