# Deployment Guide

Production deployment guide for Videoflix backend.

## Prerequisites

- Ubuntu Server 20.04 or higher
- Docker & Docker Compose
- Domain name
- SSL certificate (Let's Encrypt recommended)

## Step 1: Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose -y

# Add user to docker group
sudo usermod -aG docker $USER
```

## Step 2: Clone Repository

```bash
git clone https://github.com/CetinTo/Videoflix.git
cd Videoflix
```

## Step 3: Configure Environment

```bash
cp .env.template .env
nano .env
```

**Important production settings:**
```env
DEBUG=False
SECRET_KEY=generate-strong-random-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_PASSWORD=strong-db-password
REDIS_PASSWORD=strong-redis-password
```

## Step 4: Start Services

```bash
docker-compose up -d --build
```

## Step 5: Initialize Database

```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py create_admin
docker-compose exec web python manage.py collectstatic --noinput
```

## Step 6: Setup Nginx Reverse Proxy

Install Nginx:
```bash
sudo apt install nginx -y
```

Create Nginx config:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    client_max_body_size 1000M;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /media/ {
        alias /var/www/videoflix/media/;
    }

    location /static/ {
        alias /var/www/videoflix/static/;
    }
}
```

## Step 7: SSL with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

## Step 8: Firewall Setup

```bash
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

## Monitoring

Check logs:
```bash
docker-compose logs -f
```

## Backup Strategy

1. **Database Backup:**
```bash
docker-compose exec db pg_dump -U videoflix_user videoflix_db > backup.sql
```

2. **Media Files Backup:**
```bash
tar -czf media_backup.tar.gz media/
```

## Updates

```bash
git pull origin main
docker-compose down
docker-compose up -d --build
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --noinput
```

## Troubleshooting

- **Container won't start:** Check logs with `docker-compose logs web`
- **Database connection error:** Verify DB credentials in `.env`
- **Video processing fails:** Ensure FFmpeg is installed in container
