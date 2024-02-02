from dataclasses import asdict
import spotipy
from error import APIError
from playlist_generator import PlaylistGenerator

class SpotifyService():

    auth = None
    playlist_generator: PlaylistGenerator = None

    def get_current_user(self):
        try:
            current_user = spotipy.Spotify(auth_manager = self.auth).current_user()
            return current_user
        except spotipy.SpotifyException as e:
            print("Error obtaining current user")
            if e.http_status == 400:
                self.auth.refresh_access_token(self.auth.get_cached_token()['refresh_token'])
                sp = spotipy.Spotify(auth_manager = self.auth)
                user_info = sp.current_user()
                return user_info
            else:
                raise e

    def search_artist(self, artist_name: str):
        if self.playlist_generator is None:
            return asdict(APIError('You must login first', 403))
        
        sp = spotipy.Spotify(auth_manager = self.auth)
        artists = sp.search(q=artist_name, type="artist", limit=10)
        artists = [{"name": artist["name"], "id": artist["id"], "image": artist["images"][-1]} for artist in artists["artists"]["items"]]
        return artists

    def create_playlist(self, artists: list, name):
        if self.playlist_generator is None:
            return asdict(APIError('You must login first', 403))
        songs = []
        for artist in artists:
            songs.extend(self.search_artist_songs(artist))

        self.playlist_generator.playlist_generate(songs, name)
    
    def search_artist_songs(self, artist_name: str):
        if self.playlist_generator is None:
            return asdict(APIError('You must login first', 403))
        songs = self.playlist_generator.track_search(artist_name, 10, "songs")
        songs = [song["id"] for song in songs]
        return songs