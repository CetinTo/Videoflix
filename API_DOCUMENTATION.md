# Videoflix API Documentation

Complete API reference for the Videoflix backend.

## Base URL

```
http://localhost:8000/api/
```

## Authentication

All authenticated endpoints require a JWT token in the Authorization header or HTTP-Only cookie.

### Register New User

**Endpoint:** `POST /api/register/`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "confirmed_password": "securepassword"
}
```

**Response:** `201 Created`
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com"
  },
  "token": "activation_token"
}
```

### Activate Account

**Endpoint:** `GET /api/activate/<uidb64>/<token>/`

**Response:** `200 OK`
```json
{
  "message": "Account successfully activated."
}
```

### Login

**Endpoint:** `POST /api/login/`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:** `200 OK`
```json
{
  "detail": "Login successful",
  "user": {
    "id": 1,
    "username": "user"
  }
}
```

**Note:** Sets HTTP-Only cookies: `access_token` & `refresh_token`

### Refresh Token

**Endpoint:** `POST /api/token/refresh/`

**Response:** `200 OK`
```json
{
  "detail": "Token refreshed",
  "access": "new_access_token"
}
```

### Password Reset Request

**Endpoint:** `POST /api/password_reset/`

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response:** `200 OK`
```json
{
  "detail": "An email has been sent to reset your password."
}
```

### Password Reset Confirm

**Endpoint:** `POST /api/password_confirm/<uidb64>/<token>/`

**Request Body:**
```json
{
  "new_password": "newsecurepassword",
  "confirm_password": "newsecurepassword"
}
```

**Response:** `200 OK`
```json
{
  "detail": "Your Password has been successfully reset."
}
```

## Videos

### List All Videos

**Endpoint:** `GET /api/video/`

**Auth Required:** Yes

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "created_at": "2023-01-01T12:00:00Z",
    "title": "Movie Title",
    "description": "Movie Description",
    "thumbnail_url": "http://example.com/media/thumbnail/image.jpg",
    "category": "Drama"
  }
]
```

### Get Video Details

**Endpoint:** `GET /api/video/{id}/`

**Auth Required:** Yes

### Upload Video

**Endpoint:** `POST /api/video/`

**Auth Required:** Yes

**Request:** Multipart form data with video file

### HLS Master Playlist

**Endpoint:** `GET /api/video/{id}/{resolution}/index.m3u8`

**Auth Required:** Yes

**Resolutions:** 360p, 480p, 720p, 1080p

**Response:** M3U8 playlist file

### HLS Video Segment

**Endpoint:** `GET /api/video/{id}/{resolution}/{segment}/`

**Auth Required:** Yes

**Response:** Binary TS segment file

## Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## Rate Limiting

Currently no rate limiting is implemented. For production, consider adding rate limiting middleware.

## CORS

CORS is configured to allow all origins in development mode. For production, configure `CORS_ALLOWED_ORIGINS` in settings.

## Interactive Documentation

Visit these endpoints for interactive API documentation:
- Swagger UI: `http://localhost:8000/api/schema/swagger-ui/`
- ReDoc: `http://localhost:8000/api/schema/redoc/`
