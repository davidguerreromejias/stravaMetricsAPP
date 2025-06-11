import os
from flask import Flask, redirect, request, session, url_for, render_template_string
import requests

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
        return render_template_string(
            """
            <!doctype html>
            <html lang=\"es\">
            <head>
                <meta charset=\"utf-8\">
                <title>Strava Metrics</title>
                <style>
                    body {font-family: Arial, sans-serif; text-align: center; padding-top: 100px;}
                    .btn {background-color: #FC4C02; color: white; padding: 15px 32px; text-decoration: none; font-size: 16px; border-radius: 4px;}
                </style>
            </head>
            <body>
                <h1>Bienvenido {{athlete['firstname']}} {{athlete['lastname']}}</h1>
                <p>Strava ID: {{athlete['id']}}</p>
                <a class=\"btn\" href=\"/logout\">Cerrar sesión</a>
            </body>
            </html>
            """,
            athlete=athlete,
        )
    return render_template_string(
        """
        <!doctype html>
        <html lang=\"es\">
        <head>
            <meta charset=\"utf-8\">
            <title>Strava Metrics</title>
            <style>
                body {font-family: Arial, sans-serif; text-align: center; padding-top: 100px;}
                .btn {background-color: #FC4C02; color: white; padding: 15px 32px; text-decoration: none; font-size: 16px; border-radius: 4px;}
            </style>
        </head>
        <body>
            <h1>Bienvenido a Strava Metrics</h1>
            <p>Conecta tu cuenta para comenzar</p>
            <a class=\"btn\" href=\"/login\">Acceder con Strava</a>
        </body>
        </html>
        """
    )

@app.route("/login")
def login():
    params = {
        'client_id': STRAVA_CLIENT_ID,
        'redirect_uri': STRAVA_REDIRECT_URI,
        'response_type': 'code',
        'scope': 'read',
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
