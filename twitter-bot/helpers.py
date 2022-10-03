import datetime
import os
import sys
import traceback

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
        access_token_secret=keys.ACCESS_TOKEN_SECRET
    )
    return client


def delete_tweet(tweet_id):
    client = twitter_auth()
    client.delete_tweet(tweet_id)


def format_tweet(my_func):
    def modify_func(*args, **kwargs):
        result = my_func(*args, **kwargs)
        result += "\n\n#twitterclarets"
        return result  # returns result of original function
    return modify_func


def get_next_fixture(team_id: int):
    """
    Given a team_id, return the date of the next fixture for the corresponding team.
    Args:
        team_id: team ID value according to api.football-data.org.

    Returns:
        Fixture object of next fixture, None if no fixtures available.
    """
    f = Football()
    now = datetime.datetime.utcnow()
    fixtures = f.get_team_fixtures(team_id)
    fixtures_upcoming = [f for f in fixtures if f.date > now]  # TODO update dates to BST (uk time)
    try:
        return fixtures_upcoming[0]
    except KeyError:
        print("Dates for future fixtures are not currently available.")
        return


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
        print(f"Team with ID: {team_id} are not participating in {fixture.home_team_name}({fixture.home_team_id}) "
              f"vs {fixture.away_team_name}({fixture.away_team_id})")


def get_comp_ids():
    f = Football()
    comps = f.get_all_competitions()
    return [{'comp_id': comp.id, 'comp_name': comp.name} for comp in comps]


def write_comp_ids():
    path = Path.cwd().parent / "data" / "comp_ids.csv"
    with open(path, mode='w') as csv_file:
        fieldnames = ["comp_id", "comp_name"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in get_comp_ids():
            writer.writerow(row)
    return


def get_comp_team_ids(comp_id):
    f = Football()
    teams = f.get_competition_teams(comp_id)
    return [{'team_id': team.id, 'team_name': team.name} for team in teams]


def write_comp_team_ids(comp_id):
    path = Path.cwd().parent / "data" / f"team_ids_{comp_id}.csv"
    try:
        with open(path, mode='w') as csv_file:
            fieldnames = ["team_id", "team_name"]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for row in get_comp_team_ids(comp_id):
                writer.writerow(row)
    except requests.exceptions.HTTPError:
        print(f"Competition ID {comp_id} not found.")
        path.unlink()
    return


def oauth_login():
    """Authenticate with twitter using OAuth"""
    consumer_key = keys.CONSUMER_API_KEY
    consumer_secret = keys.CONSUMER_API_KEY_SECRET

    auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret)
    auth_url = auth.get_authorization_url()

    verify_code = input(
        "Authenticate at %s and then enter you verification code here > " % auth_url
    )
    auth.get_access_token(verify_code)

    return tweepy.API(auth)


def batch_delete(api):
    print(
        "You are about to delete all tweets from the account @%s."
        % api.verify_credentials().screen_name
    )
    print("Does this sound ok? There is no undo! Type yes to carry out this action.")
    do_delete = input("> ")
    if do_delete.lower() == "yes":
        for status in tweepy.Cursor(api.user_timeline).items():
            try:
                api.destroy_status(status.id)
                print("Deleted:", status.id)
            except Exception:
                traceback.print_exc()
                print("Failed to delete:", status.id)


if __name__ == '__main__':
    print("running helpers.py")
    # print(write_comp_ids())
    # print(get_comp_ids())
    # write_comp_ids()
    # print(get_comp_team_ids(2016))
    # write_comp_team_ids(2016002020)
    # print(f"The next fixture is: {get_next_fixture(328)}")
    # api = oauth_login()
    # batch_delete(api)


