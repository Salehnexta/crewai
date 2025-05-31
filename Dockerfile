FROM python:3.10-slim

WORKDIR /app

# Copy minimal files only
COPY requirements_minimal.txt .
COPY test_minimal_api.py .

# Install minimal dependencies only
RUN pip install --no-cache-dir -r requirements_minimal.txt

# Environment
ENV HOST=0.0.0.0
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Simple CMD
CMD ["uvicorn", "test_minimal_api:app", "--host", "0.0.0.0", "--port", "8000"]
