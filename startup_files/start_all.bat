@echo off
echo Starting Re-Style Application...
echo.

echo Starting all Docker services (PostgreSQL, Redis, Django, Celery)...
docker-compose up -d

echo.
echo 🎉 All services are starting up!
echo.
echo Services running:
echo - PostgreSQL database
echo - Redis cache
echo - Django backend (port 8000)
echo - Celery worker
echo - Celery beat scheduler
echo - Celery monitor/Flower (port 5555)
echo.
echo Starting React frontend...
start cmd /k "cd frontend && npm start"

echo Starting mobile app...
start cmd /k "cd restyle-mobile && npx expo start"

echo.
echo 🌐 Access points:
echo Frontend: http://localhost:3000
echo Backend API: http://localhost:8000
echo Admin Panel: http://localhost:8000/admin
echo Celery Monitor: http://localhost:5555
echo Mobile App: Scan QR code in the mobile terminal
echo.
pause 