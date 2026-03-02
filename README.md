# Videoflix

A Netflix-style video streaming REST API built with Django and Django REST Framework. Supports HLS streaming, JWT authentication via HTTP-only cookies, background video processing with FFmpeg, and multilingual legal pages.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [API Endpoints](#api-endpoints)
- [Project Structure](#project-structure)
- [Background Processing](#background-processing)
- [Environment Variables](#environment-variables)
- [Management Commands](#management-commands)
- [License & Author](#license--author)

## Features

- **Authentication:** Registration with email activation, login/logout via JWT + HTTP-only cookies, password reset
- **Videos:** Upload, automatic HLS conversion (360p, 480p, 720p, 1080p), thumbnail generation, duration extraction
- **Streaming:** M3U8 playlists, TS segments, fallback to original MP4 if HLS is unavailable
- **Background Processing:** Django-RQ + Redis, FFmpeg/FFprobe inside the Docker container
- **Legal Pages:** Imprint, Privacy Policy, Terms of Service (German & English) served via API
- **API Documentation:** Swagger UI / OpenAPI via drf-spectacular
- **Token Security:** JWT refresh token rotation with blacklisting via `simplejwt.token_blacklist`

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 6, Django REST Framework 3.16 |
| Database | PostgreSQL |
| Cache & Queue | Redis, Django-RQ |
| Auth | djangorestframework-simplejwt (HTTP-only cookies) |
| Video Processing | FFmpeg / FFprobe |
| Deployment | Docker, Docker Compose, Gunicorn |
| API Docs | drf-spectacular (Swagger UI) |

## Prerequisites

- Docker & Docker Compose

> Without Docker: Python 3.12+, PostgreSQL, Redis, FFmpeg installed locally.

## Installation & Setup

### With Docker (recommended)

**1. Clone the repository**
```bash
git clone https://github.com/CetinTo/Videoflix.git
cd Videoflix/videoflix-backend
```

**2. Configure environment variables**
```bash
cp .env.template .env
# Edit .env: SECRET_KEY, DB_PASSWORD, EMAIL_*, FRONTEND_URL
```

**3. Build and start containers**
```bash
docker-compose up --build -d
```

**4. Run migrations and populate legal pages**
```bash
docker exec videoflix_backend python manage.py migrate
docker exec videoflix_backend python manage.py populate_legal_pages
```

**Available URLs**

| Service | URL |
|---------|-----|
| API | http://127.0.0.1:8000/api/ |
| Admin | http://127.0.0.1:8000/admin/ |
| API Docs (Swagger) | http://127.0.0.1:8000/api/docs/ |
| RQ Dashboard | http://127.0.0.1:8000/django-rq/ |

---

### Without Docker (local development)

```bash
cd videoflix-backend
python -m venv env
source env/bin/activate       # Linux/macOS
env\Scripts\activate          # Windows

pip install -r requirements.txt
cp .env.template .env
# Set DB_HOST=localhost, REDIS_HOST=localhost in .env

python manage.py migrate
python manage.py populate_legal_pages
python manage.py rqworker default &   # Background worker
python manage.py runserver
```

## API Endpoints

### Authentication

| Method | Endpoint | Description | Auth required |
|--------|----------|-------------|---------------|
| POST | `/api/register/` | Create account (sends activation email) | No |
| GET | `/api/activate/<uidb64>/<token>/` | Activate account via email link | No |
| POST | `/api/login/` | Login — returns JWT via HTTP-only cookies | No |
| POST | `/api/logout/` | Logout — clears cookies | Yes |
| POST | `/api/token/refresh/` | Refresh access token (from cookie) | No |
| POST | `/api/password_reset/` | Request password reset email | No |
| POST | `/api/password_confirm/<uidb64>/<token>/` | Set new password | No |

### Users

| Method | Endpoint | Description | Auth required |
|--------|----------|-------------|---------------|
| GET | `/api/users/me/` | Current user profile | Yes |
| PUT/PATCH | `/api/users/<id>/` | Update profile | Yes |
| GET | `/api/watch-history/` | Watch history | Yes |
| POST | `/api/watch-history/` | Add to watch history | Yes |
| GET | `/api/favorites/` | Favorites list | Yes |
| POST | `/api/favorites/` | Add to favorites | Yes |
| DELETE | `/api/favorites/<id>/` | Remove from favorites | Yes |

### Videos

| Method | Endpoint | Description | Auth required |
|--------|----------|-------------|---------------|
| GET | `/api/video/` | List all published videos | No |
| GET | `/api/video/<slug>/` | Video detail | No |
| GET | `/api/video/featured/` | Featured videos (hero section) | No |
| GET | `/api/video/hero/` | Random featured video | No |
| GET | `/api/video/trending/` | Top videos by view count | No |
| GET | `/api/video/by_category/` | Videos grouped by category | No |
| GET | `/api/video/<slug>/stream/` | HLS stream URLs for all qualities | No |
| GET | `/api/video/<id>/<resolution>/index.m3u8` | HLS M3U8 playlist | No |
| GET | `/api/video/<id>/<resolution>/<segment>` | HLS TS segment or original MP4 | No |
| GET | `/api/categories/` | All categories | No |

### Legal Pages

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/legal/imprint/?lang=de` | Imprint (German) |
| GET | `/api/legal/imprint/?lang=en` | Imprint (English) |
| GET | `/api/legal/privacy/?lang=de` | Privacy Policy (German) |
| GET | `/api/legal/privacy/?lang=en` | Privacy Policy (English) |
| GET | `/api/legal/terms/?lang=de` | Terms of Service (German) |
| GET | `/api/legal/terms/?lang=en` | Terms of Service (English) |

## Project Structure

```
videoflix-backend/
├── core/                        # Project configuration
│   ├── settings.py              # Django settings
│   ├── urls.py                  # Root URL configuration
│   └── signals.py               # Auto-process video on upload
│
├── users/                       # User app
│   ├── models.py                # User, UserWatchHistory, UserFavorite
│   ├── utils.py                 # Auth helpers, JWT, email sending
│   ├── email_templates.py       # HTML/text email templates
│   ├── authentication.py        # Custom JWT cookie authentication
│   ├── api/
│   │   ├── views.py             # Login, Register, Activate, Password Reset, UserViewSet
│   │   ├── serializers.py       # User serializers
│   │   └── urls.py              # Auth & user URL patterns
│   └── management/commands/
│       ├── create_admin.py
│       ├── resend_activation.py
│       └── flush_db_keep_admin.py
│
├── videos/                      # Video app
│   ├── models.py                # Category, Video, VideoComment, VideoRating
│   ├── utils.py                 # FFmpeg commands, HLS serving, file paths
│   ├── tasks.py                 # RQ tasks: thumbnail, duration, HLS conversion
│   ├── api/
│   │   ├── views.py             # VideoViewSet, CategoryViewSet, HLS views
│   │   ├── serializers.py       # Video serializers
│   │   └── urls.py              # Video URL patterns
│   └── management/commands/
│       ├── reprocess_video.py
│       └── video_path_check.py
│
├── info/                        # Legal pages app
│   ├── models.py                # LegalPage model
│   ├── views.py                 # LegalPageViewSet
│   ├── serializers.py           # LegalPageSerializer
│   ├── urls.py                  # Legal URL patterns
│   ├── legal_content.py         # HTML content for DE/EN legal pages
│   └── management/commands/
│       └── populate_legal_pages.py
│
├── .env.template                # Environment variable template
├── docker-compose.yml           # Services: web, db, redis
├── backend.Dockerfile           # Python 3.12 Alpine + FFmpeg
├── backend.entrypoint.sh        # Startup: migrate, create superuser, gunicorn + rqworker
└── requirements.txt
```

## Background Processing

### Signal (`core/signals.py`)

When a `Video` is saved with an `original_video` file and status `draft`, the signal `auto_process_video` automatically enqueues the processing job on the `default` RQ queue.

### Processing Pipeline (`videos/tasks.py`)

1. Set `status = 'processing'`
2. Extract duration with `ffprobe`
3. Generate thumbnail at 5s mark with `ffmpeg`
4. Convert to HLS (M3U8 + TS segments) for all 4 resolutions: `360p`, `480p`, `720p`, `1080p`
5. Set `status = 'published'`

### RQ Worker

Started automatically inside the `web` container via `backend.entrypoint.sh`. Can also be started manually:

```bash
docker exec videoflix_backend python manage.py rqworker default
```

## Environment Variables

Copy `.env.template` to `.env` in `videoflix-backend/` and set the following:

| Section | Variable | Description |
|---------|----------|-------------|
| Django | `SECRET_KEY` | Django secret key |
| Django | `DEBUG` | `True` for development, `False` for production |
| Django | `ALLOWED_HOSTS` | Comma-separated list of allowed hosts |
| Django | `CSRF_TRUSTED_ORIGINS` | Comma-separated trusted origins |
| Django | `FRONTEND_URL` | Used in activation/reset email links |
| Superuser | `DJANGO_SUPERUSER_USERNAME` | Auto-created admin username |
| Superuser | `DJANGO_SUPERUSER_PASSWORD` | Auto-created admin password |
| Superuser | `DJANGO_SUPERUSER_EMAIL` | Auto-created admin email |
| PostgreSQL | `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | Database connection |
| Redis | `REDIS_HOST`, `REDIS_PASSWORD`, `REDIS_LOCATION`, `REDIS_PORT`, `REDIS_DB` | Redis connection |
| Email | `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL` | SMTP settings |

## Management Commands

```bash
# Run inside the container
docker exec videoflix_backend python manage.py <command>

# Apply all migrations
python manage.py migrate

# Seed legal pages (Imprint, Privacy Policy, Terms — DE & EN)
python manage.py populate_legal_pages

# Reprocess a video (re-run thumbnail, duration, HLS)
python manage.py reprocess_video <video_id>

# Check file path for a video
python manage.py video_path_check [video_id]

# Show RQ queue stats
python manage.py rqstats

# Create admin user manually
python manage.py create_admin

# Resend activation email
python manage.py resend_activation <email>
```

## License & Author

Project developed for educational purposes.  
Author: **Cetin Toker**

For questions or issues, open an issue on [GitHub](https://github.com/CetinTo/Videoflix).
