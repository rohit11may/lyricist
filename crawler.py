import json
import numpy as np
import pandas as pd
import random
import requests
from SpotifyClient import SpotifyClient

from bs4 import BeautifulSoup
from flask import Flask, request
from utils import save, load
from collections import Counter
from itertools import chain
from time import sleep
from langdetect import detect
from tqdm import trange

sp = SpotifyClient()


def start(token):
    sp.authenticate(token)
    print(sp.recommendation_genre_seeds())



