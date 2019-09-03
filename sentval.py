from flask import Flask, render_template, make_response
import pymongo
import pandas as pd
import json
import io
import base64
import matplotlib.pyplot as plt
import numpy as np
from textblob import TextBlob
import re
from pandas import DataFrame, Series
from sklearn.decomposition import NMF, LatentDirichletAllocation
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from line_graph import clean_tweet, analyze_sentiment
# from line_graph import sent_analysis, clean_tweet, analyze_sentiment
import timeit

client = pymongo.MongoClient('localhost', 27017)
db = client['tradewar']
collection = db['Tweets']

for doc in db.Tweets.find({}, {'_id': 1, 'text': 1}):
    # print(doc['text'])
    val = analyze_sentiment(doc['text'])
    # print(val)
    # print('\n')
    db = client.tradewar.Tweets
    db.update({'_id':doc['_id']}, {'$set': {'sentval': val}}, upsert=False, multi=False)
