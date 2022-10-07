"""
A module of helper functions to be used within the `main` module of the `twitter_bot` package.
"""
import datetime
import csv
from pathlib import Path
import pytz
import requests.exceptions
import tweepy

from pyfootball.football import Football
from configs import keys


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


def delete_tweet(tweet_id):
    """
    Given a tweet_id, delete the corresponding tweet on the account we authenticate to.
    Args:
        tweet_id: ID of the tweet
    """
    client = twitter_auth()
    client.delete_tweet(tweet_id)


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
    Given a datetime object, returns it in a more human readable style.
    Args:
        date_obj: datetime object

    Returns:
        str: human readable datetime
    """
    day = date_obj.day
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]
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


def get_comp_ids() -> list(dict):
    """
    Function to get all the competitions available from the football-data.org API.
    Returns:
        competition_ids and competition_names
    """
    fbl = Football()
    comps = fbl.get_all_competitions()
    return [{"comp_id": comp.id, "comp_name": comp.name} for comp in comps]


def write_comp_ids():
    """
    Function to create a csv containing all the competition IDs and names for those available
    in the football-data.org API
    """
    path = Path.cwd().parent / "data" / "comp_ids.csv"
    with open(path, mode="w", encoding="utf-8") as csv_file:
        fieldnames = ["comp_id", "comp_name"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in get_comp_ids():
            writer.writerow(row)


def get_comp_team_ids(comp_id) -> list(dict):
    """
    Given a comp_id, returns all the teams involved from the football-data.org API.
    Returns:
        team_ids and team_names
    """
    fbl = Football()
    teams = fbl.get_competition_teams(comp_id)
    return [{"team_id": team.id, "team_name": team.name} for team in teams]


def write_comp_team_ids(comp_id):
    """
    Given a comp_id, creates a csv containing all the team IDs and names involved
    for those available in the football-data.org API
    """
    path = Path.cwd().parent / "data" / f"team_ids_{comp_id}.csv"
    try:
        with open(path, mode="w", encoding="utf-8") as csv_file:
            fieldnames = ["team_id", "team_name"]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for row in get_comp_team_ids(comp_id):
                writer.writerow(row)
    except requests.exceptions.HTTPError:
        print(f"Competition ID {comp_id} not found.")
        path.unlink()


if __name__ == "__main__":
    print("running helpers.py")
    # print(write_comp_ids())
    # print(get_comp_ids())
    # write_comp_ids()
    # print(get_comp_team_ids(2016))
    # write_comp_team_ids(2016002020)
    # print(f"The next fixture is: {get_next_fixture(328)}")
