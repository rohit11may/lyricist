---
title: Lyrics-based Playlist Generation
layout: index
---
Quite often I'd find myself listening to new music and not enjoying the melody too much, but then it 
just takes one or two lyrics to change my opinion about the whole song. After two years of using
Spotify exclusively and frequently, its weekly recommendation playlists on Mondays 
(_Discover Weekly_) began to become really good; gifting me 4-5 songs each week. It caught on to 
the vibe of the music I liked and also kept up with how my taste evolved.

However, I wondered whether Spotify's recommendation engine actually factored in lyrical content 
of the songs I liked, or whether it was possible that my 'taste' in lyrics even had detectable 
patterns. This was pretty much impossible to infer from the Discover Weekly playlist directly, nor
was there much help online, so I decided to investigate myself.

### Problem Statement
At the time I started, I had around **1000 songs** that were 'liked' in my library, giving me a good
sample to represent my taste in music. As the earliest songs were saved since early 2017, this
was a relatively recent and dense representation. If there exists a pattern/taste in the lyrics of
these songs then I should be able to classify new songs as _like_ or _dislike_. Thus I arrived at 
this question. 

> **Is it possible to predict whether I like a song based *purely* on its lyrics?**

### Approach

To prove my hypothesis I needed to:

1. Have samples of *songs I like* and *songs I don't like*. 
2. Extract lyrical features for all songs.
3. Scatter plot lyrical features.

If the liked songs **clustered** in the space of all songs, it would imply that there were 
similarities in their lyrics compared to the rest and therefore it would be possible to predict
whether I liked one based on it's lyrics!

# Creating a Dataset

Of the various lyric sources available, I decided to use the 
[Genius API](https://docs.genius.com/) due to its size, and obviously the [Spotify
API](https://developer.spotify.com/) for all other track information.

### Collecting Track Details
Getting a sample of liked songs was to simply pluck the **Liked Songs** from my Spotify library.
Collecting disliked songs is more difficult. I had to make sure that the sample:
  - Included songs of all genres to eliminate bias
  - Were mostly, if not all, songs I _actually disliked_.

Since there was definitely no existing list of these songs I had access to, I took a probabilistic
approach. From the list of all possible genres, I sampled 5 at a time. Then, I passed that list as
the seed to generate a **Spotify Radio** (50 tracks), limiting the '_instrumentalness_' of the songs 
in the radio to a value which filters out lyricless songs.  

```python
import Spotipy as sp 
# Setup Spotipy...  

genre_seeds = sp.recommendation_genre_seeds()
all_tracks = {}
target_total = 15000

# Scrape songs as long as target total is not reached
while len(all_items.keys()) <= target_total:
  recc = sp.recommendations(
      seed_genres = random.sample(genre_list, 5),
      max_instrumentalness = 0.35,
      limit=50
  )
  for item in recc['tracks']:
    all_items[item['id']] = item
```

Thus, I scraped **15000** track details from Spotify, equally representing all the genres. I made
the assumption that I disliked the large majority of these songs based on the fact that I am much 
more likely to dislike any given song than to like it.

### Scraping Lyrics
For each song, I requested the lyrics by _song title_ and _song name_.
```python
import requests
def request_song_info(song_title, artist_name):
  base_url = 'https://api.genius.com'
  headers = {'Authorization': 'Bearer ' + token}
  search_url = base_url + '/search'
  data = {'q': song_title + ' ' + artist_name}
  response = requests.get(search_url, data=data, headers=headers)
  return response
```

However, this only gave me a link to the page containing the lyrics. I still had to scrape them! If
the lyrics were not available, I returned `'NA'`.
```python
import beautifulsoup
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
      name = hit['result']['primary_artist']['name']
      if artist_name.lower() in name.lower():
        remote_song_info = hit
        break
    
    # Extract lyrics from URL if the song was found
    if remote_song_info:
      song_url = remote_song_info['result']['url']
      return scrape_song_url(song_url)
  
  return "NA"
```

At this point, we have enough data to complete the hypothesis.

# Lyrical Analysis
Love, break-ups and nostalgia were just some of the themes prevalent in the lyrics of my saved
songs, from my own observations. I figured that songs discussing themes I was interested in would be
pretty good predictions!

After some research, I stumbled across [Latent Dirichlet Allocation](
https://towardsdatascience.com/light-on-math-machine-learning-intuitive-guide-to-latent-dirichlet-allocation-437c81220158),
explained very intuitively in the linked Medium article. It essentially extracts a defined number of
_topics_ from a set of documents (songs in this case). A _topic_ is a probability distribution of
the words in the _vocabulary_ used by the songs. Finally, each song is given a _topic distribution_
based on its words and which topic they fall under. In this way, I could model the overall theme of
a song.

Before I could apply LDA, the lyric data needed some pre-processing. 

### Language Filter
Of the 15000 songs scraped, lyrics were only available for 82% of them. The nature of the problem,
however, limits the possible languages to only ones I know i.e. English. To filter lyrics by
language, [langdetect](https://pypi.org/project/langdetect/) did the job perfectly.

```python
from langdetect import detect
def lang_detect(text):
  if text != "NA" and text:
    try:
      text = detect(text)
      return text
    except Exception:
      return "NA"
```
Applying that function to all the songs left only ~7200 english songs.

### Lemmatization / Stopwords
Using [gensim](https://radimrehurek.com/gensim/), I tokenized the lyrics (after removing the Genius
verse tags). Next I removed the stopwords such as _'also', 'have', 'does', 'has', 'had', 'when'_, 
etc. Finally, to avoid lyrics like _'love'_ and _'loving'_ having different meanings, I lemmatized
the lyrics to reduce every word to its root form.

```python
import gensim
stemmer = SnowballStemmer("english")

def lemmatize_stemming(text):
  return stemmer.stem(WordNetLemmatizer().lemmatize(text, pos='v'))

def preprocess(text):
  result = []
  text = re.sub('\[.*\]', '', text)
  for token in gensim.utils.simple_preprocess(text):
    if token not in gensim.parsing.preprocessing.STOPWORDS and len(token) > 3:
        result.append(lemmatize_stemming(token))
  return result
```

### Topic Modeling with LDA
Having converted the lyrics string into a list of useful tokens, we can now apply LDA. First, using
gensim, I create a dictionary of all the unique words from all downloaded lyrics and remove all
words that occur in less than 20 songs and more than 20% of the songs. This leaves around 2000
words which form the useful part of the vocabulary; ready for topic modeling. 

```python
import gensim
all_processed_lyrics = df['processed_lyrics'].tolist()
dictionary = gensim.corpora.Dictionary(all_processed_lyrics)
dictionary.filter_extremes(no_below=20, no_above=0.2)
bow_corpus = [dictionary.doc2bow(lyric) for lyric in all_processed_lyrics]
lda_model =  gensim.models.LdaMulticore(bow_corpus, 
                                  num_topics = 10, 
                                  id2word = dictionary,                                    
                                  passes = 15,
                                  workers = 3)
```

At this point we can take a sneak peak of the topics it found!

**nostalgia** | come, burn, time, go, young, hous, live, say, want <br>
**love** | feel, come, love, heart, think, know, good, eye, break, fall <br>
**desire** | want, babi, know, wanna, girl, yeah, like, caus, leav, need <br>
**party** | gonna, night, danc, home, song, rock, parti, drink, everybodi, tonight <br>
**night life** | sing, light, kill, boom, look, like, blue, life, rain, littl <br>
**break-up** | like, world, watch, heart, break, breath, leav, cold, fall, live <br>
**lust** | love, babi, come, right, girl, shake, need, bring, know <br>
**explicit** | yeah, like, fuck, bitch, shit, n\*\*\*a, know, money, caus, gotta <br>
**more love?** | yeah, love, know, like, tell, thing, wish, need, life, think <br>
**recovery** | know, time, caus, mind, away, need, lose, like, wait, hold

I named the topics based on the top ten most probable words for each topic.

### Generate the topic distributions
Finally, using the LDA model, I generate a distribution of the 10 topics present in the song, for
each song.
```python
def get_topic_dist(song, lda_model, dictionary, num_topics):
  topic_dist = [0]*num_topics
  bow_vector = dictionary.doc2bow(song)
  topic_scores = sorted(lda_model[bow_vector], 
                        key=lambda tup: -1*tup[1])
  for index, score in topic_scores:
    topic_dist[index] = score
  return topic_dist
```

