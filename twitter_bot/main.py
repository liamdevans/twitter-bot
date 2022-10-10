"""
A module containing dagster ops and jobs used to schedule football tweets as part
of the `twitter_bot` package.
"""
from datetime import datetime

import tweepy.errors
from dagster import op, job, ScheduleDefinition, repository, Out, Output, graph

from helpers import (
    twitter_auth,
    get_next_fixture,
    get_opposition_team,
    format_tweet,
    make_date_readable,
    home_or_away,
)
import globals


@op(config_schema={"team_id": int})
def get_next_fixture_obj(context):
    fix = get_next_fixture(context.op_config["team_id"])
    return fix


@op(
    out={
        "create_next_fixture_date_tweet_branch": Out(is_required=False),
        "is_it_matchday_branch": Out(is_required=False),
    }
)
def is_fixture_date_updated(fix):
    if fix.date == globals.latest_fixture:
        yield Output(fix, "is_it_matchday_branch")
    else:
        globals.update_latest_fixture(fix)
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

    opp = get_opposition_team(fix, context.op_config["team_id"])
    loc = home_or_away(fix, context.op_config["team_id"])
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
    if fix.date.date() == datetime.today().date():
        yield Output(fix, "create_opp_stats_branch")
    else:
        yield Output(fix, "do_nothing_branch")


@op
def create_opp_stats(fix):
    pass


@op
def do_nothing():
    print("Today is neither match day or the day after a match day")


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


@graph
def twitter_bot_graph():
    """
    Dagster graph to create_next_fixture_date_tweet and then post_tweet.
    Graph scheduled to run 10 AM UTC daily.
    """
    (
        create_next_fixture_date_tweet_branch,
        is_it_matchday_branch,
    ) = is_fixture_date_updated(get_next_fixture_obj())
    post_tweet(create_next_fixture_date_tweet(create_next_fixture_date_tweet_branch))

    create_opp_stats_branch, do_nothing_branch = is_it_matchday(is_it_matchday_branch)
    post_tweet(create_opp_stats(create_opp_stats_branch))
    do_nothing(do_nothing_branch)


graph_config = twitter_bot_graph.execute_in_process(
    run_config={"ops": {"get_next_fixture_date": {"config": {"team_id": 328}}}}
)

schedule = ScheduleDefinition(
    job=twitter_bot_graph, cron_schedule="0 10 * * *"  # TODO
)  # runs daily @ 10 AM UTC


@repository
def next_fixture_repo():
    """
    Dagster repository object for the twitter_bot_graph and its
    corresponding schedule.
    Returns:
        list of job object and ScheduleDefinition
    """
    return [schedule, twitter_bot_graph]
