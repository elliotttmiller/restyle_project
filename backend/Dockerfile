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

# Collect static files at build time
RUN python manage.py collectstatic --noinput

# Copy and set permissions for the start script
COPY railway_start.sh /app/railway_start.sh
RUN chmod +x /app/railway_start.sh

# Use the start script as the entrypoint
CMD ["/app/railway_start.sh"]
