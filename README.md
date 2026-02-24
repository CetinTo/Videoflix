# Videoflix

Video streaming platform (Netflix-style) with Django backend, HLS streaming, user auth, and legal pages (Imprint, Privacy Policy) in DE/EN.

## Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Prerequisites](#-prerequisites)
- [Installation & Setup](#-installation--setup)
- [API Endpoints](#-api-endpoints)
- [Project Structure](#-project-structure)
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

## Tech Stack

- **Backend:** Django 6.0, Django REST Framework 3.16
- **DB:** PostgreSQL | **Cache/Queue:** Redis, Django-RQ, RQ 2.6
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
   - Copy `.env.template` (project root) to `.env` in the **same directory** (project root). Docker Compose loads this `.env` for the backend.
   ```bash
   cp .env.template .env
   # Edit .env: SECRET_KEY, DB_PASSWORD, REDIS_PASSWORD, EMAIL_*, FRONTEND_URL
   ```
   - For local development without Docker: create `videoflix-backend/.env` from the template (e.g. `cp .env.template videoflix-backend/.env`).

3. **Start containers**
   ```bash
   docker-compose up -d
   ```

4. **Populate legal pages (Imprint/Privacy DE+EN)** (run from project root)
   ```bash
   docker-compose exec web python manage.py migrate info
   docker-compose exec web python manage.py populate_legal_pages
   ```

**Backend** läuft auf **http://127.0.0.1:8000** (bzw. http://localhost:8000).  
**Frontend** (statische Seiten) läuft auf **http://127.0.0.1:5500** (bzw. http://localhost:5500).

- Backend / API: http://127.0.0.1:8000  
- Frontend: http://127.0.0.1:5500  
- Admin: http://127.0.0.1:8000/admin/  
- API Docs: http://127.0.0.1:8000/api/docs/  
- RQ Dashboard: http://127.0.0.1:8000/django-rq/

### Without Docker (local development)

1. Virtual environment and dependencies (in backend folder):
   ```bash
   cd videoflix-backend
   python -m venv env
   env\Scripts\activate   # Windows
   pip install -r requirements.txt
   ```
2. Start PostgreSQL and Redis locally.
3. Create `.env` from `.env.template` (e.g. `cp .env.template .env` in `videoflix-backend`) and adjust values (DB_HOST=localhost, REDIS_HOST=localhost, and ports if needed).
4. Migrations and legal pages:
   ```bash
   python manage.py migrate
   python manage.py populate_legal_pages
   # Superuser is created on first start from .env (see backend.entrypoint.sh)
   ```
5. RQ worker (optional, for video processing): `python manage.py rqworker default &`
6. Server: `python manage.py runserver`

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
| GET | `/api/video/{id}/` | Video details |
| POST | `/api/video/` | Upload video |
| GET | `/api/video/{id}/{resolution}/index.m3u8` | HLS playlist (e.g. 480p) |
| GET | `/api/video/{id}/{resolution}/{segment}/` | HLS segment or original.mp4 |

### Legal (DE/EN)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/legal/imprint/?lang=de` or `?lang=en` | Imprint |
| GET | `/api/legal/privacy/?lang=de` or `?lang=en` | Privacy Policy |

### Admin & Docs

| Endpoint | Description |
|----------|-------------|
| `/admin/` | Django admin |
| `/api/docs/` | Swagger UI |
| `/api/schema/` | OpenAPI schema |
| `/django-rq/` | RQ dashboard |

## Project Structure

```
Videoflix/
├── .env.template              # Environment variables template (copy to .env)
├── .env                       # Local env vars (not versioned, used by Docker)
├── docker-compose.yml         # Docker setup (db, redis, web, frontend)
├── backend.Dockerfile        # Backend image
├── backend.entrypoint.sh      # Entrypoint: migrations, superuser, Gunicorn, RQ
├── README.md
├── pages/                     # Frontend (static pages)
│   ├── imprint/               # Imprint (loads content from API)
│   ├── privacy/               # Privacy Policy (loads content from API)
│   ├── auth/
│   └── video_list/
└── videoflix-backend/         # Django backend
    ├── .env                   # Optional: for local development without Docker
    ├── .env.template          # Copy of env template (reference)
    ├── core/                  # Project config, URLs, settings
    ├── users/                 # Users, auth
    ├── videos/                # Videos, HLS, RQ tasks
    ├── info/                  # Legal pages (Imprint, Privacy DE/EN)
    ├── media/                 # Uploaded files (videos, thumbnails)
    └── requirements.txt       # Python dependencies
```

## Environment Variables

All variables needed to set up the project are in `.env.template` (project root). After copying to `.env`, adjust at least: `SECRET_KEY`, `DB_PASSWORD`, `REDIS_PASSWORD`, `FRONTEND_URL`, and for email activation/password reset: `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL`.

| Section | Variables |
|--------|-----------|
| **Django** | `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `FRONTEND_URL` |
| **Superuser** (first start) | `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_PASSWORD`, `DJANGO_SUPERUSER_EMAIL` |
| **PostgreSQL** | `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` |
| **Redis** | `REDIS_HOST`, `REDIS_PASSWORD`, `REDIS_LOCATION`, `REDIS_PORT`, `REDIS_DB` |
| **Email (SMTP)** | `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_USE_SSL`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL` |

Note: `REDIS_LOCATION` must use the same password as `REDIS_PASSWORD` (e.g. `redis://:foobared@redis:6379/1`).

## Management Commands

```bash
# Migrations
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py migrate info   # Legal pages (language)

# Populate legal pages (DE/EN)
docker-compose exec web python manage.py populate_legal_pages

# Reprocess video (duration, thumbnail, HLS)
docker-compose exec web python manage.py reprocess_video <video_id>

# Check if video file exists on disk
docker-compose exec web python manage.py video_path_check [video_id]

# RQ status
docker-compose exec web python manage.py rqstats
```

## Default Credentials (development)

From `.env.template`: admin email e.g. `admin@videoflix.com`, password `changeme` – after first start from `.env` (e.g. `adminpassword`). For development only.

## License & Author

Project for educational purposes.  
Author: **Cetin Toker**

For questions or issues, please open an issue on GitHub.
