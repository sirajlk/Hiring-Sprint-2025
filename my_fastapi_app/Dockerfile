# Multi-stage Dockerfile for Car Damage Detection API
# Stage 1: Builder (download dependencies, prepare environment)
FROM python:3.12.4-slim as builder

WORKDIR /app

# Install system dependencies required for OpenCV and Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libopencv-dev \
    python3-opencv \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY ../requirements.txt .

# Install Python dependencies into a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt


# Stage 2: Runtime (minimal image with only runtime dependencies)
FROM python:3.12.4-slim

WORKDIR /app

# Install runtime system dependencies only (no build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libopencv-core4.8 \
    libopencv-imgproc4.8 \
    libopencv-dnn4.8 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Copy application code
COPY . .

# Health check: verify API is responding
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api', timeout=5)" || exit 1

# Expose port
EXPOSE 8000

# Run the application with Gunicorn + Uvicorn workers
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8000", "--access-logfile", "-", "--error-logfile", "-"]
