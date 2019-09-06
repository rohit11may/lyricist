from flask import Flask, request
from config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SCOPE, CACHE
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

sp_oauth = SpotifyOAuth(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, scope=SCOPE, cache_path=CACHE)

app = Flask(__name__)


@app.route('/')
def index():
    access_token = ""
    token_info = sp_oauth.get_cached_token()

    if token_info:
        return "Found cached token!"
    else:
        url = request.url
        code = sp_oauth.parse_response_code(url)
        if code:
            print("Trying to get valid access token from URL...")
            token_info = sp_oauth.get_access_token(code)
            return "Got new token!"

    return login_button()


def login_button():
    auth_url = getSPOauthURI()
    htmlLoginButton = "<a href='" + auth_url + "'>Login to Spotify</a>"
    return htmlLoginButton


def getSPOauthURI():
    auth_url = sp_oauth.get_authorize_url()
    return auth_url


if __name__ == "__main__":
    app.run()
