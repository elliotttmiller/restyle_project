FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies and Python packages in one layer
COPY requirements.txt .
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev libjpeg-dev libpng-dev libfreetype6-dev \
    && pip install --upgrade pip \
    && pip install --prefix=/install torch torchvision --index-url https://download.pytorch.org/whl/cpu \
    && pip install --prefix=/install -r requirements.txt \
    && apt-get purge -y build-essential \
    && rm -rf /var/lib/apt/lists/* /root/.cache/pip

FROM python:3.11-slim

WORKDIR /app

# Install runtime deps, copy packages, and setup in one layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 libglib2.0-0 libsm6 libxext6 libxrender1 \
    libjpeg62-turbo libpng16-16 libfreetype6 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local
COPY . .
RUN [ -f fast_start.sh ] && chmod +x fast_start.sh || true

# Debug: List files in backend directory
RUN ls -l backend/

# Ensure test user is superuser/staff on every deploy
RUN python manage.py migrate && python run_create_test_superuser.py

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

CMD ["./fast_start.sh"]
