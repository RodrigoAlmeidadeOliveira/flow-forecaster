# Dockerfile para Fly.io
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8080

# Run the application with increased timeout for ML processing
CMD ["gunicorn", "wsgi:application", "--bind", "0.0.0.0:8080", "--timeout", "300", "--workers", "2", "--worker-class", "sync", "--max-requests", "1000", "--max-requests-jitter", "100"]
