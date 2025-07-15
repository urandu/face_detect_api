# Production Deployment Guide

This guide walks you through deploying the Face Detection API in a production environment using Docker Compose.

## Prerequisites

- Docker Engine 20.10+ and Docker Compose 2.0+
- At least 4GB RAM and 20GB disk space
- Domain name and SSL certificates (for HTTPS)
- Basic understanding of Docker and web server configuration

## Quick Start

### 1. Clone and Prepare Environment

```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd face_detect_api

# Copy and configure environment file
cp .env.prod.template .env
# Edit .env with your production values
nano .env
```

### 2. Configure Environment Variables

Edit the `.env` file and set all required variables:

```bash
# Generate a Django secret key
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Set strong passwords for all services
SECRET_KEY=your-generated-secret-key
DATABASE_PASSWORD=your-secure-db-password
REDIS_PASSWORD=your-secure-redis-password
RABBITMQ_PASSWORD=your-secure-rabbitmq-password
MINIO_ROOT_PASSWORD=your-secure-minio-password
```

### 3. SSL Certificates (HTTPS)

For production, you need SSL certificates:

```bash
# Option 1: Use Let's Encrypt (recommended)
sudo certbot certonly --standalone -d yourdomain.com
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ./certs/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ./certs/key.pem

# Option 2: Self-signed for testing
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout certs/key.pem \
    -out certs/cert.pem \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=yourdomain.com"

# Set proper permissions
chmod 600 certs/*.pem
```

### 4. Update Configuration for Your Domain

Edit `face_detect_api/settings_prod.py`:

```python
ALLOWED_HOSTS = [
    'yourdomain.com',
    'api.yourdomain.com',
    # Add your actual domain
]

# Enable HTTPS security (uncomment these lines)
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

Edit `nginx/conf.d/default.conf`:

```nginx
server {
    listen 80;
    server_name yourdomain.com;  # Replace with your domain
    return 301 https://$server_name$request_uri;  # Redirect to HTTPS
}

# Uncomment and configure the HTTPS server block
```

### 5. Deploy the Application

```bash
# Build and start all services
docker-compose -f docker-compose.prod.yml up -d --build

# Check all services are healthy
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### 6. Initialize the Database

```bash
# Run migrations
docker-compose -f docker-compose.prod.yml exec api python manage.py migrate

# Create a superuser
docker-compose -f docker-compose.prod.yml exec api python manage.py createsuperuser

# Collect static files
docker-compose -f docker-compose.prod.yml exec api python manage.py collectstatic --noinput
```

### 7. Verify Deployment

```bash
# Test the health endpoint
curl http://yourdomain.com/health

# Test the API health check
curl http://yourdomain.com/api/health/

# Access the admin interface
open https://yourdomain.com/admin/
```

## Architecture Overview

### Services

- **nginx**: Reverse proxy, load balancer, SSL termination
- **api**: Django application server (Gunicorn)
- **worker**: Celery workers for background tasks
- **database**: PostgreSQL database
- **redis**: Cache and Celery result backend
- **broker**: RabbitMQ message broker
- **minio**: S3-compatible object storage

### Networks

- **internal**: Backend services communication
- **external**: External access through Nginx

### Volumes

- **postgres_data**: Database persistence
- **redis_data**: Redis persistence
- **rabbitmq_data**: RabbitMQ persistence
- **minio_data**: Object storage persistence
- **static_files**: Django static files
- **media_files**: Uploaded media files

## Configuration Details

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SECRET_KEY` | Django secret key | Yes | - |
| `DATABASE_PASSWORD` | PostgreSQL password | Yes | - |
| `REDIS_PASSWORD` | Redis password | Yes | - |
| `RABBITMQ_PASSWORD` | RabbitMQ password | Yes | - |
| `MINIO_ROOT_PASSWORD` | MinIO password | Yes | - |
| `API_PORT` | HTTP port | No | 80 |
| `API_SSL_PORT` | HTTPS port | No | 443 |

### Security Features

- **HTTPS enforcement** (when configured)
- **Security headers** (HSTS, XSS protection, etc.)
- **Rate limiting** on API endpoints
- **Non-root containers**
- **Network isolation**
- **Health checks** for all services

### Performance Optimizations

- **Multi-stage Docker builds** for smaller images
- **Nginx gzip compression**
- **Static file caching**
- **Database connection pooling**
- **Celery worker concurrency**

## Monitoring and Maintenance

### Health Checks

All services include health checks accessible via:

```bash
# Overall health
curl http://yourdomain.com/health

# API health (database, cache)
curl http://yourdomain.com/api/health/

# Service status
docker-compose -f docker-compose.prod.yml ps
```

### Logs

```bash
# View all logs
docker-compose -f docker-compose.prod.yml logs

# Follow specific service logs
docker-compose -f docker-compose.prod.yml logs -f api
docker-compose -f docker-compose.prod.yml logs -f worker
docker-compose -f docker-compose.prod.yml logs -f nginx
```

### Backup Strategy

```bash
# Database backup
docker-compose -f docker-compose.prod.yml exec database pg_dump -U django django_prod > backup.sql

# Volume backup
docker run --rm -v face_detect_api_postgres_data:/data -v $(pwd):/backup ubuntu tar czf /backup/postgres_backup.tar.gz /data
```

### Updates and Maintenance

```bash
# Update application
git pull
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# Update dependencies
docker-compose -f docker-compose.prod.yml exec api pip install -r requirements.txt

# Run migrations
docker-compose -f docker-compose.prod.yml exec api python manage.py migrate
```

## Scaling

### Horizontal Scaling

Scale specific services:

```bash
# Scale API servers
docker-compose -f docker-compose.prod.yml up -d --scale api=3

# Scale workers
docker-compose -f docker-compose.prod.yml up -d --scale worker=5
```

### Load Balancing

Nginx automatically load balances between multiple API containers. For multiple Nginx instances, use an external load balancer.

## Troubleshooting

### Common Issues

1. **Container won't start**
   ```bash
   docker-compose -f docker-compose.prod.yml logs <service>
   ```

2. **Database connection errors**
   - Check environment variables
   - Verify database service is healthy
   - Check network connectivity

3. **SSL/HTTPS issues**
   - Verify certificate files exist and are readable
   - Check Nginx configuration
   - Ensure domain DNS is correctly configured

4. **API errors**
   - Check Django logs
   - Verify all migrations are applied
   - Check environment variable configuration

### Performance Issues

1. **High memory usage**
   - Reduce Celery worker concurrency
   - Optimize image processing tasks
   - Monitor database queries

2. **Slow responses**
   - Check database performance
   - Monitor Celery queue length
   - Review Nginx access logs

## Security Considerations

### Production Checklist

- [ ] Change all default passwords
- [ ] Use HTTPS with valid certificates
- [ ] Configure firewall rules
- [ ] Regular security updates
- [ ] Monitor access logs
- [ ] Backup strategy in place
- [ ] Secret management
- [ ] Network segmentation

### Regular Maintenance

- **Weekly**: Review logs and monitor performance
- **Monthly**: Update dependencies and security patches
- **Quarterly**: Review and rotate secrets
- **Yearly**: Certificate renewal and security audit

## Support

For issues and questions:

1. Check the logs first
2. Review this documentation
3. Check the Django and Docker documentation
4. Create an issue in the project repository

## Performance Tuning

### Recommended Production Settings

```yaml
# In docker-compose.prod.yml, adjust resources:
deploy:
  resources:
    limits:
      memory: 512M
    reservations:
      memory: 256M
```

### Database Optimization

```python
# In settings_prod.py
DATABASES = {
    'default': {
        # ...
        'CONN_MAX_AGE': 600,  # Connection pooling
        'OPTIONS': {
            'MAX_CONNS': 20,
        }
    }
}
```

### Celery Optimization

```python
# Adjust worker concurrency based on your hardware
CELERY_WORKER_CONCURRENCY = 4  # Number of CPU cores
```
