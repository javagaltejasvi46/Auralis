# Deployment Guide - AURALIS

Production deployment instructions for various platforms.

## Table of Contents
- [Docker Deployment](#docker-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Mobile App Distribution](#mobile-app-distribution)
- [Environment Configuration](#environment-configuration)
- [Monitoring & Logging](#monitoring--logging)

---

## Docker Deployment

### Production Docker Compose

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  backend-api:
    image: auralis-backend:latest
    restart: always
    ports:
      - "8002:8002"
    environment:
      - PYTHON_ENV=production
      - DEBUG=False
    volumes:
      - whisper-models:/root/.cache/huggingface
      - uploads:/app/uploads
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G

  backend-ws:
    image: auralis-backend:latest
    restart: always
    ports:
      - "8003:8003"
    environment:
      - PYTHON_ENV=production
    command: python transcription_server.py
    volumes:
      - whisper-models:/root/.cache/huggingface
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend-api
      - backend-ws
```

### Build and Deploy

```bash
# Build images
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Scale WebSocket servers
docker-compose -f docker-compose.prod.yml up -d --scale backend-ws=3
```

---

## Cloud Deployment

### AWS Deployment

#### Using EC2

```bash
# 1. Launch EC2 instance (t3.large or larger)
# 2. SSH into instance
ssh -i your-key.pem ubuntu@your-instance-ip

# 3. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# 4. Clone and deploy
git clone <your-repo>
cd Auralis
docker-compose -f docker-compose.prod.yml up -d
```

#### Using ECS (Elastic Container Service)

1. Push images to ECR
```bash
aws ecr create-repository --repository-name auralis-backend
docker tag auralis-backend:latest <account-id>.dkr.ecr.region.amazonaws.com/auralis-backend
docker push <account-id>.dkr.ecr.region.amazonaws.com/auralis-backend
```

2. Create ECS task definition
3. Create ECS service
4. Configure load balancer

### Google Cloud Platform

#### Using Cloud Run

```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT-ID/auralis-backend

# Deploy
gcloud run deploy auralis-api \
  --image gcr.io/PROJECT-ID/auralis-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2
```

### Azure

#### Using Azure Container Instances

```bash
# Create resource group
az group create --name auralis-rg --location eastus

# Deploy container
az container create \
  --resource-group auralis-rg \
  --name auralis-backend \
  --image auralis-backend:latest \
  --cpu 2 \
  --memory 4 \
  --ports 8002 8003
```

### DigitalOcean

#### Using App Platform

1. Connect GitHub repository
2. Configure build settings
3. Set environment variables
4. Deploy

---

## Mobile App Distribution

### iOS (App Store)

1. **Setup**
```bash
cd frontend
eas build:configure
```

2. **Build**
```bash
eas build --platform ios --profile production
```

3. **Submit**
```bash
eas submit --platform ios
```

### Android (Play Store)

1. **Build**
```bash
eas build --platform android --profile production
```

2. **Submit**
```bash
eas submit --platform android
```

### Internal Distribution

#### TestFlight (iOS)
```bash
eas build --platform ios --profile preview
eas submit --platform ios --latest
```

#### Internal Testing (Android)
```bash
eas build --platform android --profile preview
# Upload to Play Console Internal Testing
```

---

## Environment Configuration

### Production Environment Variables

```bash
# Backend (.env)
PYTHON_ENV=production
DEBUG=False
LOG_LEVEL=WARNING
API_HOST=0.0.0.0
API_PORT=8002
WS_PORT=8003
DATABASE_URL=postgresql://user:pass@host:5432/auralis
CORS_ORIGINS=https://yourdomain.com
WHISPER_MODEL=medium
WHISPER_DEVICE=cpu
MAX_FILE_SIZE=104857600  # 100MB
```

### Frontend Configuration

```typescript
// frontend/config.ts
export const config = {
  apiUrl: process.env.EXPO_PUBLIC_API_URL || 'https://api.yourdomain.com',
  wsUrl: process.env.EXPO_PUBLIC_WS_URL || 'wss://ws.yourdomain.com',
  environment: process.env.EXPO_PUBLIC_ENV || 'production',
};
```

---

## SSL/TLS Configuration

### Using Let's Encrypt

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### Nginx Configuration

```nginx
# /etc/nginx/sites-available/auralis
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # API
    location /api/ {
        proxy_pass http://localhost:8002/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # WebSocket
    location /ws/ {
        proxy_pass http://localhost:8003/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## Monitoring & Logging

### Application Monitoring

#### Using Prometheus + Grafana

```yaml
# docker-compose.monitoring.yml
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

### Logging

#### Centralized Logging with ELK Stack

```yaml
services:
  elasticsearch:
    image: elasticsearch:8.10.0
    environment:
      - discovery.type=single-node

  logstash:
    image: logstash:8.10.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf

  kibana:
    image: kibana:8.10.0
    ports:
      - "5601:5601"
```

### Health Checks

```python
# backend/health.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "api": "up",
            "database": "up",
            "whisper": "up"
        }
    }
```

---

## Performance Optimization

### Backend

1. **Use Gunicorn with multiple workers**
```bash
gunicorn main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  -b 0.0.0.0:8002 \
  --timeout 120
```

2. **Enable caching**
```python
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

FastAPICache.init(RedisBackend(redis), prefix="auralis")
```

3. **Database connection pooling**
```python
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=40
)
```

### Frontend

1. **Enable production build**
```bash
eas build --platform all --profile production
```

2. **Optimize assets**
```bash
npx expo-optimize
```

---

## Backup & Recovery

### Database Backup

```bash
# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker exec auralis-backend-api \
  sqlite3 /app/audio_records.db ".backup /app/backups/db_$DATE.db"

# Upload to S3
aws s3 cp /app/backups/db_$DATE.db s3://auralis-backups/
```

### Model Cache Backup

```bash
# Backup Whisper models
tar -czf whisper-models.tar.gz ~/.cache/huggingface/
aws s3 cp whisper-models.tar.gz s3://auralis-backups/models/
```

---

## Security Checklist

- [ ] Enable HTTPS/TLS
- [ ] Set strong passwords
- [ ] Configure firewall rules
- [ ] Enable rate limiting
- [ ] Implement authentication
- [ ] Regular security updates
- [ ] Backup encryption
- [ ] API key rotation
- [ ] Input validation
- [ ] CORS configuration

---

## Scaling

### Horizontal Scaling

```bash
# Scale WebSocket servers
docker-compose up -d --scale backend-ws=5

# Use load balancer (nginx)
upstream websocket_backend {
    least_conn;
    server backend-ws-1:8003;
    server backend-ws-2:8003;
    server backend-ws-3:8003;
}
```

### Vertical Scaling

- Increase CPU/RAM for containers
- Use GPU for faster transcription
- Optimize model size (base vs medium vs large)

---

## Troubleshooting Production

### High Memory Usage
```bash
# Check container stats
docker stats

# Limit memory
docker update --memory 4g container-name
```

### Slow Transcription
- Use GPU acceleration
- Reduce model size
- Increase worker count
- Enable caching

### Connection Issues
- Check firewall rules
- Verify DNS settings
- Test with curl/wscat
- Review nginx logs

---

**Production deployment complete! Monitor your application and scale as needed. 🚀**
