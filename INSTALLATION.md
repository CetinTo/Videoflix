# Videoflix Backend - Installations-Anleitung für Linux

Diese Anleitung zeigt dir, wie du das Videoflix Django Backend auf einem Linux-Server einrichtest.

## Schritt 1: System-Voraussetzungen installieren

### Ubuntu/Debian

```bash
# System aktualisieren
sudo apt update && sudo apt upgrade -y

# Python 3.12 installieren
sudo apt install python3.12 python3.12-venv python3-pip -y

# PostgreSQL installieren
sudo apt install postgresql postgresql-contrib -y

# Redis installieren
sudo apt install redis-server -y

# FFmpeg installieren (für Video-Verarbeitung)
sudo apt install ffmpeg -y

# Weitere Tools
sudo apt install nginx git curl -y
```

### CentOS/RHEL

```bash
# System aktualisieren
sudo yum update -y

# Python 3.12 installieren
sudo yum install python312 python312-pip -y

# PostgreSQL installieren
sudo yum install postgresql-server postgresql-contrib -y
sudo postgresql-setup initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Redis installieren
sudo yum install redis -y
sudo systemctl start redis
sudo systemctl enable redis

# FFmpeg installieren
sudo yum install epel-release -y
sudo yum install ffmpeg -y

# Nginx installieren
sudo yum install nginx -y
```

## Schritt 2: PostgreSQL einrichten

```bash
# PostgreSQL Shell öffnen
sudo -u postgres psql

# In der PostgreSQL Shell:
CREATE DATABASE videoflix_db;
CREATE USER videoflix_user WITH PASSWORD 'dein_sicheres_passwort';
ALTER ROLE videoflix_user SET client_encoding TO 'utf8';
ALTER ROLE videoflix_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE videoflix_user SET timezone TO 'Europe/Berlin';
GRANT ALL PRIVILEGES ON DATABASE videoflix_db TO videoflix_user;
\q

# PostgreSQL neu starten
sudo systemctl restart postgresql
```

## Schritt 3: Redis konfigurieren

```bash
# Redis starten und aktivieren
sudo systemctl start redis
sudo systemctl enable redis

# Redis testen
redis-cli ping
# Sollte "PONG" zurückgeben
```

## Schritt 4: Projekt einrichten

```bash
# Projektverzeichnis erstellen
sudo mkdir -p /var/www/videoflix
cd /var/www/videoflix

# Repository klonen (oder Dateien hochladen)
# Wenn du Git verwendest:
# git clone https://github.com/dein-repo/videoflix.git .

# Dateien per SFTP/SCP hochladen:
# scp -r /pfad/zu/Videoflix/* user@server:/var/www/videoflix/

# Berechtigungen setzen
sudo chown -R $USER:$USER /var/www/videoflix

# Virtual Environment erstellen
python3.12 -m venv venv

# Virtual Environment aktivieren
source venv/bin/activate

# Dependencies installieren
pip install --upgrade pip
pip install -r requirements.txt
```

## Schritt 5: .env Datei konfigurieren

```bash
# .env Datei erstellen
nano .env

# Folgende Werte eintragen (für Production):
SECRET_KEY="dein-super-geheimer-key-hier"
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your-server-ip
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

DB_NAME=videoflix_db
DB_USER=videoflix_user
DB_PASSWORD=dein_sicheres_passwort
DB_HOST=localhost
DB_PORT=5432

REDIS_HOST=localhost
REDIS_LOCATION=redis://localhost:6379/1
REDIS_PORT=6379
REDIS_DB=0

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=deine-email@gmail.com
EMAIL_HOST_PASSWORD=dein-app-passwort
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# SECRET_KEY generieren mit:
# python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Schritt 6: Django einrichten

```bash
# Migrations erstellen und ausführen
python manage.py makemigrations
python manage.py migrate

# Superuser erstellen
python manage.py createsuperuser

# Statische Dateien sammeln
python manage.py collectstatic --noinput

# Verzeichnisse erstellen
mkdir -p logs
mkdir -p media/videos
mkdir -p media/thumbnails
mkdir -p media/profile_pictures

# Berechtigungen setzen
chmod -R 755 media/
chmod -R 755 staticfiles/
chmod -R 755 logs/
```

## Schritt 7: Gunicorn konfigurieren

```bash
# Gunicorn Socket File erstellen
sudo nano /etc/systemd/system/gunicorn.socket
```

Inhalt:
```ini
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
```

```bash
# Gunicorn Service File erstellen
sudo nano /etc/systemd/system/gunicorn.service
```

Inhalt:
```ini
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=dein-username
Group=www-data
WorkingDirectory=/var/www/videoflix
ExecStart=/var/www/videoflix/venv/bin/gunicorn \
          --access-logfile - \
          --workers 4 \
          --timeout 120 \
          --bind unix:/run/gunicorn.sock \
          videoflix.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
# Services starten und aktivieren
sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket
sudo systemctl status gunicorn.socket

# Gunicorn testen
sudo systemctl status gunicorn
```

## Schritt 8: RQ Worker als Service einrichten

```bash
# RQ Worker Service erstellen
sudo nano /etc/systemd/system/rqworker.service
```

Inhalt:
```ini
[Unit]
Description=Django RQ Worker
After=network.target

[Service]
User=dein-username
Group=www-data
WorkingDirectory=/var/www/videoflix
ExecStart=/var/www/videoflix/venv/bin/python manage.py rqworker default
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Service starten
sudo systemctl start rqworker
sudo systemctl enable rqworker
sudo systemctl status rqworker
```

## Schritt 9: Nginx konfigurieren

```bash
# Nginx Konfiguration erstellen
sudo nano /etc/nginx/sites-available/videoflix
```

Inhalt:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    client_max_body_size 500M;  # Max. Upload-Größe für Videos

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /var/www/videoflix/staticfiles/;
    }

    location /media/ {
        alias /var/www/videoflix/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
    }
}
```

```bash
# Konfiguration aktivieren
sudo ln -s /etc/nginx/sites-available/videoflix /etc/nginx/sites-enabled/

# Nginx testen und neu starten
sudo nginx -t
sudo systemctl restart nginx
```

## Schritt 10: SSL mit Let's Encrypt (Optional, aber empfohlen)

```bash
# Certbot installieren
sudo apt install certbot python3-certbot-nginx -y

# SSL Zertifikat erhalten
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-Renewal testen
sudo certbot renew --dry-run
```

## Schritt 11: Firewall konfigurieren

```bash
# UFW Firewall (Ubuntu/Debian)
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable

# Firewalld (CentOS/RHEL)
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

## Wartung & Nützliche Befehle

```bash
# Gunicorn neu starten
sudo systemctl restart gunicorn

# RQ Worker neu starten
sudo systemctl restart rqworker

# Nginx neu starten
sudo systemctl restart nginx

# Logs anschauen
sudo journalctl -u gunicorn
sudo journalctl -u rqworker
tail -f logs/django.log

# Django Shell
cd /var/www/videoflix
source venv/bin/activate
python manage.py shell

# Migrations
python manage.py makemigrations
python manage.py migrate

# Cache leeren
python manage.py shell -c "from django.core.cache import cache; cache.clear()"
```

## Troubleshooting

### Permission Denied Fehler
```bash
sudo chown -R $USER:www-data /var/www/videoflix
sudo chmod -R 755 /var/www/videoflix
```

### Gunicorn läuft nicht
```bash
sudo systemctl status gunicorn
sudo journalctl -u gunicorn -n 50
```

### Video-Upload funktioniert nicht
```bash
# Prüfe ffmpeg
ffmpeg -version

# Prüfe RQ Worker
sudo systemctl status rqworker
```

### Datenbank-Verbindung fehlgeschlagen
```bash
# PostgreSQL Status
sudo systemctl status postgresql

# Verbindung testen
psql -h localhost -U videoflix_user -d videoflix_db
```

## Performance-Optimierung

1. **Gunicorn Workers erhöhen**: `--workers 8` (2-4 × CPU Cores)
2. **Redis maxmemory setzen**: In `/etc/redis/redis.conf`
3. **PostgreSQL tunen**: connection_limit, shared_buffers
4. **Nginx Caching** aktivieren für statische Dateien

---

**Fertig!** Dein Videoflix Backend läuft jetzt auf Linux! 🎉

Zugriff:
- Frontend: `https://yourdomain.com`
- Admin: `https://yourdomain.com/admin/`
- API Docs: `https://yourdomain.com/api/docs/`
