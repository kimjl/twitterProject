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
import seaborn as sns

app = Flask(__name__)

client = pymongo.MongoClient('ds233769.mlab.com', 33769)
db = client['tradewar']
collection = db['Tweets']
db.authenticate('james', 'tradewar123')

# client = pymongo.MongoClient('localhost', 27017)
# db = client['tradewar']
# collection = db['Tweets']
data = pd.DataFrame(list(collection.find()))
df = pd.DataFrame({'date': data['created_at'].dt.date.unique()})
# data['SA'] = data['text'].apply(analyze_sentiment)

# Set up our routes and render our html
@app.route('/')
def homepage():

    return render_template('index.html')


@app.route('/about')
def about():

    return render_template('about.html')


@app.route('/home')
def home():

    return render_template('home.html')


@app.route('/contact')
def contact():

    return render_template('contact.html')


@app.route('/tradewar')
def tradewar():

    return render_template('tradewar.html')


@app.route('/pd')
def displaydf():

    data = pd.DataFrame(list(collection.find(100)))
    dates = data['created_at'].dt.date.value_counts(
    ).sort_index(axis=0).to_frame()
    return render_template('showdataframe.html',  tables=[data.to_html(classes='data')], titles=data.columns.values)


@app.route('/displayline')
def displayLineData():

    sns.set_style("whitegrid")
    img = io.BytesIO()

    dates = data['created_at'].dt.date.value_counts(
    ).sort_index(axis=0).iloc[:99]
    datess = data['created_at'].dt.date.value_counts(
    ).sort_index(axis=0).iloc[100:]

    fig, ax = plt.subplots()
    ax.patch.set_facecolor('#e3f2fd')
    ax.tick_params(axis='x', labelsize=10)
    ax.tick_params(axis='y', labelsize=10)
    ax.set_xlabel('Date', fontsize=15)
    ax.set_ylabel('Number of tweets', fontsize=15)
    ax.set_title('Number of Tweets Per Month with #tradewar',
                 fontsize=15, fontweight='bold')

    fig.autofmt_xdate()
    plt.gcf().subplots_adjust(bottom=0.25)
    dates.plot(ax=ax, kind='line', color='red')
    datess.plot(ax=ax, kind='line', color='red')
    plt.setp(ax.get_xticklabels(), fontsize=10,
             family='sans-serif', rotation=45)

    plt.savefig(img, format='png', facecolor=ax.get_facecolor(), edgecolor='none')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    return render_template('displayline.html', plot_url=plot_url)


@app.route('/displayfill')
def displayLineFill():

    sns.set_style("whitegrid")
    img = io.BytesIO()

    uniques = data.drop_duplicates('text')
    organics = uniques[uniques['text'].str.startswith('RT') == False]
    organics = organics[organics['text'].str.startswith('rt') == False]
    organics = organics[organics['text'].str.contains(
        ' RT ', case=False) == False]
    organic_sources = ['Twitter for iPhone', 'Twitter Web Client',
                       'Facebook', 'Twitter for Android', 'Instagram']
    organics = organics[organics['source'].isin(organic_sources)]
    organics['created_at'] = [
        tweetTime for tweetTime in organics['created_at']]
    organics['created_at'] = pd.to_datetime(Series(organics['created_at']))
    organics = organics.set_index('created_at', drop=False)
    organics.index = organics.index.tz_localize('UTC').tz_convert('EST')
    ts_hist = organics['created_at'].resample('W').count()

    plt.style.use
    x_date = ts_hist.index
    zero_line = np.zeros(len(x_date))

    fig, ax = plt.subplots()
    ax.patch.set_facecolor('#e3f2fd')
    ax.fill_between(x_date, zero_line, ts_hist.values,
                    facecolor='red', alpha=0.5)
    ax.set_title('Number of Tweets Per Month with #tradewar',
                 fontsize=15, fontweight='bold')

    plt.xlabel('Date', fontsize=16)
    plt.ylabel('Number of Tweets', fontsize=16)
    fig.autofmt_xdate()
    plt.savefig(img, format='png', facecolor=ax.get_facecolor(), edgecolor='none')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    return render_template('displayfill.html', plot_url=plot_url)


@app.route('/sentanalysis')
def sentAnalysisDisplay():

    n = data.shape[0]
    pos_frac = str(round((data['sentval'] > 0).sum() * 100 / n, 1))+'%'
    neu_frac = str(round((data['sentval'] == 0).sum() * 100 / n, 1))+'%'
    neg_frac = str(round((data['sentval'] < 0).sum() * 100 / n,  1))+'%'

    sns.set_style("whitegrid")
    img = io.BytesIO()
    fig, ax = plt.subplots()
    ax.patch.set_facecolor('#e3f2fd')
    data.groupby('created_at')['sentval'].sum().iloc[:99].plot(
        ax=ax, kind='line', color='red')
    data.groupby('created_at')['sentval'].sum().iloc[100:].plot(
        ax=ax, kind='line', color='red')

    plt.xlabel('Date', fontsize=16)
    plt.ylabel('Sentiment Value Sum', fontsize=16)
    ax.set_title('Sentiment Value Per Month', fontsize=15, fontweight='bold')
    fig.autofmt_xdate()

    plt.savefig(img, format='png', facecolor=ax.get_facecolor(), edgecolor='none')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    return render_template('sentanalysis.html', plot_url=plot_url, pos=pos_frac, neu=neu_frac, neg=neg_frac)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
