#!/bin/bash
# fast_start.sh

# Exit immediately if a command exits with a non-zero status.
set -e

# 1. Run Database Migrations (Runtime Operation)
echo "INFO: Running database migrations..."
python manage.py migrate --noinput

# 2. Create/Update the Test Superuser (Runtime Operation)
# This uses the management command we created in previous steps.
echo "INFO: Ensuring test superuser exists..."
python manage.py create_test_superuser

# 3. Start the Gunicorn Server (Main Process)
echo "INFO: Starting Gunicorn server with gevent workers..."
# The 'exec' command replaces the shell process with the Gunicorn process,
# which is the correct way to run the main container command.
# This includes the critical gevent worker and timeout fixes.
exec gunicorn --worker-class gevent --workers 4 --timeout 120 --log-level debug backend.wsgi