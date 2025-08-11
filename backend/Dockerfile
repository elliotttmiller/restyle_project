


# --- STAGE 1: Builder ---
FROM python:3.11-bullseye as builder

WORKDIR /app

# Set environment variables for a consistent build environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install only essential build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements for better caching
COPY backend/requirements.txt ./

# Install Python dependencies into a separate directory for the final stage
RUN pip install --upgrade pip \
    && pip install --prefix=/install torch torchvision --index-url https://download.pytorch.org/whl/cpu \
    && pip install --prefix=/install -r requirements.txt

# Now, copy the rest of the application source code
COPY . .



# --- STAGE 2: Final Image ---
FROM python:3.11-slim

# Set environment variables for runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set the correct WORKDIR for Django
WORKDIR /app/backend

# Install ONLY the essential runtime system dependencies (remove libglib2.0-0 unless strictly needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# SECURITY ENHANCEMENT: Create a non-root user
RUN addgroup --system app && adduser --system --group app

# Copy installed Python packages from the builder stage
COPY --from=builder /install /usr/local

# Copy the application code from the builder stage
COPY --from=builder --chown=app:app /app /app

# Switch to the non-root user
USER app

# Ensure the startup script is executable
RUN chmod +x ../fast_start.sh

# The command to run when the container starts
CMD ["../fast_start.sh"]
