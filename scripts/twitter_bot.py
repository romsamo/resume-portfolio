
import tweepy
import json


# Load Twitter API credentials from config/twitter_config.json
with open('/Users/romano/Desktop/twitterBot/config/twitter_config.json') as config_file:
    config = json.load(config_file)

API_KEY = config['API_KEY']
API_SECRET = config['API_SECRET']
ACCESS_TOKEN = config['ACCESS_TOKEN']
ACCESS_SECRET = config['ACCESS_SECRET']

# Set up tweepy
client = tweepy.Client(bearer_token=None,
                       consumer_key=API_KEY,
                       consumer_secret=API_SECRET,
                       access_token=ACCESS_TOKEN,
                       access_token_secret=ACCESS_SECRET)

def post_tweet(content):
    try:
        response = client.create_tweet(text=content)
        print(f"Tweet posted successfully: {response}")
    except tweepy.TweepyException as e:
        print(f"Error occurred: {e}")



