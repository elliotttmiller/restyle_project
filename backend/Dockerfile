

# ---- Build Stage ----
FROM python:3.11-slim as builder

# Install build dependencies only for pip install
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install pip dependencies in a separate layer for better caching
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --prefix=/install torch torchvision --index-url https://download.pytorch.org/whl/cpu && \
    pip install --prefix=/install -r requirements.txt

# ---- Final Stage ----
FROM python:3.11-slim

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libjpeg62-turbo \
    libpng16-16 \
    libfreetype6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only installed python packages from builder
COPY --from=builder /install /usr/local

# Copy only necessary source files (use .dockerignore to exclude unnecessary files)
COPY . .


# Make startup scripts executable if present
RUN [ -f /app/fast_start.sh ] && chmod +x /app/fast_start.sh || true

# Environment variables for Python optimization
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Railway will use the start command from settings
# This CMD is a fallback
CMD ["./fast_start.sh"]
