# stravaMetricsAPP

This is a minimal Flask application that demonstrates logging in to Strava via OAuth and displaying athlete data such as recent activities, routes and friends.

## Setup

1. Create a [Strava application](https://www.strava.com/settings/api) and obtain your `Client ID` and `Client Secret`.
2. Copy the provided `.env.example` to `.env` and fill in your values. The required variables are:
   - `STRAVA_CLIENT_ID`
   - `STRAVA_CLIENT_SECRET`
   - `STRAVA_REDIRECT_URI` (optional, defaults to `http://localhost:5000/callback`)
   - `SECRET_KEY` (any random string for Flask sessions)

The provided `setup.sh` script will create a virtual environment and install the requirements automatically.

The application requests the `read`, `profile:read_all` and `activity:read` scopes so it can display basic profile details, your recent activities, routes and friends.

## Running

```bash
./setup.sh
```

This command sets up a virtual environment (if needed), installs the dependencies and starts the server. Once running, open `http://localhost:5000` in your browser and click "Connect with Strava".

After authenticating you will see a modern dashboard built with Bootstrap and Chart.js displaying your statistics, a list of friends, your routes and your most recent activities.

You can also choose how many of your starred segments are shown using the selector in the navigation bar.
