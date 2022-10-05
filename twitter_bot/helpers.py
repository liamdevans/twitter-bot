import datetime

import pytz
import requests.exceptions
import tweepy
import csv
from pathlib import Path
from configs import keys
from pyfootball.football import Football


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
    f = Football()
    now = datetime.datetime.now()
    fixtures = f.get_team_fixtures(team_id)
    fixtures_upcoming = [utc_to_uk_time(f) for f in fixtures if f.date > now]
    try:
        return fixtures_upcoming[0]
    except KeyError:
        print("Dates for future fixtures are not currently available.")
        return


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
        if type(_object.__dict__[key]) == datetime.datetime
    ]
    london = pytz.timezone("Europe/London")
    for att in date_attributes:
        _object.__setattr__(att, london.fromutc(_object.__getattribute__(att)))
    return _object


def make_date_readable(d: datetime.datetime) -> str:
    """
    Given a datetime object, returns it in a more human readable style.
    Args:
        d: datetime object

    Returns:
        str: human readble datetime
    """
    day = d.day
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]
    return d.strftime(f"%a %-d{suffix} %b at %H:%M %p")


def get_opposition_team(fixture, team_id):  # TODO add type hinting for Fixture objects
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
    elif fixture.away_team_id == team_id:
        return fixture.home_team
    else:
        print(
            f"Team with ID: {team_id} are not participating in "
            f"{fixture.home_team_name}({fixture.home_team_id}) "
            f"vs {fixture.away_team_name}({fixture.away_team_id})"
        )


def get_comp_ids():
    f = Football()
    comps = f.get_all_competitions()
    return [{"comp_id": comp.id, "comp_name": comp.name} for comp in comps]


# TODO turn data writers into dagster assets
def write_comp_ids():
    path = Path.cwd().parent / "data" / "comp_ids.csv"
    with open(path, mode="w") as csv_file:
        fieldnames = ["comp_id", "comp_name"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in get_comp_ids():
            writer.writerow(row)
    return


def get_comp_team_ids(comp_id):
    f = Football()
    teams = f.get_competition_teams(comp_id)
    return [{"team_id": team.id, "team_name": team.name} for team in teams]


def write_comp_team_ids(comp_id):
    path = Path.cwd().parent / "data" / f"team_ids_{comp_id}.csv"
    try:
        with open(path, mode="w") as csv_file:
            fieldnames = ["team_id", "team_name"]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for row in get_comp_team_ids(comp_id):
                writer.writerow(row)
    except requests.exceptions.HTTPError:
        print(f"Competition ID {comp_id} not found.")
        path.unlink()
    return


if __name__ == "__main__":
    print("running helpers.py")
    # print(write_comp_ids())
    # print(get_comp_ids())
    # write_comp_ids()
    # print(get_comp_team_ids(2016))
    # write_comp_team_ids(2016002020)
    # print(f"The next fixture is: {get_next_fixture(328)}")
