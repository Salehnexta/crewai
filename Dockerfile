# Use Python 3.10 slim image for Railway deployment
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for AI/ML packages
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create results directory for agent outputs
RUN mkdir -p results

# Set environment variables for Railway deployment
ENV PORT=8000
ENV HOST=0.0.0.0
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE $PORT

# Use the updated API file for Railway deployment with MCP
CMD uvicorn morvo_integration_api:app --host 0.0.0.0 --port ${PORT:-8000} --log-level info
