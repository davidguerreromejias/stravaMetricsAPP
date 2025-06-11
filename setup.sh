#!/usr/bin/env bash
set -e

# Create virtual environment if not present
if [ ! -d venv ]; then
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Load environment variables from .env if present
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Ensure required variables are set
: "${STRAVA_CLIENT_ID:?Set STRAVA_CLIENT_ID in environment or .env}"
: "${STRAVA_CLIENT_SECRET:?Set STRAVA_CLIENT_SECRET in environment or .env}"
: "${SECRET_KEY:?Set SECRET_KEY in environment or .env}"

# Run the application
python app.py
