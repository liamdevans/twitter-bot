# twitter-bot

## Plan
- Initial plan
  - post to a Twitter account :white_check_mark:
  - scrape some football data (stats, lineups) using https://docs.football-data.org/general/v4/ :white_check_mark:
  - schedule posting to Twitter (using dagster?) on match-days :white_check_mark:
- Further plan
  - create better stats to post (plots/figures) 
  - pre-match post on opposition team
  - make reusable for other teams


## Post a tweet

We can either:
1. Use the `requests` module to make a `POST` request ourselves.  
Which requires a number of OAuth configurations to be created for us to [Authenticate](https://developer.twitter.com/en/docs/authentication/oauth-1-0a/authorizing-a-request).  
See examples of how them [here](https://github.com/anein/twitter-signature-python/blob/master/test/test-generate.py).
```python
import requests
import json
from configs import keys

url = "https://api.twitter.com/2/tweets"

my_tweet = "text to tweet"

payload = json.dumps({
    "text": my_tweet
})
headers = {
    'Authorization': 'OAuth '
                     f'oauth_consumer_key={keys.CONSUMER_API_KEY},'
                     f'oauth_token={keys.ACCESS_TOKEN},'
                     'oauth_signature_method="HMAC-SHA1",'
                     'oauth_timestamp="<timestamp>",'
                     'oauth_nonce="<oauth_nonce>",'
                     'oauth_version="1.0",'
                     'oauth_signature="<oauth_signature>"',
    'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
```
2. Using [tweepy](https://docs.tweepy.org/en/stable/index.html)  
Authenticates to Twitter API v2 using [OAuth 1.0a User Context](https://docs.tweepy.org/en/stable/authentication.html#id3).   
```python
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
```