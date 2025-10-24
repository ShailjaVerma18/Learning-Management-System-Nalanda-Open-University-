# 🐳 LMS - Docker Setup Guide

> **🚀 Quick Start:** 1) Start Docker Desktop → 2) Double-click `docker-start.bat` → 3) Open http://localhost:8000 
<!-- → Login: admin/admin123 -->

---

Complete guide to run the Learning Management System in Docker containers.

## 📋 Prerequisites

- **Docker Desktop** - [Download](https://www.docker.com/products/docker-desktop/)
- **Git** - [Download](https://git-scm.com/)
- **8GB RAM minimum** (recommended)
- **10GB free disk space**

## 🚀 Quick Start (Windows)

### Option 1: Automated Setup (Recommended)

1. **Start Docker Desktop**

2. **Double-click `docker-start.bat`**
   - This will automatically build and start everything
   - Wait for "Setup Complete!" message

3. **Access the application:**
   - URL: http://localhost:8000
   <!-- - Admin: `admin` / `admin123` -->

### Option 2: Manual Setup

1. **Start Docker Desktop**

2. **Open Command Prompt in project folder:**
   ```cmd
   cd "G:\git project\open source\New\Learning-Management-System-Nalanda-Open-University-"
   ```

3. **Build and start:**
   ```cmd
   docker-compose up --build -d
   ```

4. **Wait 30 seconds** for initialization

5. **Open browser:**
   ```
   http://localhost:8000
   ```

## 📊 Project Understanding

### Architecture
```
┌─────────────────┐         ┌──────────────────┐
│   Web Browser   │ ──────▶ │  Django Web App  │
│  (Port 8000)    │         │   (Container)    │
└─────────────────┘         └──────────────────┘
                                     │
                                     ▼
                            ┌──────────────────┐
                            │   PostgreSQL DB  │
                            │   (Container)    │
                            └──────────────────┘
```

### Components

1. **Web Container (`web`)**
   - Django 4.x application
   - Python 3.11
   - Runs on port 8000
   - Auto-migrates database
   - Creates admin user automatically

2. **Database Container (`db`)**
   - PostgreSQL 15 (Alpine Linux)
   - Data persists in Docker volume
   - Port 5432 (internal)

3. **Volumes**
   - `postgres_data`: Database files
   - `static_volume`: CSS, JS, images
   - `media_volume`: User uploads

### Key Files

| File | Purpose |
|------|---------|
| `Dockerfile` | Defines web container image |
| `docker-compose.yml` | Orchestrates all services |
| `docker-entrypoint.sh` | Startup script (migrations, etc.) |
| `.env` | Environment configuration |
| `requirements.docker.txt` | Python dependencies (lightweight) |

## 🛠️ Docker Commands Reference

### Container Management

```cmd
# Start services
docker-compose up

# Start in background (detached)
docker-compose up -d

# Stop services
docker-compose down

# Stop and remove all data (⚠️ CAUTION)
docker-compose down -v

# Restart services
docker-compose restart

# Rebuild after code changes
docker-compose up --build

# View running containers
docker-compose ps

# View resource usage
docker stats
```

### Logs & Debugging

```cmd
# View all logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# View logs for specific service
docker-compose logs web
docker-compose logs db

# Last 50 lines
docker-compose logs --tail=50 web

# Check container health
docker-compose ps
```

### Django Management

```cmd
# Access Django shell
docker-compose exec web python manage.py shell

# Create superuser manually
docker-compose exec web python manage.py createsuperuser

# Run migrations
docker-compose exec web python manage.py migrate

# Create migrations
docker-compose exec web python manage.py makemigrations

# Collect static files
docker-compose exec web python manage.py collectstatic

# Check Django version
docker-compose exec web python manage.py version
```

### Database Management

```cmd
# Access PostgreSQL CLI
docker-compose exec db psql -U lms_user -d lms_nalanda_db

# Backup database
docker-compose exec db pg_dump -U lms_user lms_nalanda_db > backup.sql

# Restore database
docker-compose exec -T db psql -U lms_user lms_nalanda_db < backup.sql

# View database size
docker-compose exec db psql -U lms_user -d lms_nalanda_db -c "SELECT pg_size_pretty(pg_database_size('lms_nalanda_db'));"
```


## 🔧 Configuration

### Environment Variables (`.env`)

```env
# Development Settings
DEBUG=True
SECRET_KEY=your-secret-key-here

# Database
DATABASE_NAME=lms_nalanda_db
DATABASE_USER=lms_user
DATABASE_PASSWORD=lms_password
DATABASE_HOST=db

# Admin Account
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@nalanda.edu
DJANGO_SUPERUSER_PASSWORD=admin123
```

### Port Configuration

To change the default port (8000):

Edit `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Change 8001 to your desired port
```

### Memory Limits

To add resource limits, edit `docker-compose.yml`:
```yaml
web:
  deploy:
    resources:
      limits:
        memory: 512M
        cpus: '1.0'
```

## 🐛 Troubleshooting

### Docker Desktop Not Running

**Error:** `Cannot connect to the Docker daemon`

**Solution:**
1. Open Docker Desktop application
2. Wait for "Docker Desktop is running" status
3. Try command again

### Port Already in Use

**Error:** `Bind for 0.0.0.0:8000 failed: port is already allocated`

**Solution:**
```cmd
# Option 1: Stop the conflicting service
netstat -ano | findstr :8000

# Option 2: Use different port
# Edit docker-compose.yml, change "8000:8000" to "8001:8000"
```

### Build Failures

**Error:** Package installation fails

**Solution:**
```cmd
# Clean build
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### Database Connection Issues

**Error:** `FATAL: password authentication failed`

**Solution:**
```cmd
# Remove old database volume
docker-compose down -v
docker-compose up
```

### Container Crashes on Startup

**Error:** `exec /docker-entrypoint.sh: no such file or directory`

**Cause:** Windows line endings (CRLF) in shell script instead of Unix (LF)

**Solution:**
```cmd
# Rebuild the image (Dockerfile now auto-fixes line endings)
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

**Alternative (if issue persists):**
The project includes `.gitattributes` to prevent this. If you downloaded as ZIP instead of cloning with Git:
```cmd
# Convert line endings manually (requires Git Bash or WSL)
dos2unix docker-entrypoint.sh
# OR
sed -i 's/\r$//' docker-entrypoint.sh

# Then rebuild
docker-compose build --no-cache
docker-compose up -d
```

**Check logs:**
```cmd
docker-compose logs web
```

**Common fixes:**
```cmd
# Reset everything
docker-compose down -v
docker-compose up --build
```

### Slow Performance

**Solutions:**
1. Allocate more resources in Docker Desktop:
   - Settings → Resources → Advanced
   - Increase CPU/Memory

2. Disable real-time file scanning in antivirus

3. Use WSL 2 backend (Windows 11):
   - Docker Desktop → Settings → General
   - Enable "Use the WSL 2 based engine"

## 📈 What Happens on First Run

1. **Docker pulls base images** (~2-3 minutes)
   - Python 3.11 slim
   - PostgreSQL 15 Alpine

2. **Builds web container** (~3-5 minutes)
   - Installs system dependencies
   - Installs Python packages
   - Copies project files

3. **Starts services**
   - Database container starts
   - Waits for DB to be ready

4. **Runs initialization**
   - Database migrations
   - Collects static files
   - Creates admin user

5. **Application ready!** (~30 seconds)

Total time: 5-8 minutes on first run
Subsequent starts: <30 seconds


## 📝 Development Workflow

### Making Code Changes

1. Edit files normally on your computer
2. Changes are automatically reflected (volume mount)
3. For Python changes, restart:
   ```cmd
   docker-compose restart web
   ```

### Adding Dependencies

1. Add to `requirements.docker.txt`
2. Rebuild:
   ```cmd
   docker-compose build web
   docker-compose up -d
   ```

### Database Changes

1. Make model changes
2. Create migrations:
   ```cmd
   docker-compose exec web python manage.py makemigrations
   ```
3. Apply migrations:
   ```cmd
   docker-compose exec web python manage.py migrate
   ```

## 🆘 Support & Help

### Quick Fixes

```cmd
# Reset everything (CAUTION: deletes data)
docker-compose down -v
docker-compose up --build

# View full error logs
docker-compose logs --tail=100 web

# Check if ports are available
netstat -ano | findstr :8000
netstat -ano | findstr :5432

# Free up disk space
docker system prune -a
```

### Common Issues

| Issue | Solution |
|-------|----------|
| "Cannot find module" | Rebuild: `docker-compose build --no-cache` |
| "Port already in use" | Change port in docker-compose.yml |
| "Permission denied" | Run as administrator or check Docker Desktop settings |
| "Out of disk space" | Clean: `docker system prune -a` |

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Django in Docker](https://docs.docker.com/samples/django/)
- [PostgreSQL Docker](https://hub.docker.com/_/postgres)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)

## 🎯 Next Steps

After successful setup:

1. ✅ Access http://localhost:8000
2. ✅ Login with admin/admin123
3. ✅ Explore admin panel
4. ✅ Create test data
5. ✅ Test student registration
6. ✅ Upload course materials
7. ✅ Try the chatbot

---

**Need help?** Check logs: `docker-compose logs -f`  
**Everything working?** Start developing! 🚀
