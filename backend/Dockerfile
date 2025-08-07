
FROM python:3.11

# Install system dependencies for ML/AI
RUN apt-get update && apt-get install -y \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libjpeg-dev \
    && rm -rf /var/lib/apt/lists/*

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

# Copy and install Python dependencies first (for better caching)
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the application code
COPY . .

# Make startup scripts executable
RUN chmod +x /app/fast_start.sh

# Railway will use the start command from settings
# This CMD is a fallback
CMD ["./fast_start.sh"]
