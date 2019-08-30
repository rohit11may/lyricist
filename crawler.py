from api_clients.GeniusClient import GeniusClient
from api_clients.SpotifyClient import SpotifyClient

sp = SpotifyClient()
g = GeniusClient()


def start():
    sp.authenticate()
