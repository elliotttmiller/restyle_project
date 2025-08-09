#!/bin/bash
# automate_test_superuser.sh
# This script sets up environment variables and runs the Django management command to create/update the test superuser.

# Set these as needed, or export them in your environment/CI/CD
USER_ARG=${1:-${TEST_USER:-testuser}}
PASS_ARG=${2:-${TEST_PASS:-testpass1234}}

export TEST_USER="$USER_ARG"
export TEST_PASS="$PASS_ARG"

# Run the Django management command
python backend/manage.py create_test_superuser

echo "Test superuser ensured. Credentials: $TEST_USER / $TEST_PASS"
