import tweepy
import sys
import pymongo

# Authentication Credentials
consumer_key = 'CoyP4SgPsFeLOXG65EZ4AWsdX'
consumer_secret = 'e7ZNymAi5J4oPqjHKS1oenrjq3l2QGEGDoNVqQj4DFA7GFvE8x'
access_token = '976553437570756612-us2iAIc0UoPGFBQhLYO0w5mIktwLRaF'
access_token_secret = 'zl3YDfn6fD0Dbpllfd8G2ClfjoMeFNRfwczRj6Sej9H0k'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

class CustomStreamListener(tweepy.StreamListener):
    def __init__(self, api):
        self.api = api
        super(tweepy.StreamListener, self).__init__()

        self.db = pymongo.MongoClient().tradewar

    def on_status(self, status):
        print(status.text , "\n")

        data ={}
        data['text'] = status.text
        data['created_at'] = status.created_at
        data['geo'] = status.geo
        data['source'] = status.source

        self.db.Tweets.insert(data)

    def on_error(self, status_code):
        # print >> sys.stderr, 'Encountered error with status code:', status_code
        print('Encountered error with status code:', status_code, file=sys.stderr)
        return True # Don't kill the stream

    def on_timeout(self):
        # print >> sys.stderr, 'Timeout...'
        print('Timeout...', file=sys.stderr)
        return True # Don't kill the stream

sapi = tweepy.streaming.Stream(auth, CustomStreamListener(api))
sapi.filter(track=['#tradewar'], languages=['en'])
