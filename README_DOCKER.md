# 🐳 Sudur Chinari Backend - Docker Deployment Guide

This repository contains the complete Django REST Framework backend for Sudur Chinari, containerized with Gunicorn, PostgreSQL, and automatic migrations/seeding.

---

## 🚀 Quick Start

### 1. Copy Environment Variables
```bash
cp .env.example .env
nano .env   # Configure SECRET_KEY, DB password, admin credentials
```

### 2. Start the Backend & Database
```bash
docker compose up -d --build
```

### 3. Check Logs & Health
```bash
# View startup logs (migrations, collectstatic, auto-seed)
docker compose logs -f backend

# Check status of containers
docker compose ps
```

---

## 🌐 Endpoints & Admin

Once running:
- **API Root**: `http://<vps-ip>:8000/api/v1/`
- **Django Admin**: `http://<vps-ip>:8000/admin/` (login with your configured `DJANGO_SUPERUSER_USERNAME` and `DJANGO_SUPERUSER_PASSWORD`)
- **API Documentation / Sitemap**: `http://<vps-ip>:8000/api/sitemap/`

---

## 🛠️ Management Commands

Run Django management commands inside the running container:

```bash
# Create additional superuser
docker compose exec backend python manage.py createsuperuser

# Re-run seeding commands manually
docker compose exec backend python manage.py seed_mock_data
docker compose exec backend python manage.py seed_menu_categories
docker compose exec backend python manage.py seed_district_partners
docker compose exec backend python manage.py update_translation_fields

# Run Django tests inside container
docker compose exec backend python manage.py test api

# Run database migrations manually
docker compose exec backend python manage.py migrate
```

---

## 💾 Database & Media Backups

### Database Backup (PostgreSQL):
```bash
docker compose exec -T db pg_dump -U postgres sudur_chinari > backup_$(date +%F).sql
```

### Database Restore:
```bash
cat backup_YYYY-MM-DD.sql | docker compose exec -T db psql -U postgres -d sudur_chinari
```

### Media Backup:
```bash
docker run --rm --volumes-from sudur_backend -v $(pwd):/backup alpine tar czf /backup/media_$(date +%F).tar.gz /app/media
```

---

## 🔗 Connecting to the Frontend Container

If the frontend is running on the **same VPS**:
- Both `Sudur-Chinari-Backend/docker-compose.yml` and `Sudur-Chinari-Frontend/docker-compose.yml` share the Docker bridge network named `sudur_network`.
- The frontend container can reach this backend directly at:
  ```
  DJANGO_API_URL=http://sudur_backend:8000
  ```

If the frontend is running on a **different VPS** or via a domain:
- Set `DJANGO_API_URL=https://api.yourdomain.com` (or `http://<backend-vps-ip>:8000`).
