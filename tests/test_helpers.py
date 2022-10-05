from twitter_bot.helpers import format_tweet
import pytest

tweet_data = [
    ("First tweet", "First tweet\n\n#twitterclarets"),
    ("", "\n\n#twitterclarets"),
]


@pytest.mark.parametrize(
    "tweet, expected", tweet_data, ids=["Standard Tweet", "Tweet with no text"]
)
def test_format_tweet(tweet, expected):
    assert format_tweet(tweet) == expected
