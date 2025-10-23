@echo off
echo ========================================
echo Nalanda LMS - Docker Setup
echo ========================================
echo.

REM Check if .env file exists, if not create from .env.example
if not exist .env (
    echo [SETUP] Creating .env file from .env.example...
    if not exist .env.example (
        echo ERROR: .env.example file not found!
        echo Please ensure .env.example exists in the project directory.
        pause
        exit /b 1
    )
    copy .env.example .env >nul
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create .env file!
        pause
        exit /b 1
    )
    echo [SUCCESS] .env file created successfully!
    echo.
    echo IMPORTANT: Please review the .env file and update the following:
    echo   - SECRET_KEY (generate a new one for production)
    echo   - DATABASE credentials (if needed)
    echo   - DJANGO_SUPERUSER credentials (default: admin/admin123)
    echo.
    echo Press any key to continue with Docker setup...
    pause >nul
    echo.
) else (
    echo [INFO] .env file already exists.
    echo.
)

REM Check if Docker is running
echo [CHECK] Verifying Docker Desktop is running...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Docker is not running!
    echo.
    echo Please follow these steps:
    echo   1. Start Docker Desktop
    echo   2. Wait for Docker to fully start
    echo   3. Run this script again
    echo.
    pause
    exit /b 1
)

echo [SUCCESS] Docker is running!
echo.

REM Stop existing containers
echo [DOCKER] Stopping existing containers...
docker-compose down 2>nul
if %errorlevel% neq 0 (
    echo [INFO] No existing containers to stop (first run)
)
echo.

REM Build Docker images
echo [DOCKER] Building Docker images...
echo This may take a few minutes on first run...
docker-compose build
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to build Docker images!
    echo.
    echo Please check:
    echo   1. Docker Desktop has enough resources
    echo   2. No firewall blocking Docker
    echo   3. Internet connection is stable
    echo.
    pause
    exit /b 1
)
echo [SUCCESS] Docker images built successfully!
echo.

REM Start containers
echo [DOCKER] Starting containers...
echo This includes:
echo   - PostgreSQL database
echo   - Django web application
echo.
docker-compose up -d
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to start containers!
    echo.
    echo Troubleshooting:
    echo   1. Check logs: docker-compose logs
    echo   2. Verify .env file has correct values
    echo   3. Ensure ports 8000 and 5432 are not in use
    echo.
    pause
    exit /b 1
)
echo [SUCCESS] Containers started successfully!
echo.

REM Wait for services to initialize
echo [WAIT] Waiting for services to initialize...
timeout /t 10 /nobreak >nul
echo.

REM Show container status
echo [STATUS] Container status:
docker-compose ps
echo.

echo ========================================
echo SUCCESS! Nalanda LMS is running!
echo ========================================
echo.
echo Web Application: http://localhost:8000
echo Database: PostgreSQL on localhost:5432
echo.
echo Default Admin Credentials:
echo   Username: admin
echo   Password: admin123
echo.
echo Useful Commands:
echo   View logs:        docker-compose logs -f
echo   View web logs:    docker-compose logs -f web
echo   View db logs:     docker-compose logs -f db
echo   Stop containers:  docker-compose down
echo   Restart:          docker-compose restart
echo.
echo Press any key to exit...
pause >nul
