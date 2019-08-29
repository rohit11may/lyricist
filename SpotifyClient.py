import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SCOPE, CACHE


class SpotifyClient(spotipy.Spotify):
    authenticated = False
    sp_oauth = SpotifyOAuth(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, scope=SCOPE, cache_path=CACHE)

    def authenticate(self, token):
        super().__init__(token)

    def refresh(self):
        cached_token_info = self.sp_oauth.get_cached_token()
        token_info = self.sp_oauth.refresh_access_token(cached_token_info['refresh_token'])
        super().__init__(token_info['access_token'])
