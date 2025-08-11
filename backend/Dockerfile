# --- STAGE 1: Builder ---
FROM python:3.11-slim as builder

WORKDIR /app

# Set environment variables for a consistent build environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first for better caching
COPY requirements.txt ./

# Install Python dependencies into a separate directory for the final stage
RUN pip install --upgrade pip \
    && pip install --prefix=/install torch torchvision --index-url https://download.pytorch.org/whl/cpu \
    && pip install --prefix=/install -r requirements.txt

# Now, copy the rest of the application source code
COPY . .

# --- STAGE 2: Final Image ---
FROM python:3.11-slim

WORKDIR /app

# Set environment variables for runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PYTHONPATH=/app

# Install ONLY runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# SECURITY ENHANCEMENT: Create a non-root user to run the application
RUN addgroup --system app && adduser --system --group app

# Copy installed Python packages from the builder stage
COPY --from=builder /install /usr/local

# Copy the application code from the builder stage
COPY --from=builder --chown=app:app /app /app

# Switch to the non-root user
USER app

# Ensure the startup script is executable
RUN chmod +x fast_start.sh

# The command to run when the container starts
CMD ["./fast_start.sh"]
