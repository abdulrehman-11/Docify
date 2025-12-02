# Use an official Python runtime as base image
FROM python:3.12-slim

# Set environment variables for Python optimization
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (needed for some Python packages)
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
# This allows Docker to cache the pip install step if requirements haven't changed
COPY requirements.txt .

# Install Python dependencies with cache mount for faster builds on Railway
# Railway supports cache mounts which speeds up subsequent builds
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the entire application code
COPY . .

# Run database migrations and start the agent
# Railway will execute this CMD when the container starts
CMD alembic upgrade head && python agent.py start