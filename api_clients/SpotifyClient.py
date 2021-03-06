import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from config import *

from tqdm import trange

from utils import load, save


class SpotifyClient(spotipy.Spotify):
    sp_oauth = SpotifyOAuth(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, scope=SCOPE, cache_path=CACHE)

    def authenticate(self):
        token = self.sp_oauth.get_cached_token()['access_token']
        super().__init__(token)

    def refresh(self):
        """
        Gets cached token from .spotipyoauthcache and refreshes its own access token using the refresh token.
        """
        cached_token_info = self.sp_oauth.get_cached_token()
        if self.sp_oauth.is_token_expired(cached_token_info):
            token_info = self.sp_oauth.refresh_access_token(cached_token_info['refresh_token'])
            super().__init__(token_info['access_token'])

    def get_saved_tracks(self):
        """

        :return: A list of TRACK json objects.
        """
        self.refresh()
        results = self.current_user_saved_tracks()
        tracks = results['items']
        while results['next']:
            results = self.next(results)
            tracks.extend(results['items'])
        tracks = [item['track'] for item in tracks]
        return tracks

    def get_audio_features(self, track_ids):
        """

        :param track_ids: List of ID strings of all the tracks requested
        :return: A list of AUDIO_FEATURES json objects
        """
        self.refresh()
        num_tracks = len(track_ids)
        audio_features = []
        step = 50
        for i in trange(0, num_tracks, step):
            audio_features.extend(self.audio_features(track_ids[i:min(i + step, num_tracks)]))
        return audio_features

    def get_genres(self, artist_ids):
        """

        :param artist_ids: List of artist ID strings of all the artists requested
        :return: A list of genre lists in the same order as the artists requested
        """
        self.refresh()
        try:
            artist_genre_map = load(GENRE_MAP)
        except Exception:
            artist_genre_map = {}

        all_genres = []
        for i in trange(len(artist_ids)):
            current_artist_ids = artist_ids[i]
            genres = set()
            for artist_id in current_artist_ids:
                if artist_id not in artist_genre_map:
                    artist_genre_map[artist_id] = self.artist(artist_id)['genres']
                genres.update(artist_genre_map[artist_id])
            all_genres.append(list(genres))

        save(artist_genre_map, GENRE_MAP)
        return all_genres

    def get_top_artists(self, time_range):
        """

        :param time_range: 'short_term' - 4w, 'medium_term' - 6m 'long_term' - all time
        :return: list of ARTIST json objects
        """
        self.refresh()
        return self.current_user_top_artists(limit=50, time_range=time_range)['items']

    def get_top_tracks(self, time_range):
        """

        :param time_range: 'short_term' - 4w, 'medium_term' - 6m 'long_term' - all time
        :return: list of TRACK json objects
        """
        self.refresh()
        return self.current_user_top_tracks(limit=50, time_range=time_range)['items']

    def get_discover_weekly(self):
        """

        :return: list of TRACK json objects
        """
        self.refresh()
        playlist_tracks = self.user_playlist(user=USERNAME,
                                             playlist_id=MY_DISCOVER_WEEKLY,
                                             fields='tracks')['tracks']['items']
        return [track['track'] for track in playlist_tracks]

    def get_track_radio(self, track_id, limit=50):
        """

        :param track_id: id of track to generate radio for
        :param limit: number of songs to return (max 100)
        :return: list of TRACK json objects
        """
        self.refresh()
        return self.recommendations(seed_tracks=[track_id], limit=limit)['tracks']

    def get_artist_radio(self, artist_id, limit=50):
        """

        :param artist_id: id of artist to generate radio for
        :param limit: number of songs to return (max 100)
        :return:
        """
        self.refresh()
        return self.recommendations(seed_artists=[artist_id], limit=limit)['tracks']

    def get_related_artists(self, artist_id):
        """

        :param artist_id: id of artist to get related artists for
        :return: list of ARTIST json objects
        """
        self.refresh()
        return self.artist_related_artists(artist_id)['artists']

    def add_to_reccomendation_playlist(self, track_ids):
        self.refresh()
        self.user_playlist_replace_tracks(user=USERNAME, playlist_id=RECC_PLAYLIST,
                                          tracks=track_ids)

    def set_reccomendation_playlist_details(self, details):
        self.refresh()
        self.user_playlist_change_details(user=USERNAME, playlist_id=RECC_PLAYLIST,
                                          description=details)
