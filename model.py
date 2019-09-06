import gensim
import keras
import pandas as pd
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from keras.layers import Dense, Dropout, Flatten
from langdetect import detect
from nltk.stem import WordNetLemmatizer, SnowballStemmer
from nltk.stem.porter import *
from sklearn.preprocessing import MinMaxScaler

from config import NUM_TOPICS, LDA, LDA_DICT, MODEL
from utils import load


def lemmatize_stemming(text):
    stemmer = SnowballStemmer("english")
    return stemmer.stem(WordNetLemmatizer().lemmatize(text, pos='v'))


def preprocess_lyrics(text):
    result = []
    text = re.sub('\[.*\]', '', text)
    for token in gensim.utils.simple_preprocess(text):
        if token not in gensim.parsing.preprocessing.STOPWORDS and len(token) > 3:
            result.append(lemmatize_stemming(token))
    return result


def lang_detect(text):
    if text != "NA" and text:
        try:
            text = detect(text)
            return text
        except Exception:
            return "N/A"


def get_topic_dist(song, lda_model, dictionary, num_topics):
    topic_dist = [0] * num_topics
    bow_vector = dictionary.doc2bow(song)
    for index, score in sorted(lda_model[bow_vector], key=lambda tup: -1 * tup[1]):
        topic_dist[index] = score
    return topic_dist


class Model:

    def __init__(self, df):
        self.df = df

    def preprocess(self):
        df = self.df.copy()

        # Get language of lyrics
        df['language'] = df['lyrics'].apply(lang_detect)

        # Filter by only lyrics that are english
        df = df[(df['lyrics'] != "NA") & (df['language'] == "en")]
        print("Detected langauge...")

        # Preprocess lyrics, create new field.
        df['processed_lyrics'] = df['lyrics'].apply(preprocess_lyrics)
        print("Processed lyrics...")

        lda_model, dictionary = load(LDA), load(LDA_DICT)
        topic_headers = ['topic%s' % i for i in range(NUM_TOPICS)]
        topic_columns = df['processed_lyrics'].apply(
            get_topic_dist, args=(lda_model, dictionary, NUM_TOPICS,))
        df[topic_headers] = pd.DataFrame(topic_columns.values.tolist(), index=df.index)
        print("Generated topic distributions...")
        df.drop(['lyrics', 'language', 'processed_lyrics'], axis=1, inplace=True)

        scaler = MinMaxScaler()
        features = list(set(df.columns.tolist()) - {'id'})
        df[features] = scaler.fit_transform(df[features])
        print("Normalized...")
        self.df = df

    def predict(self):
        model = keras.Sequential([
            Dense(20, activation='relu', input_dim=20),
            Dropout(0.4),
            Dense(20, activation='relu'),
            Dropout(0.4),
            Dense(10, activation='relu'),
            Dropout(0.4),
            Dense(1, activation='sigmoid'),
        ])
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=[])
        model.load_weights(MODEL)
        predictions = [x[0] for x in model.predict_proba(self.df.drop('id', axis=1))]
        self.df['score'] = pd.Series(predictions, index=self.df.index)
        self.df = self.df.sort_values('score')

    def run(self):
        self.preprocess()
        self.predict()
