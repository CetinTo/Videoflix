# Videoflix Backend

A Django REST Framework backend for a video streaming platform similar to Netflix.

## 🚀 Features

- **User Authentication**
  - JWT-based authentication with HTTP-Only cookies
  - Email activation
  - Password reset functionality
  - Custom user model

- **Video Management**
  - Video upload and management
  - Automatic HLS conversion in 4 qualities (360p, 480p, 720p, 1080p)
  - Automatic thumbnail generation
  - Video duration calculation
  - Categorization and tagging

- **HLS Adaptive Streaming**
  - M3U8 playlist generation
  - TS segment delivery
  - Multi-bitrate streaming

- **Asynchronous Video Processing**
  - Django-RQ for background tasks
  - FFmpeg integration for video conversion
  - Redis as message broker

- **API Documentation**
  - Swagger/OpenAPI with drf-spectacular
  - Interactive API documentation

## 🛠️ Tech Stack

- **Framework:** Django 6.0.2
- **API:** Django REST Framework 3.16.1
- **Database:** PostgreSQL 18
- **Cache & Queue:** Redis
- **Task Queue:** Django-RQ with RQ 2.6.1
- **Video Processing:** FFmpeg
- **Authentication:** JWT (djangorestframework-simplejwt)
- **Deployment:** Docker & Docker Compose
- **Web Server:** Gunicorn

## 📋 Prerequisites

- Docker & Docker Compose
- Python 3.12+ (for local development without Docker)
- FFmpeg (automatically installed in Docker container)

## 🔧 Installation & Setup

### With Docker (Recommended)

1. **Clone repository:**
```bash
git clone https://github.com/CetinTo/Videoflix.git
cd Videoflix
```

2. **Configure environment variables:**
```bash
# Copy .env.template to .env and adjust settings
cp .env.template .env
```

3. **Start Docker containers:**
```bash
docker-compose up --build
```

4. **Backend runs on:**
```
http://localhost:8000
```

### Without Docker (Local Development)

1. **Create virtual environment:**
```bash
python -m venv env
env\Scripts\activate  # Windows
source env/bin/activate  # Linux/Mac
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Start database & Redis** (separately)

4. **Run migrations:**
```bash
python manage.py migrate
```

5. **Create superuser:**
```bash
python manage.py create_admin
```

6. **Start server:**
```bash
python manage.py runserver
```

## 📚 API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/register/` | User registration |
| GET | `/api/activate/<uidb64>/<token>/` | Email activation |
| POST | `/api/login/` | Login (JWT + HTTP-Only cookies) |
| POST | `/api/token/refresh/` | Refresh JWT token |
| POST | `/api/password_reset/` | Request password reset |
| POST | `/api/password_confirm/<uidb64>/<token>/` | Set new password |

### Videos

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/video/` | List all videos |
| GET | `/api/video/{id}/` | Video details |
| POST | `/api/video/` | Upload video |
| GET | `/api/video/{id}/{resolution}/index.m3u8` | HLS master playlist |
| GET | `/api/video/{id}/{resolution}/{segment}/` | HLS video segment |

### Admin & Documentation

| Endpoint | Description |
|----------|-------------|
| `/admin/` | Django admin panel |
| `/api/schema/swagger-ui/` | Swagger API documentation |
| `/api/schema/redoc/` | ReDoc API documentation |

## 🔐 Default Credentials

**Django Admin:**
- Email: `admin@videoflix.com`
- Password: `adminpassword`

⚠️ **Important:** Use these credentials for development only!

## 📁 Project Structure

```
Videoflix/
├── core/                   # Django project configuration
│   ├── settings.py        # Main settings
│   ├── urls.py            # URL routing
│   └── signals.py         # Central Django signals
├── users/                 # User app
│   ├── models.py          # Custom user model
│   ├── views.py           # Auth endpoints
│   └── serializers.py     # User serializers
├── videos/                # Video app
│   ├── models.py          # Video, Category, Rating models
│   ├── views.py           # Video endpoints
│   ├── tasks.py           # Video processing (RQ tasks)
│   └── serializers.py     # Video serializers
├── media/                 # Uploaded files
│   └── videos/            # Videos + HLS segments
├── static/                # Static files
├── .env                   # Environment variables
├── docker-compose.yml     # Docker Compose configuration
├── backend.Dockerfile     # Backend Docker image
└── requirements.txt       # Python dependencies
```

## 🎥 Video Processing

Videos are automatically processed on upload:

1. **Upload** → Original video saved
2. **Duration Calculation** → FFprobe determines video length
3. **Thumbnail Generation** → Screenshot at second 5
4. **HLS Conversion** → Conversion to 4 qualities:
   - 360p (640x360, 800k bitrate)
   - 480p (854x480, 1400k bitrate)
   - 720p (1280x720, 2800k bitrate)
   - 1080p (1920x1080, 5000k bitrate)
5. **Segmentation** → 10-second TS segments + M3U8 playlists

**Directory structure after processing:**
```
media/videos/my_video/
├── original.mp4
├── thumbnail.jpg
├── hls_360p/
│   ├── index.m3u8
│   ├── segment_000.ts
│   └── ...
├── hls_480p/
│   └── ...
├── hls_720p/
│   └── ...
└── hls_1080p/
    └── ...
```

## 🐳 Docker Services

- **web:** Django backend (Port 8000)
- **db:** PostgreSQL database
- **redis:** Redis cache & message broker

## 🔧 Development

### Django Management Commands

```bash
# Create migrations
docker-compose exec web python manage.py makemigrations

# Apply migrations
docker-compose exec web python manage.py migrate

# Create admin user
docker-compose exec web python manage.py create_admin

# Django shell
docker-compose exec web python manage.py shell

# RQ worker status
docker-compose exec web python manage.py rqstats
```

### View Logs

```bash
# All containers
docker-compose logs -f

# Backend only
docker-compose logs -f web
```

## 📝 Environment Variables

Important `.env` settings:

```env
# Django
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=videoflix_db
DB_USER=videoflix_user
DB_PASSWORD=your-secure-password
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_HOST=redis
REDIS_PASSWORD=foobared
REDIS_PORT=6379

# Email (SMTP)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## 🚀 Deployment

### For Production:

1. **Adjust .env:**
   - Set `DEBUG=False`
   - Generate strong `SECRET_KEY`
   - Use secure passwords
   - Adjust `ALLOWED_HOSTS`

2. **Collect static files:**
```bash
docker-compose exec web python manage.py collectstatic --noinput
```

3. **Setup HTTPS** (e.g., with Nginx + Let's Encrypt)

4. **Setup database backups**

## 📄 License

This project is created for educational purposes.

## 👤 Author

Cetin Toker

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

## 📞 Support

For questions or issues, please open an issue on GitHub.
