#!/usr/bin/python3
""" has route for index """
from api.v1.views import app_views


@app_views.route('/status', strict_slashes=False)
def status():
    """ returns status """
    return {"status": "OK"}


@app_views.route('/stats', strict_slashes=False)
def stats():
    """ returns stats """
    from models import storage
    from models.state import State
    from models.city import City
    from models.amenity import Amenity
    from models.place import Place
    from models.review import Review
    from models.user import User
    return {
        "amenities": storage.count(Amenity),
        "cities": storage.count(City),
        "places": storage.count(Place),
        "reviews": storage.count(Review),
        "states": storage.count(State),
        "users": storage.count(User)
    }
