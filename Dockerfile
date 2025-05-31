FROM python:3.10-slim

# Cache bust - force rebuild (timestamp updated)
RUN echo "Cache bust: $(date)"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy minimal requirements for testing
COPY requirements_minimal.txt .

# Install minimal dependencies for testing
RUN pip install --no-cache-dir -r requirements_minimal.txt

# Copy application code
COPY . .

# Create results directory
RUN mkdir -p results

# Expose port
EXPOSE 8000

# Set environment variables
ENV HOST=0.0.0.0
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Use shell form to allow environment variable expansion
CMD ["/bin/sh", "-c", "uvicorn test_minimal_api:app --host 0.0.0.0 --port $PORT"]
