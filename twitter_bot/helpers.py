"""
A module of helper functions to be used within the `main` module of the `twitter_bot` package.
"""
import datetime
import pytz
import tweepy
from pyfootball.football import Football
from configs import keys

from pathlib import Path


def twitter_auth():
    """
    Authenticate user with Twitter developers account, returning a client from the tweepy package.
    :return: Twitter API v2 Client
    """
    # Authenticate to Twitter
    client = tweepy.Client(
        consumer_key=keys.CONSUMER_API_KEY,
        consumer_secret=keys.CONSUMER_API_KEY_SECRET,
        access_token=keys.ACCESS_TOKEN,
        access_token_secret=keys.ACCESS_TOKEN_SECRET,
    )
    return client


def format_tweet(tweet: str) -> str:
    """
    Given a tweet to be posted and appends the hashtag onto it.
    Args:
        tweet: str: tweet to be posted.

    Returns:
        tweet: str: same tweet with hashtag appended.
    """
    tweet += "\n\n#twitterclarets"
    return tweet


def get_next_fixture(team_id: int):
    """
    Given a team_id, return the date of the next fixture for the corresponding team.
    Args:
        team_id: team ID value according to api.football-data.org.

    Returns:
        Fixture object of next fixture, None if no fixtures available.
    """
    fbl = Football()
    now = datetime.datetime.now()
    fixtures = fbl.get_team_fixtures(team_id)
    fixtures_upcoming = [utc_to_uk_time(fix) for fix in fixtures if fix.date > now]
    try:
        return fixtures_upcoming[0]
    except KeyError:
        print("Dates for future fixtures are not currently available.")
        return None


def utc_to_uk_time(_object: object):
    """Given an object, finds all the attributes with a date type and converts them from
    utc to UK time.

    Args:
        _object: Any pyfootball object (i.e. Fixture, Competition)

    Returns:
        _object: The same object with time attribute converted to UK time.
    """
    date_attributes = [
        key
        for key in _object.__dict__.keys()
        if isinstance(_object.__dict__[key], datetime.datetime)
    ]
    london = pytz.timezone("Europe/London")
    for att in date_attributes:
        setattr(_object, att, london.fromutc(getattr(_object, att)))
    return _object


def make_date_readable(date_obj: datetime.datetime) -> str:
    """
    Given a datetime object, returns it in a more human-readable style.
    Args:
        date_obj: datetime object

    Returns:
        str: human-readable datetime
    """
    day = date_obj.day
    suffix = make_ordinal(day)[-2:]
    return date_obj.strftime(f"%a %-d{suffix} %b at %-I:%M %p")


def get_opposition_team(fixture, team_id):
    """
    Given a Fixture object and team_id, return the Team object that represents the opposition team.
    Args:
        fixture: Fixture object.
        team_id: ID of the team you want the opposition of.

    Returns:
        dictionary of opposition team.
    """
    if fixture.home_team_id == team_id:
        return fixture.away_team
    if fixture.away_team_id == team_id:
        return fixture.home_team
    print(
        f"Team with ID: {team_id} are not participating in "
        f"{fixture.home_team_name}({fixture.home_team_id}) "
        f"vs {fixture.away_team_name}({fixture.away_team_id})"
    )
    return None


def home_or_away(fixture, team_id: int) -> str:
    """
    Given a Fixture object, return whether the team corresponding to team_id are playing at home or away.
    Args:
        fixture: Fixture object.
        team_id: ID of the team you want the location of.

    Returns:
        str: 'at home' or 'away', None if team_id not part of Fixture.
    """
    if fixture.home_team_id == team_id:
        return "at home"
    if fixture.away_team_id == team_id:
        return "away"
    print(
        f"Team with ID: {team_id} are not participating in "
        f"{fixture.home_team_name}({fixture.home_team_id}) "
        f"vs {fixture.away_team_name}({fixture.away_team_id})"
    )
    return None


def write_latest_fixture_date(fixture_date: datetime.datetime):
    path = Path().cwd() / "latest_fixture.txt"
    date = datetime.datetime.strftime(fixture_date, format="%d-%m-%y")
    with open(path, mode="w", encoding="utf-8") as file:
        file.write(date)


def get_latest_fixture_date():
    pass


def make_ordinal(n):
    """
    Convert an integer into its ordinal representation::

        make_ordinal(0)   => '0th'
        make_ordinal(3)   => '3rd'
        make_ordinal(122) => '122nd'
        make_ordinal(213) => '213th'
    """
    n = int(n)
    if 11 <= (n % 100) <= 13:
        suffix = "th"
    else:
        suffix = ["th", "st", "nd", "rd", "th"][min(n % 10, 4)]
    return str(n) + suffix


def is_tweet_too_long(tweet: str):
    return len(tweet) > 280


def delete_tweet(tweet_id):
    """
    Given a tweet_id, delete the corresponding tweet on the account we authenticate to.
    Args:
        tweet_id: ID of the tweet
    """
    client = twitter_auth()
    client.delete_tweet(tweet_id)
