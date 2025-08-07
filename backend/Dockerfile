FROM python:3.11-slim-buster

# Build arguments for caching
ARG BUILDKIT_INLINE_CACHE=1

# Environment variables for Python optimization
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONHASHSEED=random
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy and install Python dependencies first (for better caching)
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the application code
COPY . .

# Make startup scripts executable
RUN chmod +x /app/fast_start.sh
RUN chmod +x /app/railway_start.sh

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Railway will use the start command from settings
# This CMD is a fallback
CMD ["./fast_start.sh"]
