from flask import redirect
import requests

class oauth2:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.user_info = None

    def authorize_user(self):
        authorization_url = "https://accounts.spotify.com/authorize"
        redirect_uri = "http://localhost:5000/callback"
        scopes = ["user-read-private", "user-read-email"]
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "scope": " ".join(scopes)
        }
        return redirect(authorization_url + '?' + '&'.join([f'{k}={v}' for k,v in params.items()]))

    def get_token(self, authorization_code):
        token_url = "https://accounts.spotify.com/api/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": "http://localhost:5000/callback",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        response = requests.post(token_url, headers=headers, data=data)
        if response.status_code == 200:
            self.access_token = response.json()["access_token"]
            return True
        else:
            print("Could not obtain token")
            return False

    def get_user_info(self):
        if not self.user_info is None:
            return self.user_info
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get("https://api.spotify.com/v1/me", headers=headers)
        if response.status_code == 200:
            self.user_info = response.json()
            return response.json()
        else:
            print("Could not obtain user info")
            return None
    
    def get_playlists(self):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        user_id = self.get_user_info()["id"]
        limit = 10
        response = requests.get(f"https://api.spotify.com/v1/users/{user_id}/playlists?offset=0&limit={limit}", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print("Could not obtain user playlists")
            return None
