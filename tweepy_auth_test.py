import tweepy
from configs import keys

my_tweet = "Final test today"

# Authenticate to Twitter
client = tweepy.Client(
    consumer_key=keys.CONSUMER_API_KEY,
    consumer_secret=keys.CONSUMER_API_KEY_SECRET,
    access_token=keys.ACCESS_TOKEN,
    access_token_secret=keys.ACCESS_TOKEN_SECRET
)
client.create_tweet(text=my_tweet)
