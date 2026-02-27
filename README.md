# Videoflix

Video streaming platform (Netflix-style) with Django backend, HLS streaming, user authentication, and legal pages (Imprint, Privacy Policy) in DE/EN.

## Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Prerequisites](#-prerequisites)
- [Installation & Setup](#-installation--setup)
- [API Endpoints](#-api-endpoints)
- [Project Structure](#-project-structure)
- [Background Processing & Signals](#-background-processing--signals)
- [Environment Variables](#-environment-variables)
- [Management Commands](#-management-commands)
- [License & Author](#-license--author)

## Features

- **Users & Auth:** Registration, email activation, login/logout (JWT + HTTP-Only cookies), password reset
- **Videos:** Upload, HLS conversion (360p, 480p, 720p, 1080p), thumbnails, duration, categories
- **Streaming:** M3U8 playlists, TS segments, fallback to original MP4 when HLS is missing
- **Processing:** Django-RQ + Redis, FFmpeg/FFprobe in container
- **Legal:** Imprint & Privacy Policy (DE/EN) served from backend API
- **API Documentation:** Swagger/OpenAPI (drf-spectacular)
- **Auto-reload:** Gunicorn with `--reload` when `DEBUG=True` for development

## Tech Stack

- **Backend:** Django 6.0, Django REST Framework 3.16
- **Database:** PostgreSQL | **Cache/Queue:** Redis, Django-RQ, RQ 2.6
- **Auth:** JWT (djangorestframework-simplejwt)
- **Video:** FFmpeg (in Docker image)
- **Deployment:** Docker & Docker Compose, Gunicorn

## Prerequisites

- Docker & Docker Compose
- Optional (without Docker): Python 3.12+, PostgreSQL, Redis, FFmpeg

## Installation & Setup

### With Docker (recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/CetinTo/Videoflix.git
   cd Videoflix
   ```

2. **Environment variables**
   - Copy `.env.template` to `.env` in the **videoflix-backend** folder:
   ```bash
   cd videoflix-backend
   cp .env.template .env
   # Edit .env: SECRET_KEY, DB_PASSWORD, REDIS_PASSWORD, EMAIL_*, FRONTEND_URL
   ```

3. **Start containers**
   ```bash
   cd videoflix-backend
   docker-compose up --build
   ```

4. **Populate legal pages (Imprint/Privacy DE+EN)**
   ```bash
   docker exec videoflix_backend python manage.py migrate info
   docker exec videoflix_backend python manage.py populate_legal_pages
   ```

**URLs**

| Service | URL |
|---------|-----|
| Backend / API | http://127.0.0.1:8000 |
| Frontend | http://127.0.0.1:5500 (or served by backend at port 8000) |
| Admin | http://127.0.0.1:8000/admin/ |
| API Docs | http://127.0.0.1:8000/api/docs/ |
| RQ Dashboard | http://127.0.0.1:8000/django-rq/ |

### Without Docker (local development)

1. Create virtual environment and install dependencies:
   ```bash
   cd videoflix-backend
   python -m venv env
   env\Scripts\activate   # Windows
   pip install -r requirements.txt
   ```
2. Start PostgreSQL and Redis locally.
3. Create `.env` from `.env.template` and adjust values (`DB_HOST=localhost`, `REDIS_HOST=localhost`, and ports if needed).
4. Run migrations and populate legal pages:
   ```bash
   python manage.py migrate
   python manage.py populate_legal_pages
   ```
5. Start RQ worker (for video processing): `python manage.py rqworker default &`
6. Start server: `python manage.py runserver`

## API Endpoints

### Auth

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/register/` | Register |
| GET | `/api/activate/<uidb64>/<token>/` | Email activation |
| POST | `/api/login/` | Login (JWT + cookies) |
| POST | `/api/logout/` | Logout |
| POST | `/api/token/refresh/` | Refresh token |
| POST | `/api/password_reset/` | Request password reset |
| POST | `/api/password_confirm/<uidb64>/<token>/` | Set new password |

### Videos

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/video/` | List all videos |
| GET | `/api/video/<int:movie_id>/<str:resolution>/index.m3u8` | HLS playlist (e.g. 480p) |
| GET | `/api/video/<int:movie_id>/<str:resolution>/<str:segment>` | HLS segment or original.mp4 |

### Legal (DE/EN)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/legal/imprint/?lang=de` or `?lang=en` | Imprint |
| GET | `/api/legal/privacy/?lang=de` or `?lang=en` | Privacy Policy |
| GET | `/api/legal/terms/?lang=de` or `?lang=en` | Terms of Service |

### Admin & Docs

| Endpoint | Description |
|----------|-------------|
| `/admin/` | Django admin |
| `/api/docs/` | Swagger UI |
| `/api/schema/` | OpenAPI schema |
| `/django-rq/` | RQ dashboard |

## Project Structure

```
videoflix-backend/
├── .env                   # Environment variables (not versioned)
├── .env.template          # Environment template
├── docker-compose.yml     # Docker setup (db, redis, web)
├── backend.Dockerfile     # Backend image
├── backend.entrypoint.sh  # Entrypoint: migrations, superuser, Gunicorn, RQ
├── core/                  # Project config, URLs, settings, signals
├── api/                   # DRF API (views, serializers, frontend_views)
│   ├── users/
│   ├── videos/
│   └── info/
├── users/                 # User model, utils
├── videos/                # Video models, FFmpeg/HLS utils, RQ tasks
├── info/                  # Legal page models
├── media/                 # Uploaded files (videos, thumbnails, HLS)
└── requirements.txt
```

## Background Processing & Signals

- **RQ Worker**
  - Started from `backend.entrypoint.sh` inside the `web` container
  - Queue: `default`
  - Handles all video processing (FFmpeg)

- **Signals (`core/signals.py`)**
  - `post_save` on `videos.Video` (`auto_process_video`):
    - Enqueues `process_uploaded_video(video_id)` on the `default` queue
    - Triggers when: new Video with `original_video`, or draft Video receiving `original_video`
    - Skips when: status is not `draft`, or `original_video` is missing

- **Processing Pipeline (`videos/tasks.py`)**
  - Sets `status='processing'`
  - Extracts duration (ffprobe), generates thumbnail, creates HLS for all resolutions
  - Sets `status='published'` on success

## Environment Variables

Copy `.env.template` to `.env` in `videoflix-backend/` and adjust:

| Section | Variables |
|---------|-----------|
| **Django** | `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `FRONTEND_URL` |
| **Superuser** | `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_PASSWORD`, `DJANGO_SUPERUSER_EMAIL` |
| **PostgreSQL** | `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` |
| **Redis** | `REDIS_HOST`, `REDIS_PASSWORD`, `REDIS_LOCATION`, `REDIS_PORT`, `REDIS_DB` |
| **Email (SMTP)** | `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL` |

## Management Commands

```bash
# Run inside container
docker exec videoflix_backend python manage.py <command>

# Migrations
python manage.py migrate
python manage.py migrate info

# Populate legal pages (DE/EN)
python manage.py populate_legal_pages

# Reprocess video (duration, thumbnail, HLS)
python manage.py reprocess_video <video_id>

# Check video file path
python manage.py video_path_check [video_id]

# RQ status
python manage.py rqstats
```

## Default Credentials (development)

From `.env`: admin email `admin@videoflix.com`, password `adminpassword`. For development only.

## License & Author

Project for educational purposes.  
Author: **Cetin Toker**

For questions or issues, please open an issue on GitHub.
