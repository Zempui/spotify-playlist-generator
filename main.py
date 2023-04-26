from dataclasses import asdict
from flask import Flask, request
import yaml
from spotipy.oauth2 import SpotifyOAuth
from error import APIError
from playlist_generator import PlaylistGenerator
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
    return {"auth_url": auth_url}

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_info = SPOTIFY_OAUTH.get_access_token(code)
    access_token = token_info['access_token']
    username = SpotifyService.get_current_user()['id']
    SpotifyService.playlist_generator = PlaylistGenerator(auth_manager=SPOTIFY_OAUTH, username_id=SpotifyService.get_current_user()['id'])
    return {"access_token": access_token, "username": username}

@app.route('/search_artist')
def search_artist():
    artist = request.args.get('query')
    if not artist:
        return asdict(APIError('No query provided', 400))
    try:
        return SpotifyService.search_artist(artist)
    except Exception as e:
        return asdict(APIError(str(e), 500))

@app.route('/create_playlist', methods=['POST'])
def create_playlist():
    artists = request.json.get('artists')
    if not artists:
        return asdict(APIError('No artists provided', 400))
    try:
        SpotifyService.create_playlist(artists)
        return {'message': 'Playlist created successfully'}
    except Exception as e:
        return asdict(APIError(str(e), 500))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')