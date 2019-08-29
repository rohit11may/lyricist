from flask import Flask, request
import crawler
from config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SCOPE, CACHE
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

sp_oauth = SpotifyOAuth(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, scope=SCOPE, cache_path=CACHE)

app = Flask(__name__)


@app.route('/')
def index():
    access_token = ""
    token_info = sp_oauth.get_cached_token()

    if token_info:
        crawler.start(token_info['access_token'])
        return "Found cached token!"
    else:
        url = request.url
        code = sp_oauth.parse_response_code(url)
        if code:
            print("Trying to get valid access token from URL...")
            token_info = sp_oauth.get_access_token(code)
            crawler.start(token_info['access_token'])
            return "Got new token!"

    return htmlForLoginButton()


def htmlForLoginButton():
    auth_url = getSPOauthURI()
    htmlLoginButton = "<a href='" + auth_url + "'>Login to Spotify</a>"
    return htmlLoginButton


def getSPOauthURI():
    auth_url = sp_oauth.get_authorize_url()
    return auth_url
