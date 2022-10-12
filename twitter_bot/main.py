"""
A module containing dagster ops and jobs used to schedule football tweets as part
of the `twitter_bot` package.
"""
from datetime import datetime
from pathlib import Path

import tweepy.errors
from dagster import (
    op,
    repository,
    Out,
    Output,
    graph,
    get_dagster_logger,
    asset,
    schedule,
    RunRequest,
)

from helpers import (
    twitter_auth,
    get_next_fixture,
    get_opposition_team,
    format_tweet,
    make_date_readable,
    home_or_away,
    write_latest_fixture_date,
)
from standings import Tables
from configs.fbref import championship_url
import global_vars


@op(config_schema={"team_id": int})
def get_next_fixture_obj(context):
    print("Getting the next fixture object")
    fix = get_next_fixture(context.op_config["team_id"])
    global_vars.request_count += 1
    print(f"Number of requests: {global_vars.request_count}")
    return fix


@asset
def get_latest_fixture_date():
    path = Path().cwd() / "latest_fixture.txt"
    with open(path, mode="r", encoding="utf-8") as file:
        date = file.read()
    return date


@op(
    out={
        "create_next_fixture_date_tweet_branch": Out(is_required=False),
        "is_it_matchday_branch": Out(is_required=False),
    }
)
def is_fixture_date_updated(fix):
    same_as_previous = fix.date.strftime(format="%d-%m-%y") == get_latest_fixture_date()
    print(
        f"Dates {fix.date.strftime(format='%d-%m-%y')} and {get_latest_fixture_date()} are the same: {same_as_previous}"
    )
    if same_as_previous:
        yield Output(fix, "is_it_matchday_branch")
    else:
        write_latest_fixture_date(fix.date)
        yield Output(fix, "create_next_fixture_date_tweet_branch")


@op
def create_next_fixture_date_tweet(context, fix):
    """
    Dagster op that forms the first part of the job twitter_bot_graph.
    Uses the get_next_fixture and get_opposition_team functions to return a
    formatted, 'tweetable' string.
    Args:
        fix:
        context: context contains dagster configuration for team_id

    Returns:
        A formatted, Twitter ready tweet
    """
    team_id = context.run_config["ops"]["get_next_fixture_obj"]["config"]["team_id"]
    opp = get_opposition_team(fix, team_id)
    loc = home_or_away(fix, team_id)
    tweet = f"The next match is {loc} against {opp['name']} on {make_date_readable(fix.date)}"
    # return format_tweet(tweet)
    return tweet


@op(
    out={
        "create_opp_stats_branch": Out(is_required=False),
        "do_nothing_branch": Out(is_required=False),
    }
)
def is_it_matchday(fix):
    my_logger = get_dagster_logger()
    my_logger.info(f"The fixture object is: {fix}")
    if fix.date.date() == datetime.today().date():
        yield Output(fix, "create_opp_stats_branch")
    else:
        yield Output(fix, "do_nothing_branch")


@op
def create_opp_stats(fix) -> str:
    print("creating stats on opp")
    my_tbl = Tables(championship_url)
    # TODO


@op
def do_nothing(fix):
    print("Today is neither match day or the day after a match day!")
    return None


@op
def post_tweet(tweet: str) -> None:
    """
    Dagster op that forms the second part of the job twitter_bot_graph.
    Given a tweet, posts to account using Twitter API v2 Client.
    Args:
        tweet: Tweet to post
    """
    client = twitter_auth()
    try:
        client.create_tweet(text=tweet)
    except tweepy.errors.Forbidden:
        print("Not allowed to create a tweet with duplicate content")
        pass


@graph
def twitter_bot_graph():
    """
    Dagster graph to create_next_fixture_date_tweet and then post_tweet.
    Graph scheduled to run 10 AM UTC daily.
    """
    next_fixture = get_next_fixture_obj()
    (
        create_next_fixture_date_tweet_branch,
        is_it_matchday_branch,
    ) = is_fixture_date_updated(next_fixture)
    post_tweet(create_next_fixture_date_tweet(create_next_fixture_date_tweet_branch))

    create_opp_stats_branch, do_nothing_branch = is_it_matchday(is_it_matchday_branch)
    post_tweet(create_opp_stats(create_opp_stats_branch))
    do_nothing(do_nothing_branch)


@schedule(
    job=twitter_bot_graph,
    execution_timezone="Europe/London",
    cron_schedule="0 12 * * *",
)
def twitter_bot_schedule():
    return RunRequest(
        run_config={"ops": {"get_next_fixture_obj": {"config": {"team_id": 328}}}}
    )


@repository
def next_fixture_repo():
    """
    Dagster repository object for the twitter_bot_graph and its
    corresponding schedule.
    Returns:
        list of job object and ScheduleDefinition
    """
    return [twitter_bot_schedule, twitter_bot_graph, get_latest_fixture_date]
