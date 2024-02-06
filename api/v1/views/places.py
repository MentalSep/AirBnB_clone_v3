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
    body = request.get_json()
    if type(body) is not dict:
        abort(400, description="Not a JSON")

    states = body.get("states", [])
    cities = body.get("cities", [])
    amenities = body.get("amenities", [])
    places = []

    if not states and not cities:
        places = storage.all(Place).values()
    else:
        states = [storage.get(State, _id) for _id
                  in states if storage.get(State, _id)]
        cities = [city for state in states for city in state.cities]
        cities += [storage.get(City, _id) for _id
                   in cities if storage.get(City, _id)]
        cities = list(set(cities))
        places = [place for city in cities for place in city.places]

    amenities = [storage.get(Amenity, _id) for _id
                 in amenities if storage.get(Amenity, _id)]

    result = []
    for place in places:
        result.append(place.to_dict())
        for amenity in amenities:
            if amenity not in place.amenities:
                result.pop()
                break

    return jsonify(result)
