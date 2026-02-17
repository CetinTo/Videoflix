# Videoflix Backend - Quickstart Guide

## Schnellstart mit Docker 🚀

Die einfachste Methode, um Videoflix zu starten:

```bash
# 1. Alle Services starten
docker-compose up --build

# 2. In einem neuen Terminal: Migrations ausführen
docker-compose exec web python manage.py migrate

# 3. Superuser erstellen
docker-compose exec web python manage.py createsuperuser
```

**Fertig!** Öffne http://localhost:8000/api/docs/

---

## Schnellstart ohne Docker (Windows) 💻

```powershell
# 1. Virtual Environment erstellen und aktivieren
python -m venv venv
venv\Scripts\activate

# 2. Dependencies installieren
pip install -r requirements.txt

# 3. .env Datei ist bereits vorhanden
# Bei Bedarf anpassen

# 4. PostgreSQL und Redis starten (Docker oder lokal)
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=videoflix_password_2026 -e POSTGRES_USER=videoflix_user -e POSTGRES_DB=videoflix_db postgres
docker run -d -p 6379:6379 redis

# 5. Migrations
python manage.py makemigrations
python manage.py migrate

# 6. Superuser erstellen
python manage.py createsuperuser

# 7. Server starten
python manage.py runserver

# 8. In neuem Terminal: RQ Worker starten
python manage.py rqworker default
```

**Fertig!** Öffne http://localhost:8000/api/docs/

---

## Schnellstart ohne Docker (Linux/Mac) 🐧

```bash
# 1. Setup-Script ausführen
chmod +x setup.sh
./setup.sh

# 2. PostgreSQL und Redis starten
sudo systemctl start postgresql
sudo systemctl start redis

# 3. Server starten
python manage.py runserver

# 4. In neuem Terminal: RQ Worker starten
python manage.py rqworker default
```

**Fertig!** Öffne http://localhost:8000/api/docs/

---

## Erste Schritte nach der Installation

### 1. Admin-Panel erkunden
```
http://localhost:8000/admin/
```
Login mit deinem Superuser

### 2. API-Dokumentation ansehen
```
http://localhost:8000/api/docs/
```
Interaktive Swagger UI

### 3. RQ Dashboard (Video-Verarbeitung)
```
http://localhost:8000/django-rq/
```
Überwache Video-Konvertierungen

### 4. Ersten Benutzer registrieren (API)

**POST** `/api/users/`
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "SecurePassword123",
  "password2": "SecurePassword123",
  "first_name": "Test",
  "last_name": "User"
}
```

### 5. Login erhalten (JWT Token)

**POST** `/api/auth/login/`
```json
{
  "email": "test@example.com",
  "password": "SecurePassword123"
}
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbG...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbG..."
}
```

### 6. Kategorien erstellen (Admin)

Im Admin-Panel:
1. Gehe zu **Kategorien**
2. Klicke **Kategorie hinzufügen**
3. Erstelle z.B.:
   - Action
   - Drama
   - Komödie
   - Horror
   - Sci-Fi

### 7. Video hochladen

**POST** `/api/videos/`

Header:
```
Authorization: Bearer <dein-access-token>
```

Form-Data:
- `title`: "Mein erstes Video"
- `description`: "Eine tolle Beschreibung"
- `original_video`: (Video-Datei)
- `category_ids`: [1, 2]
- `status`: "draft"

Das Video wird automatisch verarbeitet!

---

## Wichtige Endpoints

### Authentifizierung
```
POST /api/auth/login/        - Login (JWT Token)
POST /api/auth/refresh/      - Token erneuern
POST /api/users/             - Registrierung
GET  /api/users/me/          - Eigenes Profil
```

### Videos
```
GET  /api/videos/            - Alle Videos
GET  /api/videos/{slug}/     - Video-Details
POST /api/videos/            - Video hochladen
GET  /api/videos/featured/   - Featured Videos
GET  /api/videos/trending/   - Trending Videos
```

### Kategorien
```
GET  /api/categories/        - Alle Kategorien
GET  /api/categories/{slug}/ - Kategorie-Details
```

### Favoriten
```
GET    /api/favorites/       - Meine Favoriten
POST   /api/favorites/       - Favorit hinzufügen
DELETE /api/favorites/{id}/  - Favorit entfernen
```

---

## Probleme lösen

### Port 8000 bereits belegt
```bash
# Anderen Port verwenden
python manage.py runserver 8080
```

### PostgreSQL läuft nicht
```bash
# Docker verwenden
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres
```

### Redis läuft nicht
```bash
# Docker verwenden
docker run -d -p 6379:6379 redis
```

### ffmpeg nicht gefunden
```bash
# Windows: Herunterladen von https://ffmpeg.org/download.html
# Linux: sudo apt install ffmpeg
# Mac: brew install ffmpeg
```

### Migration Fehler
```bash
# Alle Migrations löschen und neu erstellen
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
python manage.py makemigrations
python manage.py migrate
```

---

## Tipps & Tricks

### 1. Django Shell verwenden
```bash
python manage.py shell

# Beispiel: Alle Videos anzeigen
from videos.models import Video
Video.objects.all()
```

### 2. Testdaten erstellen
```python
# In der Django Shell
from users.models import User
from videos.models import Category, Video

# Kategorie erstellen
category = Category.objects.create(name="Action")

# Video erstellen
video = Video.objects.create(
    title="Test Video",
    description="Mein Test-Video",
    status="published"
)
video.categories.add(category)
```

### 3. Cache leeren
```bash
python manage.py shell -c "from django.core.cache import cache; cache.clear()"
```

### 4. Superuser Passwort zurücksetzen
```bash
python manage.py changepassword admin
```

### 5. Video-Verarbeitung manuell starten
```python
# In der Django Shell
from videos.tasks import process_uploaded_video
import django_rq

queue = django_rq.get_queue('default')
queue.enqueue(process_uploaded_video, video_id=1)
```

---

## Nächste Schritte

1. **Frontend entwickeln**: React, Vue, oder Angular
2. **Tests schreiben**: Unit Tests und Integration Tests
3. **CI/CD einrichten**: GitHub Actions, GitLab CI
4. **Monitoring**: Sentry für Error Tracking
5. **CDN**: CloudFlare für Video-Delivery
6. **Backup**: Automatische DB-Backups

---

## Support & Dokumentation

- 📖 **Vollständige Doku**: `README_BACKEND.md`
- 🐧 **Linux Installation**: `INSTALLATION.md`
- 🔧 **API Docs**: http://localhost:8000/api/docs/
- 👨‍💼 **Admin**: http://localhost:8000/admin/

---

**Viel Erfolg mit Videoflix!** 🎬✨
