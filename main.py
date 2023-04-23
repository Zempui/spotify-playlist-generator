from flask import Flask, request, redirect
import yaml
from spotify_oauth import oauth2

app = Flask(__name__)

def load_oauth_config():
    with open('config_template.yml', 'r') as f:
        config = yaml.safe_load(f)
    oauth = oauth2(config['client_id'], config['client_secret'])
    return oauth

SPOTIFY_OAUTH = load_oauth_config()

@app.route('/')
def home():
    return 'Welcome to my spotify app! <a href="/login">Login on Spotify</a>'

@app.route('/login')
def login():
    return SPOTIFY_OAUTH.authorize_user()

@app.route('/callback')
def callback():
    code = request.args.get('code')
    SPOTIFY_OAUTH.get_token(code)
    username = SPOTIFY_OAUTH.get_user_info()["display_name"]
    return f'Access token obtained: {SPOTIFY_OAUTH.access_token} <br>Welcome {username}! <a href="/playlists">Get your playlists</a>'

@app.route('/playlists')
def playlists():
    try:
        playlists = SPOTIFY_OAUTH.get_playlists()["items"]
    except:
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