# Videoflix Backend - Django REST Framework

Ein vollständiges Video-Streaming-Backend ähnlich wie Netflix, entwickelt mit Django und Django REST Framework.

## Features

✨ **Hauptfunktionen:**
- 🎬 Video-Upload und automatische Konvertierung in mehrere Qualitäten (360p, 480p, 720p, 1080p)
- 👤 Benutzer-Authentifizierung mit JWT
- 📁 Kategorien und Tags für Videos
- ⭐ Bewertungssystem (1-5 Sterne)
- 💬 Kommentarsystem
- 📊 Wiedergabe-Historie und Favoriten
- 🔥 Featured und Trending Videos
- 📱 RESTful API mit vollständiger Dokumentation (Swagger)
- 🚀 Asynchrone Video-Verarbeitung mit Django-RQ
- 🎨 Automatische Thumbnail-Generierung
- 🔐 Sichere Authentifizierung und Autorisierung

## Technologie-Stack

- **Python 3.12**
- **Django 5.0.6**
- **Django REST Framework 3.15**
- **PostgreSQL** - Datenbank
- **Redis** - Caching und Task Queue
- **Django-RQ** - Asynchrone Video-Verarbeitung
- **FFmpeg** - Video-Konvertierung
- **JWT** - Authentifizierung
- **Docker** - Containerisierung
- **Gunicorn** - Production Server

## Installation

### 1. Voraussetzungen

- Python 3.12+
- PostgreSQL
- Redis
- FFmpeg
- Docker & Docker Compose (optional)

### 2. Mit Docker (Empfohlen)

```bash
# .env Datei bereits erstellt
# Starte alle Services
docker-compose up --build

# Migrations ausführen
docker-compose exec web python manage.py migrate

# Superuser erstellen
docker-compose exec web python manage.py createsuperuser

# Statische Dateien sammeln
docker-compose exec web python manage.py collectstatic --noinput
```

### 3. Ohne Docker (Lokale Installation)

```bash
# Virtual Environment erstellen
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate  # Windows

# Dependencies installieren
pip install -r requirements.txt

# .env Datei konfigurieren (siehe .env.template)

# PostgreSQL und Redis starten
# (manuell oder als Service)

# Migrations ausführen
python manage.py migrate

# Superuser erstellen
python manage.py createsuperuser

# Logs-Ordner erstellen
mkdir logs

# Development Server starten
python manage.py runserver

# In einem separaten Terminal: RQ Worker starten
python manage.py rqworker default
```

## Projekt-Struktur

```
Videoflix/
├── videoflix/              # Django Hauptprojekt
│   ├── settings.py        # Konfiguration
│   ├── urls.py           # Haupt-URLs
│   ├── wsgi.py
│   └── asgi.py
├── users/                 # Benutzer-App
│   ├── models.py         # User, WatchHistory, Favorites
│   ├── serializers.py
│   ├── views.py
│   └── admin.py
├── videos/                # Videos-App
│   ├── models.py         # Video, Category, Comments, Ratings
│   ├── serializers.py
│   ├── views.py
│   ├── tasks.py          # Video-Verarbeitung (ffmpeg)
│   ├── signals.py        # Auto-Processing
│   └── admin.py
├── media/                 # Hochgeladene Dateien
├── staticfiles/          # Statische Dateien
├── logs/                 # Log-Dateien
├── manage.py
├── requirements.txt
├── .env
└── docker-compose.yml
```

## API-Endpoints

### Authentifizierung
- `POST /api/auth/login/` - JWT Token erhalten
- `POST /api/auth/refresh/` - Token erneuern

### Benutzer
- `POST /api/users/` - Registrierung
- `GET /api/users/me/` - Aktuelles Profil
- `PUT /api/users/{id}/` - Profil aktualisieren
- `POST /api/users/change_password/` - Passwort ändern

### Videos
- `GET /api/videos/` - Alle Videos
- `GET /api/videos/{slug}/` - Video-Details
- `POST /api/videos/` - Video hochladen
- `GET /api/videos/featured/` - Featured Videos
- `GET /api/videos/trending/` - Trending Videos
- `GET /api/videos/{slug}/stream/` - Stream-URLs
- `GET /api/videos/{slug}/similar/` - Ähnliche Videos

### Kategorien
- `GET /api/categories/` - Alle Kategorien
- `GET /api/categories/{slug}/` - Kategorie-Details

### Kommentare
- `GET /api/comments/?video_slug={slug}` - Kommentare zu einem Video
- `POST /api/comments/` - Kommentar hinzufügen
- `PUT /api/comments/{id}/` - Kommentar bearbeiten
- `DELETE /api/comments/{id}/` - Kommentar löschen

### Bewertungen
- `GET /api/ratings/?video_slug={slug}` - Bewertungen zu einem Video
- `POST /api/ratings/` - Bewertung hinzufügen
- `GET /api/ratings/my_rating/?video_slug={slug}` - Eigene Bewertung

### Favoriten & Historie
- `GET /api/favorites/` - Favoriten
- `POST /api/favorites/` - Zu Favoriten hinzufügen
- `DELETE /api/favorites/{id}/` - Aus Favoriten entfernen
- `GET /api/watch-history/` - Wiedergabe-Historie
- `POST /api/watch-history/` - Fortschritt speichern

### Dokumentation
- `GET /api/docs/` - Swagger UI (Interaktive API-Dokumentation)
- `GET /api/schema/` - OpenAPI Schema

## Video-Verarbeitung

Videos werden automatisch nach dem Upload verarbeitet:

1. **Dauer ermitteln** - Mit ffprobe
2. **Thumbnail generieren** - Screenshot bei 5 Sekunden
3. **Konvertierung** - In 4 Qualitäten (360p, 480p, 720p, 1080p)

Die Verarbeitung läuft asynchron im Hintergrund mit Django-RQ.

### RQ Dashboard

Überwache die Video-Verarbeitung:
```
http://localhost:8000/django-rq/
```

## Admin-Panel

Django Admin ist verfügbar unter:
```
http://localhost:8000/admin/
```

Login mit dem erstellten Superuser.

## Umgebungsvariablen (.env)

Wichtige Variablen:

```env
# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Datenbank
DB_NAME=videoflix_db
DB_USER=videoflix_user
DB_PASSWORD=your-password
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# E-Mail
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email
EMAIL_HOST_PASSWORD=your-app-password
```

## Testing

```bash
# Alle Tests ausführen
python manage.py test

# Nur bestimmte App testen
python manage.py test users
python manage.py test videos
```

## Production Deployment

### Wichtige Schritte:

1. **DEBUG auf False setzen**
   ```python
   DEBUG=False
   ```

2. **SECRET_KEY generieren**
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

3. **ALLOWED_HOSTS setzen**
   ```python
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   ```

4. **Statische Dateien sammeln**
   ```bash
   python manage.py collectstatic
   ```

5. **Mit Gunicorn starten**
   ```bash
   gunicorn videoflix.wsgi:application --bind 0.0.0.0:8000 --workers 4
   ```

6. **Nginx als Reverse Proxy** (empfohlen)

## Nützliche Befehle

```bash
# Migrations erstellen
python manage.py makemigrations

# Migrations anwenden
python manage.py migrate

# Shell öffnen
python manage.py shell

# RQ Worker starten
python manage.py rqworker default

# Cache leeren
python manage.py clear_cache

# Testdaten erstellen
python manage.py loaddata fixtures/sample_data.json
```

## Troubleshooting

### ffmpeg nicht gefunden
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Herunterladen von https://ffmpeg.org/download.html
```

### Redis Connection Error
```bash
# Redis starten
redis-server

# Oder als Service
sudo systemctl start redis
```

### PostgreSQL Connection Error
```bash
# PostgreSQL starten
sudo systemctl start postgresql

# Datenbank erstellen
createdb videoflix_db
```

## Lizenz

MIT License

## Support

Bei Fragen oder Problemen:
- Dokumentation: http://localhost:8000/api/docs/
- Admin: http://localhost:8000/admin/

---

**Viel Erfolg mit deinem Videoflix Backend!** 🎬
