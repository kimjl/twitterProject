from flask import Flask, render_template, make_response, jsonify
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
from random import sample
from datetime import datetime
from dateutil.parser import parse

client = pymongo.MongoClient('localhost', 27017)
db = client['tradetest']
collection = db['tweettest']
data = pd.DataFrame(list(collection.find()))

app = Flask(__name__)
#
# #adding in sent value to our db
# for doc in db.tweettest.find({}, {'_id': 1, 'text': 1}):
#     # print(doc['text'])
#     val = analyze_sentiment(doc['text'])
#     # print(val)
#     # print('\n')
#     db = client.tradetest.tweettest
#     db.update({'_id':doc['_id']}, {'$set': {'sentnum': val}}, upsert=False, multi=False)


@app.route("/pd")
def home():
    data = pd.DataFrame(list(collection.find().limit(50)))
    data['SA'] = data['text'].apply(analyze_sentiment)
    return render_template('showdataframe.html',  tables=[data.to_html(classes='data')], titles=data.columns.values)

# db = client.tradetest.tweettest
@app.route("/")
def display():
    #get collection you are interested in
    return render_template('chart.html')
@app.route("/data")
def data():
    #sentvalue
    r = []
    for doc in db.tweettest.find({}, {'_id': 0, 'sentnum': 1}).limit(20):
        for k, v in doc.items():
            r.append(v)
    #dates
    res = []
    for doc in db.tweettest.find({}, {'_id': 0, 'created_at': 1}).limit(20):
        for k, v in doc.items():
            sep = str(v).split(' ')
            d = sep[0]
            dates = d[5:7]
            res.append(dates)
    return jsonify({'results': r})

# @app.route('/dates')
# def dates():
#     res = []
#     for doc in db.tweettest.find({}, {'_id': 0, 'created_at': 1}).limit(20):
#         for k, v in doc.items():
#             sep = str(v).split(' ')
#             d = sep[0]
#             r = d[5:7]
#             res.append(r)
#             # dt = parse(str(v))
#             # res.append(dt)
#     return jsonify({'dates': res})

    # return jsonify({'results': sample(range(1, 10), 5)})

if __name__ == "__main__":
    app.run()
