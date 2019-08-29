from api_clients.GeniusClient import GeniusClient
from api_clients.SpotifyClient import SpotifyClient

sp = SpotifyClient()
g = GeniusClient()


def start():
    sp.authenticate()
    tracks = sp.get_top_tracks(time_range='long_term')

    # print(sp.get_genres([['0OdUWJ0sBjDrqHygGUXeCF']]))
start()