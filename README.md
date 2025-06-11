# stravaMetricsAPP

This is a minimal Flask application that demonstrates logging in to Strava via OAuth and displaying basic athlete information.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Create a [Strava application](https://www.strava.com/settings/api) and obtain your `Client ID` and `Client Secret`.
3. Set the following environment variables:
   - `STRAVA_CLIENT_ID`
   - `STRAVA_CLIENT_SECRET`
   - `STRAVA_REDIRECT_URI` (optional, defaults to `http://localhost:5000/callback`)
   - `SECRET_KEY` (any random string for Flask sessions)

## Running

```bash
python app.py
```

Then open `http://localhost:5000` in your browser and click "Connect with Strava".