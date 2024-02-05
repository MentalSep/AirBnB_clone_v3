#!/usr/bin/python3
""" has route for index """
from api.v1.views import app_views


@app_views.route('/status', strict_slashes=False)
def status():
    """ returns status """
    return {"status": "OK"}
