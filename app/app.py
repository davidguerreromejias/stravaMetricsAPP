import os
from flask import Flask, redirect, request, session
import requests

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'change_this_secret')

STRAVA_CLIENT_ID = os.environ.get('STRAVA_CLIENT_ID')
STRAVA_CLIENT_SECRET = os.environ.get('STRAVA_CLIENT_SECRET')

@app.route('/')
def index():
    if 'token' in session:
        return f"Logged in with token: {session['token']}"
    return '<a href="/login">Login with Strava</a>'

@app.route('/login')
def login():
    redirect_uri = request.url_root.rstrip('/') + '/callback'
    auth_url = (
        'https://www.strava.com/oauth/authorize'
        f'?client_id={STRAVA_CLIENT_ID}'
        '&response_type=code'
        f'&redirect_uri={redirect_uri}'
        '&approval_prompt=auto'
        '&scope=read,activity:read'
    )
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return 'No code returned', 400
    token_resp = requests.post(
        'https://www.strava.com/api/v3/oauth/token',
        data={
            'client_id': STRAVA_CLIENT_ID,
            'client_secret': STRAVA_CLIENT_SECRET,
            'code': code,
            'grant_type': 'authorization_code',
        },
    )
    if token_resp.status_code != 200:
        return f"Error fetching token: {token_resp.text}", 400
    data = token_resp.json()
    session['token'] = data.get('access_token')
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
