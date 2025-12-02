# Use an official Python image - slim for smaller image size
FROM python:3.12-slim

# Set environment variables for Python optimization
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set the working directory
WORKDIR /app

# Install system dependencies required for some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project files
COPY . .

# Expose port (not required for LiveKit WebSocket agent, but useful for debugging)
EXPOSE 8000

# Default command - Railway overrides this via railway.json startCommand
# Pre-deploy runs migrations via railway.json preDeployCommand
CMD ["python", "agent.py", "start"]