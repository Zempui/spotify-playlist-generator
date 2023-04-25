from flask import Flask, request, redirect
import yaml
from spotipy.oauth2 import SpotifyOAuth
from spotify_service import SpotifyService

app = Flask(__name__)

def load_oauth_config():
    with open('config.yml', 'r') as f:
        config = yaml.safe_load(f)
    sp = SpotifyOAuth(client_id=config["client_id"], client_secret=config["client_secret"], redirect_uri=config["redirect_uri"], scope=config["scope"])
    return sp

SPOTIFY_OAUTH = load_oauth_config()
SpotifyService.auth = SPOTIFY_OAUTH

@app.route('/')
def home():
    return 'Welcome to my spotify app! <a href="/login">Login on Spotify</a>'

@app.route('/login')
def login():
    auth_url = SPOTIFY_OAUTH.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_info = SPOTIFY_OAUTH.get_access_token(code)
    access_token = token_info['access_token']
    username = SpotifyService.get_current_user()['id']
    return f'Access token obtained: {access_token} <br>Welcome {username}! <a href="/playlists">Get your playlists</a>'

@app.route('/playlists')
def playlists():
    try:
        playlists = SpotifyService.get_user_playlists()["items"]
    except Exception as e:
        return redirect("/login")
    response = "<ul>"
    for playlist in playlists:
        response += f"<li>{playlist['name']}</li>"
    response += "</ul><br><a href='/logout''>Logout</a>"
    return response

@app.route("/logout")
def logout():
    response = redirect("https://accounts.spotify.com/es-ES/status")
    return response 

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')