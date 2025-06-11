# stravaMetricsAPP

Small Flask application that demonstrates authenticating with the Strava API.

## Setup

1. Create a Strava API application to obtain a `client_id` and `client_secret`.
2. Set the following environment variables:

```bash
export STRAVA_CLIENT_ID=<your_client_id>
export STRAVA_CLIENT_SECRET=<your_client_secret>
export FLASK_SECRET_KEY=<random_secret>
```

3. Install dependencies and run the application:

```bash
pip install -r requirements.txt
python app/app.py
```

Once running, open `http://localhost:5000` in your browser and click the login link to authorize access with Strava.
