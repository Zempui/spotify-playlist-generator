from dataclasses import asdict
import spotipy

from error import APIError
from playlist_generator import PlaylistGenerator

class SpotifyService():

    auth = None
    playlist_generator: PlaylistGenerator = None

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
    def search_artist(artist_name):
        if SpotifyService.playlist_generator is None:
            return asdict(APIError('You must login first', 403))
        
        sp = spotipy.Spotify(auth_manager = SpotifyService.auth)
        artists = sp.search(q=artist_name, type="artist", limit=10)
        artists = [{"name": artist["name"], "id": artist["id"]} for artist in artists["artists"]["items"]]
        return artists

    @staticmethod
    def create_playlist(artists):
        if SpotifyService.playlist_generator is None:
            return asdict(APIError('You must login first', 403))
        songs = []
        for artist in artists:
            songs.extend(SpotifyService.search_artist_songs(artist))

        SpotifyService.playlist_generator.playlist_generate(songs)
    
    @staticmethod
    def search_artist_songs(artist_name):
        if SpotifyService.playlist_generator is None:
            return asdict(APIError('You must login first', 403))
        songs = SpotifyService.playlist_generator.track_search(artist_name, 10, "songs")
        songs = [song["id"] for song in songs]
        return songs