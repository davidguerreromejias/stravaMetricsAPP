import os
from datetime import datetime
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


def _year_stats(headers, year, activity_type):
    """Return aggregated stats for a given year and activity type."""
    start = int(datetime(year, 1, 1).timestamp())
    end = int(datetime(year + 1, 1, 1).timestamp())
    page = 1
    per_page = 50
    activities = []
    while True:
        resp = requests.get(
            "https://www.strava.com/api/v3/athlete/activities",
            headers=headers,
            params={"after": start, "before": end, "page": page, "per_page": per_page},
        )
        if resp.status_code != 200:
            break
        data = resp.json()
        if activity_type != "all":
            data = [a for a in data if a.get("type") == activity_type]
        activities.extend(data)
        if len(data) < per_page:
            break
        page += 1

    segments = 0
    prs = 0
    for a in activities:
        detail = requests.get(
            f"https://www.strava.com/api/v3/activities/{a['id']}",
            headers=headers,
            params={"include_all_efforts": "true"},
        )
        if detail.status_code != 200:
            continue
        effs = detail.json().get("segment_efforts", [])
        segments += len(effs)
        prs += sum(1 for e in effs if e.get("pr_rank") == 1)

    total_km = sum(a.get("distance", 0) for a in activities) / 1000
    monthly = [0] * 12
    for a in activities:
        dt = datetime.fromisoformat(a["start_date"].replace("Z", "+00:00"))
        monthly[dt.month - 1] += 1

    return {
        "count": len(activities),
        "distance": total_km,
        "segments": segments,
        "prs": prs,
        "monthly_counts": monthly,
    }

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change_me")

# Month names for stats charts
MONTHS = [
    "Enero",
    "Febrero",
    "Marzo",
    "Abril",
    "Mayo",
    "Junio",
    "Julio",
    "Agosto",
    "Septiembre",
    "Octubre",
    "Noviembre",
    "Diciembre",
]

STRAVA_CLIENT_ID = os.environ.get("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.environ.get("STRAVA_CLIENT_SECRET")
STRAVA_REDIRECT_URI = os.environ.get("STRAVA_REDIRECT_URI", "http://localhost:5000/callback")

OAUTH_AUTHORIZE_URL = "https://www.strava.com/oauth/authorize"
OAUTH_TOKEN_URL = "https://www.strava.com/oauth/token"
ATHLETE_URL = "https://www.strava.com/api/v3/athlete"


@app.route("/set_activity_type", methods=["POST"])
def set_activity_type():
    """Store selected activity type in the session and redirect back."""
    session["activity_type"] = request.form.get("activity_type", "all")
    return redirect(request.referrer or url_for("index"))


@app.route("/set_year", methods=["POST"])
def set_year():
    """Store selected year in the session and redirect back."""
    try:
        session["year"] = int(request.form.get("year"))
    except (TypeError, ValueError):
        session["year"] = datetime.utcnow().year
    return redirect(request.referrer or url_for("index"))


@app.route("/set_segments_count", methods=["POST"])
def set_segments_count():
    """Store number of starred segments to display and redirect back."""
    try:
        session["segments_count"] = int(request.form.get("segments_count", 5))
    except (TypeError, ValueError):
        session["segments_count"] = 5
    return redirect(request.referrer or url_for("index"))

@app.route("/")
def index():
    if "athlete" in session:
        athlete = session["athlete"]

        activity_type = session.get("activity_type", "all")
        selected_year = session.get("year", datetime.utcnow().year)

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

        if activity_type != "all":
            activities = [a for a in activities if a.get("type") == activity_type]

        segments_count = session.get("segments_count", 5)
        starred_segments = requests.get(
            "https://www.strava.com/api/v3/segments/starred",
            headers=headers,
            params={"per_page": segments_count},
        ).json()

        for seg in starred_segments:
            pr = None
            kom_time = None

            pr = seg.get("athlete_segment_stats", {}).get("pr_elapsed_time")

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

        years = list(range(datetime.utcnow().year, datetime.utcnow().year - 5, -1))
        year_stats = _year_stats(headers, selected_year, activity_type)
        months = MONTHS

        return render_template(
            "index.html",
            athlete=athlete,
            stats=stats,
            friends=friends,
            routes=routes,
            activities=activities,
            activity_type=activity_type,
            starred_segments=starred_segments,
            year_stats=year_stats,
            years=years,
            selected_year=selected_year,
            months=months,
            segments_count=segments_count,
        )
    years = list(range(datetime.utcnow().year, datetime.utcnow().year - 5, -1))
    selected_year = session.get("year", datetime.utcnow().year)
    months = MONTHS
    segments_count = session.get("segments_count", 5)
    return render_template(
        "index.html",
        athlete=None,
        activity_type=session.get("activity_type", "all"),
        years=years,
        selected_year=selected_year,
        year_stats={"count": 0, "distance": 0, "segments": 0, "prs": 0, "monthly_counts": [0]*12},
        months=months,
        segments_count=segments_count,
    )

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
