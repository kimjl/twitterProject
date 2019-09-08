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
df = pd.DataFrame({'date':data['created_at'].dt.date.unique()})

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
    data = data.drop('sentanalysis', axis=1)
    data = data.drop('sentnum', axis=1)
    data = data.drop('sentval', axis=1)
    data['SA'] = data['text'].apply(analyze_sentiment)
    return render_template('showdataframe.html',  tables=[data.to_html(classes='data')], titles=data.columns.values)

@app.route('/display')
def displayline():
    data = pd.DataFrame(list(collection.find()))
    data['SA'] = data['text'].apply(analyze_sentiment)
    #Set up our data to display as a line using matplotlib
    img = io.BytesIO()
    fig, ax = plt.subplots()
    data.groupby('created_at')['SA'].sum().plot(kind='line')
    # y_axis = data['created_at'].dt.date.value_counts()
    #
    # #Creating parameters for our line plot and labeling x and y axis
    # ax.tick_params(axis='x', labelsize=10)
    # ax.tick_params(axis='y', labelsize=10)
    # ax.set_xlabel('Dates', fontsize=15)
    # ax.set_ylabel('Number of tweets' , fontsize=15)
    # ax.set_title('Number of Tweets Per Day with #tradewar', fontsize=15, fontweight='bold')
    #
    # y_axis.plot(ax=ax, kind='line', color='red')
    # plt.setp(ax.get_xticklabels(), fontsize=8, family='sans-serif', rotation=45)
    # plt.setp(ax.get_yticklabels(), fontsize=10, family='sans-serif')

    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    # return '<img src="data:image/png;base64,{}">'.format(plot_url)
    return render_template('displayline.html', plot_url=plot_url)

# db = client.tradetest.tweettest
@app.route("/")
def display():
    #get collection you are interested in
    return render_template('chart.html')

@app.route("/data")
def data():
    #sentvalue
    results = []
    for doc in db.tweettest.find({}, {'_id': 0, 'sentnum': 1}).limit(50):
        for k, v in doc.items():
            results.append(v)
    #dates
    months = []
    for doc in db.tweettest.find({}, {'_id': 0, 'created_at': 1}).limit(50):
        for k, v in doc.items():
            sep = str(v).split(' ')
            d = sep[0]
            dates = d[5:7]
            months.append(int(dates))

    # sentnum = []
    # result = db.tweettest.find({}, {'_id': 0, 'sentnum': 1, 'created_at': 1}).limit(20)
    # for res in result:
    #     sentnum.append(res)

    return jsonify({'results': results}, {'months': months})

    #
    # return jsonify({'results': results})

if __name__ == "__main__":
    app.run()
