FROM python:3.11-slim as builder

WORKDIR /app

### --- STAGE 1: Builder ---
# This stage installs all dependencies, including build-time tools.

# Set environment variables for a consistent build environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# CRITICAL OPTIMIZATION: Copy only the requirements file first
# This layer is only invalidated when requirements.txt changes.
COPY requirements.txt ./

# Install Python dependencies into a separate directory for the final stage
# This includes the special index for torch/cpu
RUN pip install --upgrade pip \
    && pip install --prefix=/install torch torchvision --index-url https://download.pytorch.org/whl/cpu \
    && pip install --prefix=/install -r requirements.txt

# Now, copy the rest of the application source code
COPY . .


### --- STAGE 2: Final Image ---
# This stage creates the lean, final image for production.
FROM python:3.11-slim

# Set the same consistent environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random

WORKDIR /app

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
# Set ownership to the new non-root user
COPY --from=builder --chown=app:app /app /app

# Switch to the non-root user
USER app

# Ensure the startup script is executable
RUN chmod +x fast_start.sh

# The command to run when the container starts
CMD ["./fast_start.sh"]
COPY requirements.txt ./
RUN apt-get update && apt-get install -y --no-install-recommends \
    git build-essential libpq-dev libjpeg-dev libpng-dev libfreetype6-dev \
    && pip install --upgrade pip \
    && pip install --prefix=/install torch torchvision --index-url https://download.pytorch.org/whl/cpu \
    && pip install --prefix=/install -r requirements.txt \
    && apt-get purge -y build-essential \
    && rm -rf /var/lib/apt/lists/* /root/.cache/pip

FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    git libpq5 libglib2.0-0 libsm6 libxext6 libxrender1 \
    libjpeg62-turbo libpng16-16 libfreetype6 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local
COPY . .

# Set PYTHONPATH so 'backend.core' is always importable
ENV PYTHONPATH=/app

RUN [ -f fast_start.sh ] && chmod +x fast_start.sh || true


# Debug: List files in backend directory
RUN ls -l backend/
# Debug: List files in backend/core directory
RUN ls -l backend/core/

# Run migrations and create test superuser
RUN python manage.py migrate && python run_create_test_superuser.py

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1


CMD ["./fast_start.sh"]
