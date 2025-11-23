# Deployment Guide for Feldtheorie / UTAC

Comprehensive deployment instructions for all Feldtheorie components: Python API, React Simulator, and Docker containerization.

---

## Table of Contents

1. [Overview](#overview)
2. [Python Backend Deployment](#python-backend-deployment)
3. [React Simulator Deployment](#react-simulator-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Cloud Platform Deployments](#cloud-platform-deployments)
6. [Environment Variables](#environment-variables)
7. [Production Checklist](#production-checklist)
8. [Monitoring & Maintenance](#monitoring--maintenance)
9. [Troubleshooting](#troubleshooting)

---

## Overview

### Component Architecture

```
Feldtheorie/
├── api/                    # FastAPI REST server
├── simulator/              # React/TypeScript frontend
├── analysis/               # Python analysis pipeline
├── models/                 # Numerical solvers
└── data/                   # Scientific datasets
```

### Deployment Options

| Option | Use Case | Complexity | Cost |
|--------|----------|------------|------|
| **Local Development** | Testing, demos | Low | Free |
| **Docker Compose** | Single-server deployment | Medium | Low |
| **Docker + Nginx** | Production web server | Medium | Low-Medium |
| **Cloud PaaS** | Scalable production | Medium-High | Medium-High |
| **Kubernetes** | Enterprise scale | High | High |

---

## Python Backend Deployment

### Prerequisites

- Python ≥ 3.10
- pip or conda
- Virtual environment tool (venv/conda)

### 1. Environment Setup

#### Using venv (Recommended)

```bash
# Clone repository
git clone https://github.com/GenesisAeon/Feldtheorie.git
cd Feldtheorie

# Create virtual environment
python -m venv venv

# Activate
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

#### Using conda

```bash
# Create environment from spec
conda env create -f environment.yml

# Activate
conda activate feldtheorie
```

### 2. API Server Deployment

#### Development Server

```bash
cd api
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

Access at: http://localhost:8000

#### Production Server (Uvicorn + Gunicorn)

```bash
# Install production server
pip install gunicorn

# Run with Gunicorn
cd api
gunicorn server:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --access-logfile /var/log/feldtheorie/access.log \
  --error-logfile /var/log/feldtheorie/error.log
```

**Production Settings:**
- **Workers**: `2-4 × CPU cores`
- **Worker Class**: `uvicorn.workers.UvicornWorker`
- **Timeout**: `120s` (for long-running analyses)
- **Keep-alive**: `5s`

#### Systemd Service (Linux)

Create `/etc/systemd/system/feldtheorie-api.service`:

```ini
[Unit]
Description=Feldtheorie UTAC API
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/feldtheorie/api
Environment="PATH=/opt/feldtheorie/venv/bin"
ExecStart=/opt/feldtheorie/venv/bin/gunicorn server:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --access-logfile /var/log/feldtheorie/access.log \
  --error-logfile /var/log/feldtheorie/error.log
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable feldtheorie-api
sudo systemctl start feldtheorie-api
sudo systemctl status feldtheorie-api
```

---

## React Simulator Deployment

### Prerequisites

- Node.js ≥ 18.0.0
- npm or yarn

### 1. Development Server

```bash
cd simulator
npm install
npm run dev
```

Access at: http://localhost:5173

### 2. Production Build

```bash
cd simulator
npm install
npm run build
```

Output: `simulator/dist/`

### 3. Static File Hosting

#### Option A: Nginx

```nginx
# /etc/nginx/sites-available/feldtheorie-simulator

server {
    listen 80;
    server_name simulator.feldtheorie.example.com;

    root /var/www/feldtheorie/simulator/dist;
    index index.html;

    # Enable gzip
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # SPA fallback
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```

Deploy:

```bash
# Copy build
sudo cp -r simulator/dist/* /var/www/feldtheorie/simulator/

# Enable site
sudo ln -s /etc/nginx/sites-available/feldtheorie-simulator /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### Option B: Apache

```apache
# /etc/apache2/sites-available/feldtheorie-simulator.conf

<VirtualHost *:80>
    ServerName simulator.feldtheorie.example.com
    DocumentRoot /var/www/feldtheorie/simulator/dist

    <Directory /var/www/feldtheorie/simulator/dist>
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted

        # SPA fallback
        RewriteEngine On
        RewriteBase /
        RewriteRule ^index\.html$ - [L]
        RewriteCond %{REQUEST_FILENAME} !-f
        RewriteCond %{REQUEST_FILENAME} !-d
        RewriteRule . /index.html [L]
    </Directory>

    # Enable compression
    <IfModule mod_deflate.c>
        AddOutputFilterByType DEFLATE text/html text/plain text/css application/javascript application/json
    </IfModule>

    # Cache static assets
    <FilesMatch "\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$">
        Header set Cache-Control "max-age=31536000, public, immutable"
    </FilesMatch>
</VirtualHost>
```

Deploy:

```bash
sudo a2enmod rewrite headers deflate
sudo a2ensite feldtheorie-simulator
sudo systemctl reload apache2
```

#### Option C: Node.js Static Server

```bash
cd simulator
npm install -g serve

# Production
serve -s dist -l 3000

# Or with PM2
npm install -g pm2
pm2 start "serve -s dist -l 3000" --name feldtheorie-simulator
pm2 save
pm2 startup
```

---

## Docker Deployment

### 1. Docker Compose (All-in-One)

**docker-compose.yml**:

```yaml
version: '3.8'

services:
  api:
    build:
      context: ./api
      dockerfile: Dockerfile
    container_name: feldtheorie-api
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - PYTHONUNBUFFERED=1
      - WORKERS=4
    volumes:
      - ./data:/app/data:ro
      - ./analysis/results:/app/analysis/results:ro
      - ./logs:/var/log/feldtheorie
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  simulator:
    build:
      context: ./simulator
      dockerfile: Dockerfile
    container_name: feldtheorie-simulator
    restart: unless-stopped
    ports:
      - "3000:80"
    depends_on:
      - api

  nginx:
    image: nginx:alpine
    container_name: feldtheorie-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./logs/nginx:/var/log/nginx
    depends_on:
      - api
      - simulator

volumes:
  logs:
```

**API Dockerfile** (`api/Dockerfile`):

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application
COPY . .

# Create log directory
RUN mkdir -p /var/log/feldtheorie

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run with Gunicorn
CMD ["gunicorn", "server:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120", \
     "--access-logfile", "/var/log/feldtheorie/access.log", \
     "--error-logfile", "/var/log/feldtheorie/error.log"]
```

**Simulator Dockerfile** (`simulator/Dockerfile`):

```dockerfile
# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source
COPY . .

# Build
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
```

**Simulator Nginx Config** (`simulator/nginx.conf`):

```nginx
server {
    listen 80;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    # Gzip
    gzip on;
    gzip_vary on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

    # Cache static
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # SPA fallback
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

### 2. Deploy with Docker Compose

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

### 3. Production Nginx Reverse Proxy

**nginx/nginx.conf**:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream api {
        server api:8000;
    }

    upstream simulator {
        server simulator:80;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=general_limit:10m rate=50r/s;

    server {
        listen 80;
        server_name feldtheorie.example.com;

        # Redirect to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name feldtheorie.example.com;

        # SSL certificates
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # Security headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;

        # API routes
        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;

            proxy_pass http://api/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_read_timeout 120s;
        }

        # Simulator
        location / {
            limit_req zone=general_limit burst=100 nodelay;

            proxy_pass http://simulator/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }
}
```

---

## Cloud Platform Deployments

### AWS (Elastic Beanstalk)

#### 1. API Deployment

```bash
# Install EB CLI
pip install awsebcli

# Initialize
cd api
eb init -p python-3.11 feldtheorie-api --region us-east-1

# Create environment
eb create feldtheorie-api-prod

# Deploy
eb deploy

# Open
eb open
```

**`.ebextensions/python.config`**:

```yaml
option_settings:
  aws:elasticbeanstalk:application:environment:
    PYTHONPATH: "/var/app/current"
  aws:elasticbeanstalk:container:python:
    WSGIPath: "server:app"
```

#### 2. Simulator Deployment (S3 + CloudFront)

```bash
# Build
cd simulator
npm run build

# Upload to S3
aws s3 sync dist/ s3://feldtheorie-simulator/ --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/*"
```

### Google Cloud Platform

#### 1. API (Cloud Run)

```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/feldtheorie-api api/

# Deploy
gcloud run deploy feldtheorie-api \
  --image gcr.io/PROJECT_ID/feldtheorie-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --timeout 120
```

#### 2. Simulator (Firebase Hosting)

```bash
cd simulator
npm run build

# Install Firebase CLI
npm install -g firebase-tools

# Login
firebase login

# Initialize
firebase init hosting

# Deploy
firebase deploy --only hosting
```

### Heroku

#### API Deployment

```bash
# Install Heroku CLI
# Login
heroku login

# Create app
cd api
heroku create feldtheorie-api

# Add buildpack
heroku buildpacks:set heroku/python

# Deploy
git push heroku main

# Scale
heroku ps:scale web=2

# View logs
heroku logs --tail
```

**Procfile**:

```
web: gunicorn server:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

### Vercel (Simulator Only)

```bash
cd simulator

# Install Vercel CLI
npm install -g vercel

# Deploy
vercel

# Production
vercel --prod
```

---

## Environment Variables

### API Server

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `8000` | Server port |
| `WORKERS` | `4` | Number of worker processes |
| `TIMEOUT` | `120` | Request timeout (seconds) |
| `LOG_LEVEL` | `info` | Logging level |
| `DATA_PATH` | `../data` | Path to datasets |
| `RESULTS_PATH` | `../analysis/results` | Analysis results path |

### Simulator

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_URL` | `/api` | API base URL |
| `VITE_DEFAULT_LANG` | `en` | Default language |

Set in `.env` file:

```bash
# API
HOST=0.0.0.0
PORT=8000
WORKERS=4

# Simulator
VITE_API_URL=https://api.feldtheorie.example.com
VITE_DEFAULT_LANG=en
```

---

## Production Checklist

### Security

- [ ] HTTPS enabled with valid SSL certificate
- [ ] API rate limiting configured
- [ ] CORS properly configured
- [ ] Security headers set (HSTS, CSP, X-Frame-Options)
- [ ] Secrets stored in environment variables (not in code)
- [ ] File upload limits enforced
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS protection enabled

### Performance

- [ ] Static assets cached (1 year for immutable)
- [ ] Gzip/Brotli compression enabled
- [ ] CDN configured for static files
- [ ] Database queries optimized
- [ ] API response pagination implemented
- [ ] Image optimization (WebP, lazy loading)

### Monitoring

- [ ] Application logs configured
- [ ] Error tracking (Sentry, Rollbar)
- [ ] Uptime monitoring (UptimeRobot, Pingdom)
- [ ] Performance monitoring (New Relic, DataDog)
- [ ] Health check endpoints
- [ ] Alerts configured for critical errors

### Backup

- [ ] Database backups automated
- [ ] Data files backed up regularly
- [ ] Disaster recovery plan documented
- [ ] Backup restoration tested

---

## Monitoring & Maintenance

### Health Checks

**API Health Endpoint** (`api/server.py`):

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "4.0.0"
    }
```

Test:

```bash
curl https://api.feldtheorie.example.com/health
```

### Log Aggregation

#### Using Logrotate (Linux)

`/etc/logrotate.d/feldtheorie`:

```
/var/log/feldtheorie/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload feldtheorie-api > /dev/null 2>&1 || true
    endscript
}
```

### Performance Monitoring

```bash
# API response times
curl -w "@curl-format.txt" -o /dev/null -s https://api.feldtheorie.example.com/beta

# Server resources
htop
docker stats

# Network traffic
iftop
```

---

## Troubleshooting

### Common Issues

#### 1. API Returns 502 Bad Gateway

**Cause**: Backend not running or timeout

**Solution**:

```bash
# Check API status
docker-compose logs api

# Increase timeout
# In nginx.conf:
proxy_read_timeout 180s;
proxy_connect_timeout 180s;
```

#### 2. Simulator Shows Blank Page

**Cause**: Incorrect base path or API URL

**Solution**:

```bash
# Check build output
cd simulator/dist
ls -la

# Verify API URL in .env
echo $VITE_API_URL

# Rebuild
npm run build
```

#### 3. CORS Errors

**Cause**: API CORS not configured for frontend domain

**Solution** (`api/server.py`):

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://feldtheorie.example.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 4. Out of Memory

**Cause**: Large dataset processing

**Solution**:

```bash
# Increase Docker memory
# docker-compose.yml:
services:
  api:
    deploy:
      resources:
        limits:
          memory: 4G

# Or increase system limits
ulimit -m 4194304  # 4GB
```

---

## Support

- **Issues**: https://github.com/GenesisAeon/Feldtheorie/issues
- **Documentation**: [docs/](docs/)
- **Email**: [Your contact]

---

## License

Code: GPLv3 | Content & Data: CC BY-NC 4.0 (non-commercial). Commercial use requires explicit permission. See [LICENSE](LICENSE).
