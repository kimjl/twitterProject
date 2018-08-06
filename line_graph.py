import pymongo
import json
from textblob import TextBlob
import re
from pandas import DataFrame, Series
import numpy as np
import pandas as pd

client = pymongo.MongoClient('localhost', 27017)
db = client['tradewar']
collection = db['Tweets']
data = pd.DataFrame(list(collection.find()))

# Clean our tweets and perform sentiment analysis
def clean_tweet(tweet):

    # Clean the text in a tweet by removing links and special characters using regex.

    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

def analyze_sentiment(tweet):

    # Classify the polarity of a tweet using textblob.

    analysis = TextBlob(clean_tweet(tweet))
    if analysis.sentiment.polarity > 0:
        return 1
    elif analysis.sentiment.polarity == 0:
        return 0
    else:
        return -1

def sent_analysis():
    data['SA'] = np.array([ analyze_sentiment(tweet) for tweet in data['text'] ])

    pos_tweets = [ tweet for index, tweet in enumerate(data['text']) if data['SA'][index] > 0]
    neu_tweets = [ tweet for index, tweet in enumerate(data['text']) if data['SA'][index] == 0]
    neg_tweets = [ tweet for index, tweet in enumerate(data['text']) if data['SA'][index] < 0]

    pos = len(pos_tweets)* 100/ len(data['text'])
    neu = len(neu_tweets)* 100/ len(data['text'])
    neg = len(neg_tweets)* 100/ len(data['text'])

    return pos, neu, neg
