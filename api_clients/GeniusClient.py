import requests
from bs4 import BeautifulSoup
from tqdm import trange

from config import GENIUS_TOKEN, LYRICS
from utils import load, save


def request_song_info(song_title, artist_name):
    base_url = 'https://api.genius.com'
    headers = {'Authorization': 'Bearer ' + GENIUS_TOKEN}
    search_url = base_url + '/search'
    data = {'q': song_title + ' ' + artist_name}
    response = requests.get(search_url, data=data, headers=headers)
    return response


def scrape_song_url(url):
    page = requests.get(url)
    html = BeautifulSoup(page.text, 'html.parser')
    lyrics = html.find('div', class_='lyrics').get_text()
    return lyrics


def extract_lyrics(song_title, artist_name):
    # Search for matches in the request response
    response = request_song_info(song_title, artist_name)
    json = response.json()
    remote_song_info = None

    if json:
        for hit in json['response']['hits']:
            if artist_name.lower() in hit['result']['primary_artist']['name'].lower():
                remote_song_info = hit
                break

        # Extract lyrics from URL if the song was found
        if remote_song_info:
            song_url = remote_song_info['result']['url']
            return scrape_song_url(song_url)

    return "NA"


class GeniusClient():

    @staticmethod
    def get_lyrics(names, artists):
        """

        :param names: List of track names
        :param artists: List of lists of artists
        :return: List of lyrics in the order requested, updates the map too.
        """
        try:
            lyrics = load(LYRICS)
        except Exception:
            lyrics = {}

        lyrics_list = []
        for i in trange(len(names)):
            name, artist = names[i], artists[i]
            key = "{},{}".format(name, ",".join(artist))
            if lyrics.get(key, 0) == 0:
                lyrics[key] = extract_lyrics(name, artist[0])

            lyrics_list.append(lyrics[key])
            if i % 100 == 0:
                save(lyrics, LYRICS)

        save(lyrics, LYRICS)
        return lyrics_list
