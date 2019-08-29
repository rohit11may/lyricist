from api_clients.GeniusClient import GeniusClient
from api_clients.SpotifyClient import SpotifyClient

sp = SpotifyClient()
g = GeniusClient()


def start():
    sp.authenticate()
    # print(g.get_lyrics(['hot girl bummer'], [['blackbear']]))
    # print(sp.get_genres([['0OdUWJ0sBjDrqHygGUXeCF']]))
