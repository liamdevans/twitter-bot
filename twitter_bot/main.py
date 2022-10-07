"""
A module containing dagster ops and jobs used to schedule football tweets as part
of the `twitter_bot` package.
"""
from dagster import op, job, ScheduleDefinition, repository

from helpers import (
    twitter_auth,
    get_next_fixture,
    get_opposition_team,
    format_tweet,
    make_date_readable,
)


@op(config_schema={"team_id": int})
def create_next_fixture_date_tweet_op(context):
    """
    Dagster op that forms the first part of the job create_next_fixture_date_tweet_job.
    Uses the get_next_fixture and get_opposition_team functions to return a
    formatted, 'tweetable' string.
    Args:
        context: context contains dagster configuration for team_id

    Returns:
        A formatted, Twitter ready tweet
    """
    fix = get_next_fixture(context.op_config["team_id"])
    opp = get_opposition_team(fix, context.op_config["team_id"])
    tweet = f"The next match is against {opp['name']} on {make_date_readable(fix.date)}"
    return format_tweet(tweet)


@op
def post_tweet(tweet: str) -> None:
    """
    Dagster op that forms the second part of the job create_next_fixture_date_tweet_job.
    Given a tweet, posts to account using Twitter API v2 Client.
    Args:
        tweet: Tweet to post
    """
    client = twitter_auth()
    client.create_tweet(text=tweet)


@job
def create_next_fixture_date_tweet_job():
    """
    Dagster job to create_next_fixture_date_tweet_op and then post_tweet.
    Job scheduled to run 10 AM UTC daily.
    """
    post_tweet(create_next_fixture_date_tweet_op())


schedule = ScheduleDefinition(
    job=create_next_fixture_date_tweet_job, cron_schedule="0 10 * * *"
)  # runs daily @ 10 AM UTC

job_config = create_next_fixture_date_tweet_job.execute_in_process(
    run_config={
        "ops": {"create_next_fixture_date_tweet_op": {"config": {"team_id": 328}}}
    }
)


@repository
def next_fixture_repo():
    """
    Dagster repository object for the create_next_fixture_date_tweet_job and its
    corresponding schedule.
    Returns:
        list of job object and ScheduleDefinition
    """
    return [schedule, create_next_fixture_date_tweet_job]
