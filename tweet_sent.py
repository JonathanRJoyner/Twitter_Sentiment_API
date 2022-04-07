from flair.models import TextClassifier
from flair.data import Sentence
#import torch, flair
import tweepy
#from dotenv import load_dotenv, find_dotenv
import json
import os

#load_dotenv(find_dotenv())

API_KEY = os.environ.get("API_KEY")
API_SECRET = os.environ.get("API_SECRET")
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
ACCESS_SECRET = os.environ.get('ACCESS_SECRET')

#flair.device = torch.device("cpu")

auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

api = tweepy.API(auth, wait_on_rate_limit=True)

def lambda_handler(event, context):
    params = event['queryStringParameters']
    
    if 'q' in params:
        output = tweets(params['q'])
        
        return {
            'statusCode': 200,
            'body': json.dumps(output)            
        }
    
    else:
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid Query')
        }

def flair_sentiment(tweets, classifier):
    classifier = TextClassifier.load(classifier)
    sentences = [Sentence(tweet) for tweet in tweets]
    classifier.predict(sentences, mini_batch_size=32)

    return[
        (sent.labels[0].value, sent.labels[0].score) for sent in sentences
    ]

def tweets(query, lang = 'en', result_type = 'mixed', count = 10, filter_retweets = True):
    if filter_retweets == True:
        suf = ' -filter:retweets'
    else:
        suf = ''
    
    tweets_data = api.search_tweets(
        q=f'{query}{suf}',
        lang = lang,
        result_type = result_type,
        tweet_mode = 'extended',
        count = count
    )

    tweet_text = [status.full_text for status in tweets_data]
    tweet_id = [status.id for status in tweets_data]
    tweet_sent = flair_sentiment(tweet_text, 'sentiment')

    tweets = []
    
    for id, text, sent in zip(tweet_id, tweet_text, tweet_sent):
        tweet_data = {
            'ID': id,
            'Score': sent[1] ,
            'Sentiment': sent[0],
            'Text': text
        }
        tweets.append(tweet_data)


    average = average_sent(tweet_sent)

    data = {
        'Average': average,
        'Tweets': tweets
    }

    return data

def average_sent(tweet_sent):
    sent = [-sent[1] if sent[0] == 'NEGATIVE' else sent[1] for sent in tweet_sent]
    return sum(sent)/len(sent)