# Docker Troubleshooting Guide

## First-Time Installation Issues

### Problem: Entrypoint script not found
**Error:** `exec /docker-entrypoint.sh: no such file or directory`

**Symptoms:**
- Web container starts and immediately stops
- Error appears in logs: "exec /docker-entrypoint.sh: no such file or directory"
- Container status shows "Exited (1)"

**Cause:**
This happens when the `docker-entrypoint.sh` file has Windows line endings (CRLF) instead of Unix line endings (LF). Docker/Linux cannot execute scripts with Windows line endings.

**Solution:**
The Dockerfile now automatically fixes this during build. Simply rebuild:
```cmd
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

**Why this happens:**
- Windows editors (Notepad, some Git configurations) add CRLF line endings
- Linux/Docker requires LF line endings for shell scripts
- The `.gitattributes` file now prevents this for future clones

**Prevention:**
- The project now includes `.gitattributes` to ensure proper line endings
- The Dockerfile contains `sed -i 's/\r$//'` to auto-convert during build
- Clone with Git (don't download as ZIP) to preserve line endings

### Problem: `.env` file missing error
**Solution:**
1. Run `docker-start.bat` - it will automatically create `.env` from `.env.example`
2. If the error persists, manually copy:
   ```cmd
   copy .env.example .env
   ```

### Problem: Database connection errors on first run
**Symptoms:**
- "database does not exist"
- "connection refused"
- "authentication failed"

**Solution:**
The improved entrypoint script now handles this automatically:
1. Stop containers: `docker-compose down -v`
2. Run fresh install: `docker-start.bat`
3. Wait 10-15 seconds for initialization

**What the script does:**
- ✅ Validates environment variables
- ✅ Waits for PostgreSQL to be ready (max 60 seconds)
- ✅ Creates database if it doesn't exist
- ✅ Runs migrations
- ✅ Collects static files
- ✅ Creates superuser automatically

### Problem: Entrypoint script fails on second run
**Symptoms:**
- "Superuser already exists" errors
- Migration conflicts
- Static files errors

**Solution:**
The script is now idempotent (can run multiple times safely):
- Checks if database exists before creating
- Checks if superuser exists before creating
- Handles migration conflicts gracefully

## Common Issues

### 1. Port Already in Use

**Error:** "port is already allocated"

**Solution:**
```cmd
REM Check what's using the port
netstat -ano | findstr :8000
netstat -ano | findstr :5432

REM Kill the process or change ports in docker-compose.yml
```

### 2. Docker Desktop Not Running

**Error:** "error during connect"

**Solution:**
1. Start Docker Desktop
2. Wait for it to fully start (whale icon should be steady)
3. Run `docker-start.bat` again

### 3. Permission Denied Errors

**Error:** "permission denied" when accessing files

**Solution:**
```cmd
REM Run as Administrator
REM Right-click docker-start.bat → Run as administrator
```

### 4. Out of Disk Space

**Error:** "no space left on device"

**Solution:**
```cmd
REM Clean up Docker
docker system prune -a --volumes

REM Remove unused images
docker image prune -a
```

### 5. Build Failures

**Error:** "failed to build" or "error downloading packages"

**Solution:**
```cmd
REM Clear build cache
docker builder prune -a

REM Rebuild without cache
docker-compose build --no-cache
```

### 6. Database Migration Errors

**Error:** "migration conflicts" or "table already exists"

**Solution:**
```cmd
REM Reset database (WARNING: deletes all data)
docker-compose down -v
docker-compose up -d db
timeout /t 5
docker-compose exec web python manage.py migrate --run-syncdb
```

### 7. Static Files Not Loading

**Error:** CSS/JS files not loading

**Solution:**
```cmd
REM Recollect static files
docker-compose exec web python manage.py collectstatic --noinput --clear

REM Or rebuild
docker-compose down
docker-compose up -d --build
```

## Fresh Install Testing

To test the first-time installation experience:

```cmd
REM Use the provided test script
docker-test-fresh.bat
```

This script will:
1. Backup your existing `.env` (if exists)
2. Remove `.env` to simulate fresh install
3. Stop all containers
4. Run complete setup from scratch
5. Verify everything works

## Verification Steps

After running `docker-start.bat`, verify:

1. **Containers are running:**
   ```cmd
   docker-compose ps
   ```
   Both `web` and `db` should be "Up"

2. **Database is accessible:**
   ```cmd
   docker-compose exec db psql -U lms_user -d lms_nalanda_db -c "\dt"
   ```

3. **Web server is responding:**
   ```cmd
   curl http://localhost:8000
   ```
   Or open in browser

4. **Admin access works:**
   - Go to http://localhost:8000/admin
   - Login with: admin / admin123

5. **Check logs for errors:**
   ```cmd
   docker-compose logs web
   docker-compose logs db
   ```

## Clean Start (Complete Reset)

If you need to start completely fresh:

```cmd
REM Stop and remove everything
docker-compose down -v

REM Remove images
docker rmi learning-management-system-nalanda-open-university-_web
docker rmi postgres:15-alpine

REM Remove .env (optional - will be recreated)
del .env

REM Fresh install
docker-start.bat
```

## Environment Variables Reference

Required in `.env`:

```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration (Django)
DATABASE_NAME=lms_nalanda_db
DATABASE_USER=lms_user
DATABASE_PASSWORD=lms_password
DATABASE_HOST=db
DATABASE_PORT=5432

# PostgreSQL Configuration
POSTGRES_DB=lms_nalanda_db
POSTGRES_USER=lms_user
POSTGRES_PASSWORD=lms_password
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Superuser Auto-Creation
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@nalanda.edu
DJANGO_SUPERUSER_PASSWORD=admin123
```

## Getting Help

If issues persist:

1. **Check logs:**
   ```cmd
   docker-compose logs -f
   ```

2. **Check container status:**
   ```cmd
   docker-compose ps
   docker inspect <container-id>
   ```

3. **Access container shell:**
   ```cmd
   docker-compose exec web bash
   docker-compose exec db psql -U lms_user -d lms_nalanda_db
   ```

4. **Review this guide:** `DOCKER_SETUP.md`

5. **Create an issue:** Include logs and error messages

## Performance Optimization

If containers are slow:

1. **Increase Docker resources:**
   - Docker Desktop → Settings → Resources
   - Increase CPU and Memory

2. **Use bind mounts selectively:**
   - Comment out code volume mount in production
   - Keep only static/media volumes

3. **Enable BuildKit:**
   ```cmd
   set DOCKER_BUILDKIT=1
   docker-compose build
   ```

## Security Notes

**Before deploying to production:**

1. ✅ Change `SECRET_KEY` in `.env`
2. ✅ Change database passwords
3. ✅ Change admin password
4. ✅ Set `DEBUG=False`
5. ✅ Update `ALLOWED_HOSTS`
6. ✅ Use `docker-compose.prod.yml`
7. ✅ Enable HTTPS
8. ✅ Review firewall settings

## Quick Command Reference

```cmd
REM Start (first time or restart)
docker-start.bat

REM View logs (all services)
docker-compose logs -f

REM View logs (specific service)
docker-compose logs -f web
docker-compose logs -f db

REM Stop containers
docker-compose down

REM Stop and remove volumes (fresh start)
docker-compose down -v

REM Restart containers
docker-compose restart

REM Rebuild and restart
docker-compose up -d --build

REM Access web container shell
docker-compose exec web bash

REM Access database
docker-compose exec db psql -U lms_user -d lms_nalanda_db

REM Run Django management commands
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic

REM View container status
docker-compose ps

REM View resource usage
docker stats

REM Clean up
docker system prune -a --volumes
```
