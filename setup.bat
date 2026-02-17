@echo off
REM Videoflix Backend Setup Script für Windows

echo ==========================================
echo Videoflix Backend Setup
echo ==========================================
echo.

REM Virtual Environment erstellen
echo 1. Erstelle Virtual Environment...
python -m venv venv
call venv\Scripts\activate.bat

echo [OK] Virtual Environment erstellt
echo.

REM Dependencies installieren
echo 2. Installiere Dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo [OK] Dependencies installiert
echo.

REM .env Datei prüfen
if not exist .env (
    echo 3. Erstelle .env Datei...
    copy .env.template .env
    echo [OK] .env Datei erstellt
    echo [!] Bitte .env Datei bearbeiten und Werte anpassen!
) else (
    echo [OK] .env Datei existiert bereits
)
echo.

REM Verzeichnisse erstellen
echo 4. Erstelle notwendige Verzeichnisse...
if not exist logs mkdir logs
if not exist media\videos mkdir media\videos
if not exist media\thumbnails mkdir media\thumbnails
if not exist media\profile_pictures mkdir media\profile_pictures
if not exist staticfiles mkdir staticfiles

echo [OK] Verzeichnisse erstellt
echo.

REM Migrations
echo 5. Fuehre Migrations aus...
python manage.py makemigrations
python manage.py migrate

echo [OK] Migrations abgeschlossen
echo.

REM Statische Dateien
echo 6. Sammle statische Dateien...
python manage.py collectstatic --noinput

echo [OK] Statische Dateien gesammelt
echo.

REM Superuser erstellen
set /p create_superuser="7. Moechtest du einen Superuser erstellen? (j/n): "
if /i "%create_superuser%"=="j" (
    python manage.py createsuperuser
    echo [OK] Superuser erstellt
)
echo.

echo ==========================================
echo Setup abgeschlossen!
echo ==========================================
echo.
echo Naechste Schritte:
echo 1. Bearbeite die .env Datei mit deinen Werten
echo 2. Starte PostgreSQL und Redis
echo 3. Starte den Server mit: python manage.py runserver
echo 4. Starte RQ Worker mit: python manage.py rqworker default
echo.
echo Zugriff:
echo - Admin: http://localhost:8000/admin/
echo - API Docs: http://localhost:8000/api/docs/
echo - RQ Dashboard: http://localhost:8000/django-rq/
echo.
pause
