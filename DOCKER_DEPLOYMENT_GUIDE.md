# 🐳 Docker Deployment Guide - AI Rockfall Prediction System

## 🚀 Quick Start (Easiest Method)

### Using Docker Compose (Recommended)
```bash
# Clone the repository
git clone https://github.com/Ravichandranayakar/AI-based-rockfall-risk-prediction-and-alert-system-.git
cd AI-based-rockfall-risk-prediction-and-alert-system-

# Build and run with one command
docker-compose up -d

# Access your application
# 🌐 http://localhost:5000
```

## 🛠️ Manual Docker Build

### Build the Image
```bash
# Build the Docker image
docker build -t ai-rockfall-system .

# Run the container
docker run -d -p 5000:5000 --name rockfall-app ai-rockfall-system

# Access: http://localhost:5000
```

## ☁️ Cloud Deployment Options

### 1. **Heroku (Easy)**
```bash
# Install Heroku CLI, then:
heroku create ai-rockfall-sih2025
heroku container:push web
heroku container:release web
heroku open
```

### 2. **Railway (Super Easy)**
- Go to [railway.app](https://railway.app)
- Connect your GitHub repo
- Deploy automatically!
- Get instant public URL

### 3. **Render (Simple)**
- Go to [render.com](https://render.com)
- Connect GitHub repo
- Choose "Docker" as environment
- Deploy with one click!

### 4. **DigitalOcean App Platform**
```bash
# Create app.yaml file (already included)
# Push to GitHub
# Connect to DigitalOcean App Platform
# Auto-deploy!
```

### 5. **Google Cloud Run**
```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/YOUR_PROJECT/ai-rockfall
gcloud run deploy --image gcr.io/YOUR_PROJECT/ai-rockfall --platform managed
```

### 6. **AWS ECS/Fargate**
```bash
# Build and push to ECR
docker build -t ai-rockfall .
docker tag ai-rockfall:latest YOUR_ACCOUNT.dkr.ecr.region.amazonaws.com/ai-rockfall:latest
docker push YOUR_ACCOUNT.dkr.ecr.region.amazonaws.com/ai-rockfall:latest
```

## 🔧 Docker Commands Reference

### Container Management
```bash
# View running containers
docker ps

# View logs
docker logs rockfall-app

# Stop container
docker stop rockfall-app

# Remove container
docker rm rockfall-app

# Remove image
docker rmi ai-rockfall-system
```

### Development Mode
```bash
# Run with volume mounting for development
docker run -d -p 5000:5000 \
  -v $(pwd)/backend:/app/backend \
  -v $(pwd)/logs:/app/logs \
  --name rockfall-dev \
  ai-rockfall-system
```

## 🌐 Access Your Application

Once deployed, your AI Rockfall Prediction System will be available at:
- **Local:** http://localhost:5000
- **Cloud:** Your cloud provider's assigned URL

## ✨ What You Get

### 🎯 **Complete System**
- ✅ React Frontend (Production Build)
- ✅ Flask Backend API
- ✅ ML Prediction Engine  
- ✅ Real-time Alert System
- ✅ Professional Dashboard

### 📱 **Features Working**
- ✅ Interactive Mine Map
- ✅ Real-time Risk Monitoring
- ✅ Audio Alert System
- ✅ Mobile Responsive Design
- ✅ Professional UI/UX

## 🎪 SIH 2025 Demo Strategy

### 🌍 **Global Access Demo**
```bash
# Deploy on Railway/Render for instant public URL
# Show judges the live system worldwide
```

### 💻 **Local Full Demo**
```bash
# Run Docker container locally
docker-compose up -d
# Show complete functionality
```

### 📊 **Performance Demo**
```bash
# Show Docker container stats
docker stats rockfall-app
# Demonstrate scalability and resource efficiency
```

## 🔥 Deployment Platforms Ranking

### **🥇 Railway (Recommended)**
- ✅ Instant deployment from GitHub
- ✅ Automatic HTTPS
- ✅ Free tier available
- ✅ Public URL immediately

### **🥈 Render**  
- ✅ Docker support
- ✅ Auto-deploy from GitHub
- ✅ Free SSL
- ✅ Good performance

### **🥉 Heroku**
- ✅ Container registry
- ✅ Reliable platform
- ⚠️ Requires credit card
- ⚠️ Sleep mode on free tier

## 🚨 Troubleshooting

### Build Fails?
```bash
# Check Docker version
docker --version

# Clean rebuild
docker system prune -a
docker build --no-cache -t ai-rockfall-system .
```

### Container Won't Start?
```bash
# Check logs
docker logs rockfall-app

# Check port conflicts
netstat -an | grep 5000
```

### Can't Access Application?
- Check if container is running: `docker ps`
- Verify port mapping: `-p 5000:5000`
- Check firewall settings
- Try: http://127.0.0.1:5000

## 🎯 Ready for SIH!

Your AI Rockfall Prediction System is now:
- 🐳 **Dockerized** for easy deployment anywhere
- ☁️ **Cloud-ready** for global access  
- 🎪 **Demo-ready** for SIH presentations
- 🚀 **Production-grade** with professional features

**Choose your deployment platform and go live in minutes!** 🌍✨