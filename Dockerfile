# Multi-stage Docker build for AI Rockfall Prediction System
# Stage 1: Build React Frontend
FROM node:18-alpine as frontend-build

# Set working directory for frontend
WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm install

# Copy frontend source
COPY frontend/ ./

# Build React app
RUN npm run build

# Stage 2: Python Backend with React Build
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ ./backend/
COPY *.py ./

# Copy React build from frontend stage
COPY --from=frontend-build /app/frontend/build ./frontend/build

# Create data directories
RUN mkdir -p sample-data logs

# Copy sample data
COPY sample-data/ ./sample-data/

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=network_app.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Create startup script
RUN echo '#!/bin/bash\n\
echo "🚀 Starting AI Rockfall Prediction System..."\n\
echo "🏔️  Backend: Flask API Server"\n\
echo "⚡  Frontend: React Dashboard (Built)"\n\
echo "🌐 Access: http://localhost:5000"\n\
echo ""\n\
python network_app.py\n\
' > start.sh && chmod +x start.sh

# Start the application
CMD ["./start.sh"]