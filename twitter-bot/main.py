import datetime

from dagster import op, job, ScheduleDefinition, repository

from helpers import twitter_auth, get_next_fixture, get_opposition_team, format_tweet


# @format_tweet

@op(config_schema={"team_id": int})
def create_next_fixture_date_tweet_op(context):
    f = get_next_fixture(context.op_config["team_id"])
    opp = get_opposition_team(f, context.op_config["team_id"])
    d = datetime.datetime.now().strftime("%H:%M:%S")
    return f"The next match is against {opp['name']} at {f.date}\n[{d}]"


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
def create_next_fixture_date_tweet_job():
    post_tweet(create_next_fixture_date_tweet_op())


job_config = create_next_fixture_date_tweet_job.execute_in_process(
    run_config={"ops": {"create_next_fixture_date_tweet_op": {"config": {"team_id": 328}}}}
)
schedule = ScheduleDefinition(job=create_next_fixture_date_tweet_job, cron_schedule="* * * * *")


@repository
def next_fixture_repo():
    return [schedule,
            create_next_fixture_date_tweet_job]

# if __name__ == '__main__':
#     print("running main.py")
# post_tweet(create_next_fixture_date_tweet_op(328))
# post_tweet(f"Shirt Number: {get_next_fixture()}")
