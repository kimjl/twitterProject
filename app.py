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
from line_graph import sent_analysis, clean_tweet, analyze_sentiment

app = Flask(__name__)

client = pymongo.MongoClient('localhost', 27017)
db = client['tradewar']
collection = db['Tweets']
data = pd.DataFrame(list(collection.find()))

#Set up our routes and render our html
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

#
@app.route('/displayline')
def displayLineData():
    #Set up our data to display as a line using matplotlib
    img = io.BytesIO()
    data = pd.DataFrame(list(collection.find()))
    df = pd.DataFrame({'date':data['created_at'].dt.date.unique()})
    y_axis = data['created_at'].dt.date.value_counts()

    #Creating parameters for our line plot
    fig, ax = plt.subplots()
    ax.tick_params(axis='x', labelsize=8)
    ax.tick_params(axis='y', labelsize=10)
    ax.set_xlabel('Dates', fontsize=15)
    ax.set_ylabel('Number of tweets' , fontsize=15)
    ax.set_title('Number of Tweets Per Day with #tradewar', fontsize=15, fontweight='bold')

    y_axis.plot(ax=ax, kind='line', color='red')

    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    return '<img src="data:image/png;base64,{}">'.format(plot_url)

@app.route('/displayfill')
def displayLineFill():
    #Set up our data to display as a line using matplotlib
    img = io.BytesIO()
    data = pd.DataFrame(list(collection.find()))
    df = pd.DataFrame({'date':data['created_at'].dt.date.unique()})

    #Creating parameters to display data as line
    uniques = data.drop_duplicates('text')
    organics = uniques[uniques['text'].str.startswith('RT')==False]
    organics = organics[organics['text'].str.startswith('rt')==False]
    organics = organics[ organics['text'].str.contains(' RT ', case=False)==False ]
    organic_sources = ['Twitter for iPhone', 'Twitter Web Client',
                    'Facebook', 'Twitter for Android', 'Instagram']
    organics = organics[organics['source'].isin(organic_sources)]
    organics['created_at'] = [tweetTime for tweetTime in organics['created_at']]
    organics['created_at'] = pd.to_datetime(Series(organics['created_at']))
    organics = organics.set_index('created_at',drop=False)
    organics.index = organics.index.tz_localize('UTC').tz_convert('EST')

    ts_hist = organics['created_at'].resample('60t').count()
    # Visualization of our tweets over a period of time
    plt.style.use
    x_date = ts_hist.index
    zero_line = np.zeros(len(x_date))

    fig, ax = plt.subplots()
    ax.fill_between(x_date, zero_line, ts_hist.values, facecolor='blue', alpha=0.5)
    # Format plot
    plt.setp(ax.get_xticklabels(),fontsize=8,family='sans-serif')
    plt.setp(ax.get_yticklabels(),fontsize=15,family='sans-serif')
    plt.xlabel('Date',fontsize=25)
    plt.ylabel('Counts',fontsize=25)

    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    return '<img src="data:image/png;base64,{}">'.format(plot_url)


@app.route('/sentanalysis')
def sentAnalysisDisplay():
    #fix naming convention
    pos = sent_analysis()[0]
    neu = sent_analysis()[1]
    neg = sent_analysis()[2]

    #call once instead of 3 times
    #positive, neutral, negative = sent_analysis()

    return render_template('sentanalysis.html', pos=pos, neu=neu, neg=neg)



def displayTopics(model, feature_names, no_top_words):
    for topic_idx, topic in enumerate(model.components_):
        print("Topic %d:" % (topic_idx))
        print(" ".join([feature_names[i]
                        for i in topic.argsort()[:-no_top_words - 1:-1]]))

@app.route('/displaytopics')
def displayLDA():
    tweets = data.text
    no_features = 1000
    no_topics = 10
    no_top_words = 10
    tf_vectorizer = CountVectorizer(max_df=0.95, min_df=2, max_features=no_features, stop_words='english')
    tf = tf_vectorizer.fit_transform(tweets)
    tf_feature_names = tf_vectorizer.get_feature_names()
    lda = LatentDirichletAllocation(n_topics=no_topics, max_iter=5, learning_method='online', learning_offset=50.,
                                random_state=0).fit(tf)
    topics = display_topics(lda, tf_feature_names, no_top_words)

    return render_template('displaytopics.html', topics=topics)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
