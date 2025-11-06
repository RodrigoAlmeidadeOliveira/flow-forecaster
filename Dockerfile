# Multi-purpose Dockerfile for Flow Forecaster
# Supports: web, celery worker, flower
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (including PostgreSQL client libraries)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose ports
EXPOSE 8080 5555

# Default command (can be overridden in docker-compose.yml)
# For web server:
#   gunicorn wsgi:application --bind 0.0.0.0:8080 --workers 4 --timeout 120
# For celery worker:
#   celery -A celery_app worker --loglevel=info --concurrency=4
# For flower:
#   celery -A celery_app flower --port=5555

CMD ["sh", "-c", "exec gunicorn wsgi:application --bind 0.0.0.0:${PORT:-8080} --timeout 300 --workers 4 --worker-class sync --max-requests 1000 --max-requests-jitter 100"]
