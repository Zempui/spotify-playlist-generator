from dataclasses import asdict
from flask import Flask, request, session, jsonify
import yaml
from spotipy.oauth2 import SpotifyOAuth
from error import APIError
from playlist_generator import PlaylistGenerator
from spotify_service import SpotifyService
from flasgger import Swagger

app = Flask(__name__)
app.secret_key = ''
app.config['SWAGGER'] = {
    'title': 'Flasgger RESTful',
    'uiversion': 3
}
swagger = Swagger(app)

def load_oauth_config():
    with open('config.yml', 'r', encoding='utf-8') as f:
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

@app.errorhandler(Exception)
def handle_exception(e):
    # Pasa la excepción a Flask para que la maneje
    response = jsonify({"error": str(e)})
    response.status_code = 500
    return response

@app.route('/')
def home():
    return 'Welcome to my spotify app! <a href="/login">Login on Spotify</a>'

@app.route('/login')
def login():
    """Login
    ---
    tags:
      - Spotify Service
    responses:
      200:
        description: The authorization URL for Spotify login.
        schema:
          type: object
          properties:
            auth_url:
              type: string
              description: The authorization URL.
    """
    auth_url = SPOTIFY_OAUTH.get_authorize_url()
    return {"auth_url": auth_url}

@app.route('/callback')
def callback():
    """Url de callback
    ---
    tags:
      - Spotify Service
    parameters:
      - name: code
        in: query
        type: string
        required: true
        description: The authorization code from Spotify.
    responses:
      200:
        description: The username of the logged in user.
        schema:
          type: object
          properties:
            username:
              type: string
              description: The username of the logged in user.
    """
    code = request.args.get('code')
    sp = loadSpotifyService(code)
    sp.auth.get_access_token(code, as_dict=False)
    username = sp.get_current_user()['id']
    session['code'] = code
    return {"username": username}

@app.route('/search_artist')
def search_artist():
    """Devuelve los artistas que coinciden con la búsqueda
    ---
    tags:
      - Spotify Service
    parameters:
      - name: query
        in: query
        type: string
        required: true
        description: The name of the artist to search for.
    responses:
      200:
        description: A list of artists matching the query.
      400:
        description: No query provided.
      401:
        description: You must login first.
      500:
        description: An error occurred.
    """
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
    """
    Crea la playlist
    ---
    tags:
      - Spotify Service
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            artists:
              type: array
              items:
                type: string
              description: The list of artists to include in the playlist.
            name:
              type: string
              description: The name of the playlist to be created.
        required: true
    responses:
      200:
        description: A message indicating that the playlist was created successfully.
        schema:
          type: object
          properties:
            message:
              type: string
              description: A message indicating that the playlist was created successfully.
      400:
        description: No artists provided.
      401:
        description: You must login first.
      500:
        description: An error occurred.
    """
    artists = request.json.get('artists')
    print(artists)
    name = request.json.get('name')
    
    if not 'code' in session.keys():
        return asdict(APIError('You must login first', 401))
    
    if not artists:
        return asdict(APIError('No artists provided', 400))
    try:
        loadSpotifyService(session['code']).create_playlist(artists, name)
        return {'message': 'Playlist created successfully'}
    except Exception as e:
        return asdict(APIError(str(e), 500))

if __name__ == '__main__':
    try:
        app.run(debug=True, host='0.0.0.0')
    except Exception as e:
        print(asdict(APIError(str(e), 500)))