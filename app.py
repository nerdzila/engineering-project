from flask import Flask, jsonify, request, render_template
from flask_httpauth import HTTPBasicAuth
from db import Car, User, database_proxy, InvalidPassword
from coord import Location
from peewee import SqliteDatabase, DoesNotExist, IntegrityError
from playhouse.shortcuts import model_to_dict


database = SqliteDatabase('data/dev.db')
database_proxy.initialize(database)

app = Flask(__name__)
auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):
    try:
        User.authenticate(username, password)
    except (DoesNotExist, InvalidPassword):
        return False
    return True


@app.errorhandler(404)
def not_found(error):
    return 'Not found', 404


@app.route('/')
@auth.login_required
def index():
    user = User.get(User.username == auth.username())
    cars = [car for car in Car.find_user_cars(user).dicts()]
    return render_template('index.html.j2', cars=cars)


@app.route('/api/cars', methods=['GET'])
@auth.login_required
def get_cars():
    user = User.get(User.username == auth.username())
    cars = [car for car in Car.find_user_cars(user).dicts()]
    return jsonify(cars)


@app.route('/api/cars', methods=['POST'])
@auth.login_required
def create_car():
    user = User.get(User.username == auth.username())
    if not request.json:
        return 'Request must be JSON', 400

    required_fields = ('license_plate', 'latitude', 'longitude')

    for field in required_fields:
        if field not in request.json:
            return f'Field "{field}" missing', 400
    if 'license_plate' not in request.json:
        return 'missing license plate', 400

    try:
        location = Location.create_from_string(
            request.json['latitude'],
            request.json['longitude']
        )
    except ValueError as e:
        return str(e), 400

    try:
        car = Car.create_with_user(
            user,
            request.json['license_plate'],
            location
        )
    except IntegrityError:
        return 'License plates already in use', 400
    except ValueError as e:
        return str(e), 400

    return jsonify(model_to_dict(car, recurse=False))


@app.route('/api/cars/<license_plate>', methods=['PUT'])
@auth.login_required
def update_car(license_plate):
    user = User.get(User.username == auth.username())

    try:
        car = Car.find_car_by_plate(user, license_plate)
    except DoesNotExist:
        return 'Car not found', 400

    if not request.json:
        return 'Request must be JSON', 400

    required_fields = ('latitude', 'longitude')

    for field in required_fields:
        if field not in request.json:
            return f'Field "{field}" missing', 400

    try:
        location = Location.create_from_string(
            request.json['latitude'],
            request.json['longitude']
        )
    except ValueError as e:
        return str(e), 400

    car.update_location(location)

    return jsonify(model_to_dict(car, recurse=False))


@app.route('/api/cars/<license_plate>', methods=['DELETE'])
@auth.login_required
def delete_car(license_plate):
    user = User.get(User.username == auth.username())

    try:
        car = Car.find_car_by_plate(user, license_plate)
    except DoesNotExist:
        return 'Car not found', 400

    car.delete_instance()
    return jsonify({'deleted': True})


if __name__ == '__main__':
    app.run(debug=True)
