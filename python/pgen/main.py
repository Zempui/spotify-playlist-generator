from dataclasses import asdict
from flask import Flask, request, session
import yaml
from spotipy.oauth2 import SpotifyOAuth
from error import APIError
from playlist_generator import PlaylistGenerator
from spotify_service import SpotifyService

app = Flask(__name__)
app.secret_key = ''

def load_oauth_config():
    with open('config.yml', 'r') as f:
        config = yaml.safe_load(f)
    sp = SpotifyOAuth(client_id=config["client_id"], client_secret=config["client_secret"], redirect_uri=config["redirect_uri"], scope=config["scope"])
    app.secret_key = config['secret']
    return sp

def loadSpotifyService(code):
    sp = SpotifyService()
    sp.auth = SPOTIFY_OAUTH
    sp.auth.get_access_token(code, as_dict=False)
    sp.playlist_generator = PlaylistGenerator(auth_manager=SPOTIFY_OAUTH, username_id=sp.get_current_user()['id'])
    return sp


SPOTIFY_OAUTH = load_oauth_config()

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
    sp = loadSpotifyService(code)
    sp.auth.get_access_token(code, as_dict=False)
    username = sp.get_current_user()['id']
    session['code'] = code
    return {"username": username}

@app.route('/search_artist')
def search_artist():
    artist = request.args.get('query')
    if not artist:
        return asdict(APIError('No query provided', 400))
    
    if not 'code' in session.keys():
        return asdict(APIError('You must login first', 401))
    
    try:
        return loadSpotifyService(session['code']).search_artist(artist)
    except Exception as e:
        return asdict(APIError(str(e), 500))

@app.route('/create_playlist', methods=['POST'])
def create_playlist():
    artists = request.json.get('artists')
    
    if not 'code' in session.keys():
        return asdict(APIError('You must login first', 401))
    
    if not artists:
        return asdict(APIError('No artists provided', 400))
    try:
        loadSpotifyService(session['code']).create_playlist(artists)
        return {'message': 'Playlist created successfully'}
    except Exception as e:
        return asdict(APIError(str(e), 500))

if __name__ == '__main__':
    try:
        app.run(debug=True, host='0.0.0.0')
    except Exception as e:
        print(asdict(APIError(str(e), 500)))