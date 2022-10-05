# deletes all tweets from account
import traceback

import tweepy

from configs import keys


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


if __name__ == "__main__":
    api = oauth_login()
    batch_delete(api)
