# Production Deployment Guide

This guide covers deploying SymptoMap to production environments including cloud platforms, VPS servers, and Kubernetes clusters.

## Table of Contents
- [Server Requirements](#server-requirements)
- [Docker Deployment](#docker-deployment)
- [Cloud Platforms](#cloud-platforms)
- [Database Setup](#database-setup)
- [SSL/TLS Configuration](#ssltls-configuration)
- [Monitoring](#monitoring)
- [Backup & Recovery](#backup--recovery)

## Server Requirements

### Minimum Requirements
- **CPU**: 2 cores
- **RAM**: 4GB
- **Disk**: 20GB SSD
- **OS**: Ubuntu 22.04 LTS (recommended) or any Linux with Docker support

### Recommended for Production
- **CPU**: 4+ cores
- **RAM**: 8GB+
- **Disk**: 50GB+ SSD
- **Network**: 100 Mbps+

### Software Prerequisites
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose-plugin

# Verify installation
docker --version
docker compose version
```

## Docker Deployment

### 1. Initial Setup

```bash
# Clone repository
git clone https://github.com/yourusername/symptomap.git
cd symptomap

# Create production environment file
cp .env.example .env
```

### 2. Configure Environment Variables

Edit `.env` with production settings:

```env
# Database - Use strong passwords!
POSTGRES_PASSWORD=$(openssl rand -base64 32)

# Security - Generate random secrets
JWT_SECRET=$(openssl rand -base64 32)
JWT_REFRESH_SECRET=$(openssl rand -base64 32)

# Production URLs
CORS_ORIGINS=https://symptomap.yourdomain.com
VITE_API_URL=https://api.symptomap.yourdomain.com/api/v1

# Disable debug
DEBUG=false
VITE_ENVIRONMENT=production
```

### 3. Build and Start Services

```bash
# Build images
docker compose build

# Start in detached mode
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f
```

### 4. Verify Deployment

```bash
# Test backend
curl http://localhost:8000/health

# Test frontend
curl http://localhost:3000/health

# Check database
docker compose exec postgres pg_isready
```

## Cloud Platforms

### AWS EC2

1. **Launch Instance**
   - AMI: Ubuntu 22.04 LTS
   - Instance Type: t3.medium (minimum)
   - Security Group: Open ports 80, 443, 22

2. **Setup**
```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Install Docker (see above)
# Clone and deploy (see Docker Deployment)

# Configure security group
# Allow: 80 (HTTP), 443 (HTTPS), 22 (SSH)
# Restrict PostgreSQL (5432) to localhost only
```

3. **Use RDS for Database** (Recommended)
```env
DATABASE_URL=postgresql://user:pass@your-rds-endpoint:5432/symptomap
```

### Google Cloud Platform

```bash
# Create VM instance
gcloud compute instances create symptomap-server \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --machine-type=e2-medium \
  --boot-disk-size=50GB

# SSH and deploy
gcloud compute ssh symptomap-server
```

### DigitalOcean

1. Create Droplet: Ubuntu 22.04, 4GB RAM
2. SSH and follow Docker deployment steps
3. Use managed PostgreSQL database (recommended)

## Database Setup

### Production PostgreSQL Configuration

Create `docker-compose.prod.yml` override:

```yaml
services:
  postgres:
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    environment:
      POSTGRES_INITDB_ARGS: "-E UTF8 --locale=en_US.UTF-8"
      POSTGRES_HOST_AUTH_METHOD: md5
    command: postgres -c max_connections=200 -c shared_buffers=512MB
```

### Database Migrations

```bash
# Access backend container
docker compose exec backend bash

# Run migrations
alembic upgrade head

# Verify
alembic current
```

### Initial Data Seeding

```bash
# Run seed script
docker compose exec backend python seed_data.py
```

## SSL/TLS Configuration

### Using Let's Encrypt (Recommended)

1. **Install Certbot**

```bash
sudo apt install certbot python3-certbot-nginx
```

2. **Create Nginx Configuration**

Create `nginx-prod.conf`:

```nginx
server {
    listen 80;
    server_name symptomap.yourdomain.com;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name symptomap.yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/symptomap.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/symptomap.yourdomain.com/privkey.pem;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    
    location / {
        proxy_pass http://frontend:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

3. **Obtain Certificate**

```bash
sudo certbot --nginx -d symptomap.yourdomain.com
```

4. **Auto-renewal**

```bash
# Test renewal
sudo certbot renew --dry-run

# Renewal runs automatically via systemd timer
sudo systemctl status certbot.timer
```

## Monitoring

### Enable Prometheus & Grafana

Uncomment monitoring services in `docker-compose.yml`:

```yaml
services:
  prometheus:
    # ... (uncomment)
  
  grafana:
    # ... (uncomment)
```

### Access Monitoring

- **Prometheus**: http://your-server:9090
- **Grafana**: http://your-server:3001
  - Default login: admin / admin (change immediately!)

### Custom Metrics

Backend exposes metrics at `/metrics`:

```bash
curl http://localhost:8000/metrics
```

### Log Aggregation

Using Docker Compose logging:

```yaml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

View logs:

```bash
docker compose logs -f backend --tail=100
```

## Backup & Recovery

### Database Backups

#### Automated Daily Backups

Create `backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
FILENAME="symptomap_backup_$DATE.sql"

docker compose exec -T postgres pg_dump -U symptomap symptomap > "$BACKUP_DIR/$FILENAME"

# Compress
gzip "$BACKUP_DIR/$FILENAME"

# Keep only last 7 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "Backup completed: $FILENAME.gz"
```

#### Schedule with Cron

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /path/to/backup.sh >> /var/log/backup.log 2>&1
```

### Restore from Backup

```bash
# Stop backend
docker compose stop backend

# Restore database
gunzip < backup_file.sql.gz | docker compose exec -T postgres psql -U symptomap symptomap

# Restart services
docker compose up -d
```

### Volume Backups

```bash
# Backup volumes
docker run --rm \
  -v symptomap_postgres_data:/data \
  -v $(pwd)/backups:/backup \
  ubuntu tar czf /backup/postgres_volume_backup.tar.gz /data
```

## Performance Tuning

### Backend Scaling

```bash
# Scale backend workers
docker compose up -d --scale backend=3

# Use load balancer (nginx)
```

### Database Optimization

```sql
-- Create indexes for frequent queries
CREATE INDEX idx_outbreaks_date ON outbreaks(date_reported);
CREATE INDEX idx_outbreaks_location ON outbreaks(hospital_id);

-- Analyze tables
ANALYZE outbreaks;
ANALYZE alerts;
```

### Caching with Redis

Uncomment Redis service in `docker-compose.yml` and configure:

```python
# Backend caching
REDIS_URL=redis://redis:6379
```

## Security Checklist

- [ ] Change all default passwords
- [ ] Use strong JWT secrets (32+ characters)
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall (ufw/firewalld)
- [ ] Restrict database access
- [ ] Enable rate limiting
- [ ] Set up fail2ban
- [ ] Regular security updates
- [ ] Enable audit logging
- [ ] Use secrets management (Vault, AWS Secrets Manager)

## Troubleshooting

### Container won't start

```bash
# Check logs
docker compose logs backend

# Rebuild
docker compose build --no-cache backend
docker compose up -d
```

### Database connection issues

```bash
# Check database status
docker compose exec postgres pg_isready

# Check connection from backend
docker compose exec backend python -c "from app.core.database import engine; print(engine)"
```

### High memory usage

```bash
# Check container stats
docker stats

# Limit container memory
docker compose up -d --scale backend=1
```

## Support

For issues and questions:
- GitHub Issues: https://github.com/yourusername/symptomap/issues
- Documentation: https://docs.symptomap.com
- Email: support@symptomap.com

---

**Last Updated**: 2025-12-29
