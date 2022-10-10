prev_response = {}


def update_prev_response(r, endpoint):
    """Sets the prev_response attribute to contain a dict that includes
    the response status code and headers of the most recent HTTP
    request.

    Arguments:
    r -- The response object (of the latest HTTP request).
    endpoint -- The endpoint used (in the latest HTTP request).
    """
    global prev_response
    prev_response = r.headers
    prev_response["Status-Code"] = r.status_code
    prev_response["Endpoint"] = endpoint
