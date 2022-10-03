import datetime

from dagster import op, job, ScheduleDefinition, repository

from helpers import twitter_auth, get_next_fixture, get_opposition_team, format_tweet


@op(config_schema={"team_id": int})
def create_next_fixture_date_tweet_op(context):
    f = get_next_fixture(context.op_config["team_id"])
    opp = get_opposition_team(f, context.op_config["team_id"])
    d = datetime.datetime.now().strftime("%H:%M:%S")
    tweet = f"The next match is against {opp['name']} at {f.date}\n[{d}]"
    return format_tweet(tweet)


@op
def post_tweet(tweet: str) -> None:
    """
    Given a tweet, posts to account using Twitter API v2 Client.
    Args:
        tweet: Tweet to post
    """
    client = twitter_auth()
    client.create_tweet(text=tweet)


@job
def create_next_fixture_date_tweet_job():  # TODO perform check to see if tweet is same as previous post
    post_tweet(create_next_fixture_date_tweet_op())


schedule = ScheduleDefinition(job=create_next_fixture_date_tweet_job,
                              cron_schedule="0 10 * * *")

job_config = create_next_fixture_date_tweet_job.execute_in_process(
    run_config={"ops": {"create_next_fixture_date_tweet_op": {"config": {"team_id": 328}}}}
)


@repository
def next_fixture_repo():
    return [schedule,
            create_next_fixture_date_tweet_job]

# TODO - if today is matchday tweet about opposition and
#  wait for game end to tweet stats

# TODO create tests for functions




