@echo off
echo ========================================
echo Nalanda LMS - Docker Setup
echo ========================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo Docker is running...
echo.

REM Stop any existing containers
echo Stopping existing containers...
docker-compose down
echo.

REM Build the images
echo Building Docker images...
docker-compose build
if %errorlevel% neq 0 (
    echo ERROR: Docker build failed!
    pause
    exit /b 1
)
echo.

REM Start the containers
echo Starting containers...
docker-compose up -d
if %errorlevel% neq 0 (
    echo ERROR: Failed to start containers!
    pause
    exit /b 1
)
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Application is starting up...
echo Please wait 30 seconds for initialization.
echo.
echo Access the application at:
echo   http://localhost:8000
echo.
echo Admin credentials:
echo   Username: admin
echo   Password: admin123
echo.
echo To view logs: docker-compose logs -f
echo To stop: docker-compose down
echo.
pause
