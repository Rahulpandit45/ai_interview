# Multi-stage production container for AI Video Interview System
FROM python:3.11-slim

# Prevent Python from writing .pyc and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=10000

# Install system dependencies for OpenCV, MediaPipe, FFmpeg, and audio processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    libsndfile1 \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency definition first for caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy all application code
COPY . .

# Ensure upload and reports directories exist
RUN mkdir -p backend/uploads/resumes \
             backend/uploads/recordings \
             backend/uploads/profiles \
             backend/reports

# Expose server port
EXPOSE 10000

# Run with Gunicorn WSGI server in production (1 worker + threads to stay within 512MB RAM limit)
CMD gunicorn --bind 0.0.0.0:${PORT:-10000} --workers 1 --threads 4 --timeout 120 backend.app:app
