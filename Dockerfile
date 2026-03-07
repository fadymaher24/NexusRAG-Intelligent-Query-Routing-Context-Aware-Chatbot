# Docker configuration for NexusRAG application

FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY main.py .
COPY .env.example .env

# Create directories
RUN mkdir -p logs dataset

# Expose port
EXPOSE 5001

# Run application
CMD ["python", "main.py"]
