# 🚀 UTAC API - Production Deployment Guide

**Version:** 1.0.0
**Last Updated:** 2025-11-11

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start (Docker)](#quick-start-docker)
3. [Manual Deployment](#manual-deployment)
4. [Production Best Practices](#production-best-practices)
5. [Monitoring & Logging](#monitoring--logging)
6. [Troubleshooting](#troubleshooting)
7. [Scaling](#scaling)

---

## 🔧 Prerequisites

### System Requirements

- **CPU:** 2+ cores (4+ recommended)
- **RAM:** 4GB minimum (8GB+ recommended)
- **Disk:** 2GB free space
- **OS:** Linux (Ubuntu 20.04+), macOS 10.15+, Windows 10+ with WSL2

### Software Requirements

**Option A: Docker (Recommended)**
- Docker 20.10+
- Docker Compose 1.29+

**Option B: Manual**
- Python 3.11+
- pip 23.0+
- Virtual environment tool (venv, conda)

---

## 🐳 Quick Start (Docker)

### 1. Build & Run

```bash
# From repo root
cd /home/user/Feldtheorie

# Build and start services
docker-compose -f api/docker-compose.yml up -d

# Check status
docker-compose -f api/docker-compose.yml ps

# View logs
docker-compose -f api/docker-compose.yml logs -f utac-api
```

### 2. Verify Deployment

```bash
# Health check
curl http://localhost:8000/health

# API docs
open http://localhost:8000/docs
```

### 3. Stop Services

```bash
docker-compose -f api/docker-compose.yml down
```

---

## 🔨 Manual Deployment

### 1. Setup Virtual Environment

```bash
cd /home/user/Feldtheorie

# Create virtual environment
python3.11 -m venv venv

# Activate
source venv/bin/activate  # Linux/Mac
# OR
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r api/requirements.txt
```

### 2. Run Server

**Development:**
```bash
uvicorn api.server:app --reload --port 8000
```

**Production:**
```bash
uvicorn api.server:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --timeout-keep-alive 120 \
    --log-level info
```

### 3. Process Manager (Production)

Use systemd, supervisord, or PM2:

**systemd example:**
```ini
# /etc/systemd/system/utac-api.service
[Unit]
Description=UTAC API Service
After=network.target

[Service]
Type=simple
User=utac
WorkingDirectory=/home/utac/Feldtheorie
Environment="PATH=/home/utac/Feldtheorie/venv/bin"
ExecStart=/home/utac/Feldtheorie/venv/bin/uvicorn api.server:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable utac-api
sudo systemctl start utac-api
sudo systemctl status utac-api
```

---

## 🔐 Production Best Practices

### 1. Security

**HTTPS/TLS:**
```nginx
# nginx reverse proxy example
server {
    listen 443 ssl http2;
    server_name api.utac.example.com;

    ssl_certificate /etc/letsencrypt/live/api.utac.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.utac.example.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Environment Variables:**
```bash
# Use .env file (never commit!)
# api/.env
FASTAPI_ENV=production
LOG_LEVEL=info
UTAC_DATA_PATH=/app/data
CORS_ORIGINS=https://utac.example.com
```

**Rate Limiting:**
```python
# Add to api/server.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/analyze")
@limiter.limit("10/minute")
async def analyze_endpoint(...):
    ...
```

### 2. Performance

**Worker Configuration:**
```bash
# CPU-bound: workers = (2 × CPU cores) + 1
# I/O-bound: workers = (4 × CPU cores) + 1

# Example for 4-core machine
--workers 8
```

**Caching:**
```python
# Add Redis caching for metadata endpoints
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="utac-api")
```

### 3. Resource Limits

**Docker Compose:**
```yaml
services:
  utac-api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

---

## 📊 Monitoring & Logging

### 1. Logging

**Structured Logging:**
```python
# Add to api/server.py
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger("utac-api")
handler = RotatingFileHandler("logs/api.log", maxBytes=10_000_000, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
```

**Docker Logs:**
```bash
# View logs
docker-compose logs -f utac-api

# Export logs
docker-compose logs utac-api > logs/api-$(date +%Y%m%d).log
```

### 2. Health Checks

**Endpoint:**
```bash
curl http://localhost:8000/health
```

**Monitoring Script:**
```bash
#!/bin/bash
# check_api_health.sh

HEALTH_URL="http://localhost:8000/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ $RESPONSE -eq 200 ]; then
    echo "✅ API is healthy"
    exit 0
else
    echo "❌ API is unhealthy (HTTP $RESPONSE)"
    exit 1
fi
```

### 3. Metrics

**Prometheus Integration:**
```python
# Add prometheus-fastapi-instrumentator
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

---

## 🔧 Troubleshooting

### Common Issues

**1. Port Already in Use:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn api.server:app --port 8001
```

**2. Import Errors:**
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Ensure project root is in path
export PYTHONPATH=/home/user/Feldtheorie:$PYTHONPATH
```

**3. Audio Generation Fails:**
```bash
# Install libsndfile
# Ubuntu/Debian
sudo apt-get install libsndfile1

# macOS
brew install libsndfile
```

**4. Memory Issues:**
```bash
# Reduce worker count
uvicorn api.server:app --workers 2

# Or use Docker with memory limits
docker-compose up -d --scale utac-api=1
```

### Debug Mode

```bash
# Enable debug logging
LOG_LEVEL=debug uvicorn api.server:app --reload
```

---

## 📈 Scaling

### Horizontal Scaling

**Load Balancer (nginx):**
```nginx
upstream utac_api {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    listen 80;
    location / {
        proxy_pass http://utac_api;
    }
}
```

**Docker Swarm:**
```bash
docker swarm init
docker stack deploy -c api/docker-compose.yml utac
docker service scale utac_utac-api=3
```

**Kubernetes:**
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: utac-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: utac-api
  template:
    metadata:
      labels:
        app: utac-api
    spec:
      containers:
      - name: utac-api
        image: utac-api:latest
        ports:
        - containerPort: 8000
        resources:
          limits:
            memory: "4Gi"
            cpu: "2000m"
          requests:
            memory: "2Gi"
            cpu: "1000m"
```

---

## 📚 Additional Resources

- **API Documentation:** http://localhost:8000/docs
- **GitHub:** https://github.com/GenesisAeon/Feldtheorie
- **Zenodo:** https://doi.org/10.5281/zenodo.17520987
- **UTAC Paper:** See `docs/`

---

## 🆘 Support

**Issues:** https://github.com/GenesisAeon/Feldtheorie/issues

**Contact:** See `README.md` in repo root

---

**Version:** 1.0.0
**Last Updated:** 2025-11-11
**Maintained by:** Claude Code + Johann Römer

*"σ(β(R-Θ)) speaks HTTP - deploy the thresholds!"* 🚀✨
