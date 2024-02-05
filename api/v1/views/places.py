#!/usr/bin/python3
""" handles all default RestFul API actions for places """
from flask import jsonify, abort, request
from models import storage
from models.place import Place
from api.v1.views import app_views
from models.city import City
from models.user import User
from models.state import State
from models.amenity import Amenity


@app_views.route('/cities/<city_id>/places', methods=['GET'],
                 strict_slashes=False)
def get_all_places(city_id):
    """ Retrieves the list of all Place objects of a City """
    city = storage.get(City, city_id)
    if city is None:
        abort(404)
    places = [place.to_dict() for place in city.places]
    return jsonify(places)


@app_views.route('/places/<place_id>', methods=['GET'], strict_slashes=False)
def get_place(place_id):
    """ Retrieves a Place object """
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    return jsonify(place.to_dict())


@app_views.route('/places/<place_id>', methods=['DELETE'],
                 strict_slashes=False)
def delete_place(place_id):
    """ Deletes a Place object """
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    storage.delete(place)
    storage.save()
    return jsonify({}), 200


@app_views.route('/cities/<city_id>/places', methods=['POST'],
                 strict_slashes=False)
def create_place(city_id):
    """ Creates a Place """
    city = storage.get(City, city_id)
    if city is None:
        abort(404)
    if not request.get_json():
        abort(400, description="Not a JSON")
    if 'user_id' not in request.get_json():
        abort(400, description="Missing user_id")
    if storage.get(User, request.get_json()['user_id']) is None:
        abort(404)
    if 'name' not in request.get_json():
        abort(400, description="Missing name")
    place = Place(**request.get_json())
    place.city_id = city_id
    place.save()
    return jsonify(place.to_dict()), 201


@app_views.route('/places/<place_id>', methods=['PUT'], strict_slashes=False)
def update_place(place_id):
    """ Updates a Place object """
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    if not request.get_json():
        abort(400, description="Not a JSON")
    for key, value in request.get_json().items():
        if key not in ['id', 'user_id', 'city_id', 'created_at', 'updated_at']:
            setattr(place, key, value)
    storage.save()
    return jsonify(place.to_dict())


@app_views.route('/places_search', methods=['POST'], strict_slashes=False)
def search_places():
    """ Retrieves the list of all Place objects depending of the JSON
    in the body of the request """
    if not request.get_json():
        abort(400, description="Not a JSON")
    cities = request.get_json().get('cities', [])
    states = request.get_json().get('states', [])
    amenities = request.get_json().get('amenities', [])

    if not cities and not states and not amenities:
        places = storage.all(Place).values()
        return jsonify([place.to_dict() for place in places])

    places = []
    if cities:
        for city_id in cities:
            city = storage.get(City, city_id)
            if city is not None:
                places.extend(city.places)

    if states:
        for state_id in states:
            state = storage.get(State, state_id)
            if state is not None:
                for city in state.cities:
                    places.extend(city.places)

    if amenities:
        for place in places:
            place_amenities = {amenity.id for amenity in place.amenities}
            if not place_amenities.issuperset(amenities):
                places.remove(place)

    return jsonify([place.to_dict() for place in places])
