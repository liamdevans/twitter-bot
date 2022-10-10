latest_fixture = {}


def update_latest_fixture(fix):
    """Sets the latest_fixture attribute to date of the most recent

    Arguments:
    r -- The response object (of the latest HTTP request).
    endpoint -- The endpoint used (in the latest HTTP request).
    """
    global latest_fixture
    latest_fixture = fix.date
