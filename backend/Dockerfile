FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (only what's needed)
# Include ca-certificates and curl for better SSL/network handling
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && update-ca-certificates

# Upgrade pip and install build tools first (faster builds)
# Add retry logic and longer timeouts for network issues
RUN pip install --upgrade pip setuptools wheel --timeout=100 --retries=5 || \
    pip install --upgrade pip setuptools wheel --timeout=100 --retries=5 || \
    pip install --upgrade pip setuptools wheel --timeout=100 --retries=5

# Copy requirements and install Python dependencies
# Using cache for faster rebuilds - Docker layer caching will help
# Add retry logic and split into smaller chunks for better error recovery
COPY requirements.txt .
RUN pip install --upgrade pip --timeout=100 --retries=5 && \
    pip install -r requirements.txt --timeout=300 --retries=5 --no-cache-dir || \
    (echo "First attempt failed, retrying..." && \
     pip install -r requirements.txt --timeout=300 --retries=5 --no-cache-dir) || \
    (echo "Second attempt failed, retrying with trusted hosts..." && \
     pip install -r requirements.txt --timeout=300 --retries=5 --no-cache-dir \
     --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org)

# Copy application code
COPY backend/ ./backend/
COPY src/ ./src/

# Set Python path
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
