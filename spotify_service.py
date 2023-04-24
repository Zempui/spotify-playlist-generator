import spotipy

class SpotifyService():

    auth = None

    @staticmethod
    def get_current_user():
        try:
            current_user = spotipy.Spotify(auth_manager = SpotifyService.auth).current_user()
            return current_user
        except spotipy.SpotifyException as e:
            print("Error obtaining current user")
            if e.http_status == 400:
                SpotifyService.auth.refresh_access_token(SpotifyService.auth.get_cached_token()['refresh_token'])
                sp = spotipy.Spotify(auth_manager = SpotifyService.auth)
                user_info = sp.current_user()
                return user_info
            else:
                raise e

    @staticmethod
    def get_user_playlists():
        user_id = SpotifyService.get_current_user()["id"]
        try:
            playlists = spotipy.Spotify(auth_manager = SpotifyService.auth).user_playlists(user_id)
            return playlists
        except Exception as e:
            print("Could not retreive playlists")
            raise e