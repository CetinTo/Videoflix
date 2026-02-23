#!/bin/bash

# Videoflix Backend Setup Script
# Für lokale Entwicklung

echo "=========================================="
echo "Videoflix Backend Setup"
echo "=========================================="
echo ""

# Farben
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Virtual Environment erstellen
echo -e "${YELLOW}1. Erstelle Virtual Environment...${NC}"
python3 -m venv venv
source venv/bin/activate

echo -e "${GREEN}✓ Virtual Environment erstellt${NC}"
echo ""

# Dependencies installieren
echo -e "${YELLOW}2. Installiere Dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${GREEN}✓ Dependencies installiert${NC}"
echo ""

# .env Datei prüfen
if [ ! -f .env ]; then
    echo -e "${YELLOW}3. Erstelle .env Datei...${NC}"
    cp .env.template .env
    echo -e "${GREEN}✓ .env Datei erstellt${NC}"
    echo -e "${YELLOW}⚠ Bitte .env Datei bearbeiten und Werte anpassen!${NC}"
else
    echo -e "${GREEN}✓ .env Datei existiert bereits${NC}"
fi
echo ""

# Verzeichnisse erstellen
echo -e "${YELLOW}4. Erstelle notwendige Verzeichnisse...${NC}"
mkdir -p logs
mkdir -p media/videos
mkdir -p media/thumbnails
mkdir -p media/profile_pictures
mkdir -p staticfiles

echo -e "${GREEN}✓ Verzeichnisse erstellt${NC}"
echo ""

# Migrations
echo -e "${YELLOW}5. Führe Migrations aus...${NC}"
python manage.py makemigrations
python manage.py migrate

echo -e "${GREEN}✓ Migrations abgeschlossen${NC}"
echo ""

# Statische Dateien
echo -e "${YELLOW}6. Sammle statische Dateien...${NC}"
python manage.py collectstatic --noinput

echo -e "${GREEN}✓ Statische Dateien gesammelt${NC}"
echo ""

# Superuser erstellen
echo -e "${YELLOW}7. Möchtest du einen Superuser erstellen? (j/n)${NC}"
read -r create_superuser
if [ "$create_superuser" = "j" ] || [ "$create_superuser" = "J" ]; then
    python manage.py createsuperuser
    echo -e "${GREEN}✓ Superuser erstellt${NC}"
fi
echo ""

echo "=========================================="
echo -e "${GREEN}Setup abgeschlossen!${NC}"
echo "=========================================="
echo ""
echo "Nächste Schritte:"
echo "1. Bearbeite die .env Datei mit deinen Werten"
echo "2. Starte PostgreSQL und Redis"
echo "3. Starte den Server mit: python manage.py runserver"
echo "4. Starte RQ Worker mit: python manage.py rqworker default"
echo ""
echo "Zugriff:"
echo "- Admin: http://localhost:8000/admin/"
echo "- API Docs: http://localhost:8000/api/docs/"
echo "- RQ Dashboard: http://localhost:8000/django-rq/"
echo ""
