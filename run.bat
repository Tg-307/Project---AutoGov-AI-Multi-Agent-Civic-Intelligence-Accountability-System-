@echo off
echo.
echo ========================================
echo    AutoGov AI -- Setup and Launch
echo ========================================
echo.

echo [1/4] Installing dependencies...
pip install -r requirements.txt

echo [2/4] Running database migrations...
python manage.py migrate --run-syncdb

echo [3/4] Seeding departments...
python manage.py seed_departments

echo [4/4] Starting server at http://127.0.0.1:8000
echo       Press Ctrl+C to stop.
echo.
python manage.py runserver 127.0.0.1:8000
