import datetime

from twitter_bot.helpers import format_tweet, make_date_readable
import pytest

dummy_tweet_data = [
    ("First tweet", "First tweet\n\n#twitterclarets"),
    ("", "\n\n#twitterclarets"),
]


dummy_date_data = [
    (
        datetime.datetime.strptime("2022-01-01 20:00", "%Y-%m-%d %H:%M"),
        "Sat 1st Jan at 8:00 PM",
    ),
    (
        datetime.datetime.strptime("2022-01-02 08:00", "%Y-%m-%d %H:%M"),
        "Sun 2nd Jan at 8:00 AM",
    ),
    (
        datetime.datetime.strptime("2022-01-03 12:00", "%Y-%m-%d %H:%M"),
        "Mon 3rd Jan at 12:00 PM",
    ),
    (
        datetime.datetime.strptime("2022-01-04 00:00", "%Y-%m-%d %H:%M"),
        "Tue 4th Jan at 12:00 AM",
    ),
]


@pytest.mark.parametrize(
    "tweet, expected", dummy_tweet_data, ids=["Standard Tweet", "Tweet with no text"]
)
def test_format_tweet(tweet, expected):
    assert format_tweet(tweet) == expected


@pytest.mark.parametrize("datetime_object, expected", dummy_date_data)
def test_make_date_readable(datetime_object, expected):
    assert make_date_readable(datetime_object) == expected
