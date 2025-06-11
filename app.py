import os
from flask import Flask, redirect, request, session, url_for, render_template
import requests


def _parse_time_str(t):
    """Convert a time string like '1:23' or '1:02:03' to seconds."""
    if not t:
        return None
    parts = [int(p) for p in t.split(":")]
    if len(parts) == 3:
        h, m, s = parts
    elif len(parts) == 2:
        h, m, s = 0, parts[0], parts[1]
    else:
        h, m, s = 0, 0, parts[0]
    return h * 3600 + m * 60 + s


def _format_seconds(seconds):
    """Return a hh:mm:ss string for a number of seconds."""
    if seconds is None:
        return None
    h, rem = divmod(int(seconds), 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change_me")

STRAVA_CLIENT_ID = os.environ.get("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.environ.get("STRAVA_CLIENT_SECRET")
STRAVA_REDIRECT_URI = os.environ.get("STRAVA_REDIRECT_URI", "http://localhost:5000/callback")

OAUTH_AUTHORIZE_URL = "https://www.strava.com/oauth/authorize"
OAUTH_TOKEN_URL = "https://www.strava.com/oauth/token"
ATHLETE_URL = "https://www.strava.com/api/v3/athlete"

@app.route("/")
def index():
    if "athlete" in session:
        athlete = session["athlete"]

        headers = {"Authorization": f"Bearer {session['access_token']}"}

        stats = requests.get(
            f"https://www.strava.com/api/v3/athletes/{athlete['id']}/stats",
            headers=headers,
        ).json()

        friends = requests.get(
            "https://www.strava.com/api/v3/athlete/friends",
            headers=headers,
            params={"per_page": 5},
        ).json()

        routes = requests.get(
            f"https://www.strava.com/api/v3/athletes/{athlete['id']}/routes",
            headers=headers,
            params={"per_page": 5},
        ).json()

        activities = requests.get(
            "https://www.strava.com/api/v3/athlete/activities",
            headers=headers,
            params={"per_page": 5},
        ).json()

        starred_segments = requests.get(
            "https://www.strava.com/api/v3/segments/starred",
            headers=headers,
            params={"per_page": 5},
        ).json()

        for seg in starred_segments:
            pr = None
            kom_time = None

            seg_stats = seg.get("athlete_segment_stats") or {}
            pr = seg_stats.get("pr_elapsed_time")

            xoms = seg.get("xoms") or {}
            kom_str = xoms.get("kom") or xoms.get("qom") or xoms.get("cr")
            if kom_str:
                kom_time = _parse_time_str(kom_str)

            if pr is not None and kom_time is not None:
                seg["kom_diff"] = pr - kom_time
            else:
                seg["kom_diff"] = None

            seg["pr_time"] = _format_seconds(pr) if pr is not None else None
            seg["kom_time"] = _format_seconds(kom_time) if kom_time is not None else None

        return render_template(
            "index.html",
            athlete=athlete,
            stats=stats,
            friends=friends,
            routes=routes,
            activities=activities,
            starred_segments=starred_segments,
        )
    return render_template("index.html", athlete=None)

@app.route("/login")
def login():
    params = {
        'client_id': STRAVA_CLIENT_ID,
        'redirect_uri': STRAVA_REDIRECT_URI,
        'response_type': 'code',
        'scope': 'read,profile:read_all,activity:read',
    }
    url = requests.Request('GET', OAUTH_AUTHORIZE_URL, params=params).prepare().url
    return redirect(url)

@app.route("/callback")
def callback():
    code = request.args.get('code')
    if not code:
        return 'Authorization failed', 400
    data = {
        'client_id': STRAVA_CLIENT_ID,
        'client_secret': STRAVA_CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
    }
    response = requests.post(OAUTH_TOKEN_URL, data=data)
    if response.status_code != 200:
        return 'Token exchange failed', 400
    token_data = response.json()
    access_token = token_data['access_token']
    athlete = token_data['athlete']
    session['access_token'] = access_token
    session['athlete'] = athlete
    return redirect(url_for('index'))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
