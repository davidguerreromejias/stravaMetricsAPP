# stravaMetricsAPP

This is a minimal Flask application that demonstrates logging in to Strava via OAuth and displaying basic athlete information.

## Setup

1. Create a [Strava application](https://www.strava.com/settings/api) and obtain your `Client ID` and `Client Secret`.
2. Set the following environment variables (you can place them in a `.env` file):
   - `STRAVA_CLIENT_ID`
   - `STRAVA_CLIENT_SECRET`
   - `STRAVA_REDIRECT_URI` (optional, defaults to `http://localhost:5000/callback`)
   - `SECRET_KEY` (any random string for Flask sessions)

The provided `setup.sh` script will create a virtual environment and install the requirements automatically.

## Running

```bash
./setup.sh
```

This command sets up a virtual environment (if needed), installs the dependencies and starts the server. Once running, open `http://localhost:5000` in your browser and click "Connect with Strava".
