import nltk
import pandas as pd
import datetime
from tqdm import trange

from api_clients.GeniusClient import GeniusClient
from api_clients.SpotifyClient import SpotifyClient
from config import CRAWLED_TRACKS, CRAWLED_AUDIO_FEATURES, CRAWLED_LYRICS, TOLERANCE, TOP_SONGS, ALREADY_RECOMMENDED
from model import Model
from utils import save, load

sp = SpotifyClient()
g = GeniusClient()


def start():
    sp.authenticate()
    tracks = crawl_discover_weekly()
    tracks = load(CRAWLED_TRACKS)
    df = get_all_attributes(tracks)
    model = Model(df)
    model.run()
    top = model.df[model.df['score'] > TOLERANCE][['id', 'score']].sort_values('score', ascending=False)
    description = top[:30]['score'].describe()
    description = "On average like {}%, the top one is {}%, worst is approx {}%.".format(
        int(100*description['mean']),
        int(100*description['max']),
        int(100*description['min']))

    next_recommended = top[:31]['id'].tolist()

    already_recommended = load(ALREADY_RECOMMENDED)
    already_recommended.update(next_recommended)
    save(already_recommended, ALREADY_RECOMMENDED)

    sp.add_to_reccomendation_playlist(top['id'][:31].tolist())
    sp.set_reccomendation_playlist_details(description)


def crawl_discover_weekly():
    crawled_track_ids = set()
    all_tracks = []
    already_saved_track_ids = [track['id'] for track in sp.get_saved_tracks()]
    discover_weekly = sp.get_discover_weekly()
    for i in trange(len(discover_weekly)):
        track = discover_weekly[i]
        track_id, artists = track['id'], track['artists']
        track_radio = sp.get_track_radio(track_id=track_id)

        artist_radio = []
        for artist in artists:
            artist_radio.extend(sp.get_artist_radio(artist['id']))

        all_radio = track_radio + artist_radio
        all_tracks.extend(all_radio)
        crawled_track_ids.update([track['id'] for track in all_radio])

    unique_tracks = []
    already_recommended = load(ALREADY_RECOMMENDED)
    # already_recommended = set()
    for track in all_tracks:
        if track['id'] in crawled_track_ids:
            crawled_track_ids.remove(track['id'])
            if track['id'] not in already_saved_track_ids and track['id'] not in already_recommended:
                unique_tracks.append(track)

    save(unique_tracks, CRAWLED_TRACKS)
    return unique_tracks


def get_all_attributes(tracks):
    ids, names, artists = [], [], []
    drop_columns = ['album', 'available_markets', 'disc_number',
                    'explicit', 'external_ids', 'external_urls', 'href',
                    'is_local', 'preview_url', 'track_number', 'type',
                    'uri', 'analysis_url', 'time_signature', 'uri',
                    'track_href', 'speechiness', 'name', 'artists',
                    'popularity', 'mode']

    for track in tracks:
        ids.append(track['id'])
        names.append(track['name'])
        artist = []
        for a in track['artists']:
            artist.append(a['name'])
        artists.append(artist)

    df = pd.DataFrame(tracks)

    # Get features
    audio_features = sp.get_audio_features(track_ids=ids)
    lyrics = g.get_lyrics(names, artists)
    audio_df = pd.DataFrame(audio_features)
    audio_cols = list(audio_df.columns)
    df[audio_cols] = audio_df[audio_cols]
    df.drop(drop_columns, axis=1, inplace=True)
    df['lyrics'] = pd.Series(lyrics)
    return df


if __name__ == "__main__":
    start()
