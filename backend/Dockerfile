FROM python:3.11-slim-buster

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the application code into the container
COPY . .

# Make railway_start.sh executable
RUN chmod +x /app/railway_start.sh

# Collect static files at build time
RUN python manage.py collectstatic --noinput

# Copy the Python startup script
COPY start.py /app/start.py

# Use railway_start.sh as the entrypoint
CMD ["/app/railway_start.sh"]
