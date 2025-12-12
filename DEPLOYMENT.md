# Deployment Guide

## 🚀 Organization Management System - Full Stack Deployment

This guide covers deployment options for your internship assignment.

---

## Table of Contents
1. [Local Deployment](#local-deployment)
2. [Production Deployment Options](#production-deployment-options)
3. [Cloud Deployment (Render/Heroku)](#cloud-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Environment Configuration](#environment-configuration)

---

## Local Deployment

### Running Locally

Your application is already set up for local deployment!

```bash
# Backend is running on: http://localhost:8000
# Frontend is available at: http://localhost:8000

# API Documentation: http://localhost:8000/docs
# API Health Check: http://localhost:8000/api
```

**Access the Application:**
- Open browser: http://localhost:8000
- Use the UI to interact with all API endpoints

---

## Production Deployment Options

### Option 1: Render (Recommended - Free Tier Available)

#### Backend Deployment on Render

1. **Create account**: https://render.com

2. **Create New Web Service**:
   - Connect your GitHub repository
   - Configure:
     ```
     Name: organization-management-api
     Environment: Python 3
     Build Command: pip install -r requirements.txt
     Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```

3. **Add Environment Variables**:
   ```
   MONGODB_URL=<your-mongodb-atlas-url>
   SECRET_KEY=<generate-strong-secret>
   DEBUG=False
   ```

4. **MongoDB Atlas Setup**:
   - Go to https://www.mongodb.com/cloud/atlas
   - Create free cluster
   - Get connection string
   - Add to Render environment variables

#### Frontend on Render (Static Site)

Since your frontend is served by FastAPI, it's already deployed with the backend!

---

### Option 2: Heroku

#### Deploy to Heroku

1. **Create Heroku account**: https://heroku.com

2. **Install Heroku CLI**:
   ```bash
   # Download from https://devcenter.heroku.com/articles/heroku-cli
   ```

3. **Create Procfile** (already created below)

4. **Deploy**:
   ```bash
   heroku login
   heroku create your-app-name
   heroku addons:create mongolab:sandbox
   git push heroku main
   ```

---

### Option 3: Railway

Railway offers simple deployment with MongoDB support.

1. **Sign up**: https://railway.app
2. **Connect GitHub repo**
3. **Add MongoDB service**
4. **Deploy automatically**

---

## Docker Deployment

### Docker Configuration Files

#### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### docker-compose.yml
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MONGODB_URL=mongodb://mongo:27017
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - mongo

  mongo:
    image: mongo:latest
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db

volumes:
  mongo_data:
```

### Deploy with Docker

```bash
# Build and run
docker-compose up --build

# Access at http://localhost:8000
```

---

## Environment Configuration

### Production Environment Variables

Create `.env.production`:

```env
# MongoDB Configuration
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/
MASTER_DB_NAME=master_organization_db

# JWT Configuration - MUST CHANGE!
SECRET_KEY=<GENERATE_STRONG_SECRET_KEY_HERE>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Configuration
APP_NAME=Organization Management Service
APP_VERSION=1.0.0
DEBUG=False
```

### Generate Secure Secret Key

```python
import secrets
print(secrets.token_urlsafe(32))
```

Or use online generator: https://randomkeygen.com/

---

## Quick Deployment Checklist

### Pre-Deployment

- [ ] Change SECRET_KEY in production
- [ ] Set DEBUG=False
- [ ] Setup MongoDB Atlas (free tier)
- [ ] Test all API endpoints locally
- [ ] Update CORS origins for production domain
- [ ] Add rate limiting (optional)

### Post-Deployment

- [ ] Test all endpoints on production URL
- [ ] Verify MongoDB connection
- [ ] Check authentication flow
- [ ] Test frontend UI
- [ ] Monitor logs for errors
- [ ] Setup SSL/HTTPS (automatic on Render/Heroku)

---

## Free Hosting Options Summary

| Platform | Backend | Database | Frontend | Free Tier |
|----------|---------|----------|----------|-----------|
| **Render** | ✅ 750hrs/mo | MongoDB Atlas | ✅ Included | Yes |
| **Heroku** | ✅ 1000hrs/mo | mLab/Atlas | ✅ Included | Yes |
| **Railway** | ✅ 500hrs/mo | ✅ Built-in | ✅ Included | Yes |
| **Vercel** | ❌ (Serverless) | External | ✅ Unlimited | Yes |

### Recommended for Internship: **Render + MongoDB Atlas**
- Easy setup
- Free SSL
- Auto-deploys from GitHub
- Perfect for portfolio/assignment

---

## Deployment Commands Reference

### Render
```bash
# No commands needed - automatic from GitHub
```

### Heroku
```bash
heroku login
heroku create your-app-name
heroku config:set SECRET_KEY=your-secret-key
git push heroku main
heroku open
```

### Docker
```bash
docker-compose up --build -d
docker-compose logs -f
docker-compose down
```

---

## MongoDB Atlas Setup (Free Tier)

1. **Create Account**: https://www.mongodb.com/cloud/atlas
2. **Create Cluster**: Select free M0 tier
3. **Create Database User**:
   - Username: admin
   - Password: (generate strong password)
4. **Network Access**: Add `0.0.0.0/0` (allow from anywhere)
5. **Get Connection String**:
   ```
   mongodb+srv://admin:<password>@cluster0.xxxxx.mongodb.net/
   ```
6. **Update Environment Variable**: `MONGODB_URL=<connection-string>`

---

## Testing Deployment

### Verify Backend
```bash
curl https://your-app.onrender.com/health
curl https://your-app.onrender.com/api
```

### Verify Frontend
Open browser: https://your-app.onrender.com

### Test API Endpoints
Use the deployed frontend UI or Postman to test all operations.

---

## Troubleshooting

### Issue: MongoDB Connection Error
**Solution**: Check connection string, network access settings in Atlas

### Issue: 502 Bad Gateway
**Solution**: Check application logs, ensure port is correct

### Issue: CORS Errors
**Solution**: Update CORS origins in `app/main.py`:
```python
allow_origins=["https://your-frontend-domain.com"]
```

### Issue: JWT Token Errors
**Solution**: Verify SECRET_KEY is set correctly in environment

---

## Demo URLs for Assignment Submission

After deployment, you'll have:

```
🌐 Application URL: https://your-app.onrender.com
📚 API Documentation: https://your-app.onrender.com/docs
🔧 API Health: https://your-app.onrender.com/health
📊 GitHub Repository: https://github.com/yourusername/org-management
```

---

## Performance Tips

1. **Enable MongoDB Indexes**:
   - Index on `organization_name`
   - Index on `email`

2. **Add Caching** (for production):
   - Use Redis for session storage
   - Cache organization metadata

3. **Rate Limiting**:
   ```python
   from slowapi import Limiter
   # Add to main.py
   ```

4. **Monitoring**:
   - Use Render/Heroku built-in metrics
   - Add Sentry for error tracking

---

## Next Steps

1. **Test locally** ✅ (Already done)
2. **Push to GitHub** (if not already)
3. **Deploy to Render** (recommended)
4. **Test deployed version**
5. **Submit assignment** with deployment URL

---

## Support

For deployment issues:
- Render Docs: https://render.com/docs
- Heroku Docs: https://devcenter.heroku.com
- MongoDB Atlas Docs: https://docs.atlas.mongodb.com

Good luck with your deployment! 🚀
