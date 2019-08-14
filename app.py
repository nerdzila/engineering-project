from flask import Flask, jsonify, request, render_template
from flask_httpauth import HTTPBasicAuth
from model import Car, User, database_proxy, InvalidPassword, Location
from peewee import SqliteDatabase, DoesNotExist, IntegrityError
from playhouse.shortcuts import model_to_dict


# ============================================================================
# SETUP
# ============================================================================
database = SqliteDatabase('data/dev.db')
database_proxy.initialize(database)

app = Flask(__name__)
auth = HTTPBasicAuth()


# ============================================================================
# HELPERS
# ============================================================================
class BadApiRequest(Exception):
    pass


@app.errorhandler(404)
def not_found(error):
    return 'Not found', 404


@app.errorhandler(BadApiRequest)
def handle_invalid_api_requests(e):
    return json_response(str(e), success=False), 400


def json_response(result, success=True):
    return jsonify({
        'success': success,
        'result': result
    })


def validate_json_request(request, required_fields=[]):
    if not request.json:
        raise BadApiRequest('Request must contain JSON payload')

    for field in required_fields:
        if field not in request.json:
            raise BadApiRequest(f'Field "{field}" missing')


# ============================================================================
# AUTHENTICATION
# ============================================================================
@auth.verify_password
def verify_password(username, password):
    try:
        User.authenticate(username, password)
    except (DoesNotExist, InvalidPassword):
        return False
    return True


# ============================================================================
# FRONTEND
# ============================================================================
@app.route('/')
@auth.login_required
def index():
    user = User.get(User.username == auth.username())
    cars = [car for car in Car.find_user_cars(user).dicts()]
    return render_template('index.html.j2', cars=cars)


# ============================================================================
# API
# ============================================================================
@app.route('/api/cars', methods=['GET'])
@auth.login_required
def get_cars():
    user = User.get(User.username == auth.username())
    cars = [car for car in Car.find_user_cars(user).dicts()]
    return json_response(cars)


@app.route('/api/cars', methods=['POST'])
@auth.login_required
def create_car():
    user = User.get(User.username == auth.username())

    required_fields = ('license_plate', 'latitude', 'longitude')
    validate_json_request(request, required_fields=required_fields)

    try:
        location = Location.create_from_string(
            request.json['latitude'],
            request.json['longitude']
        )
    except ValueError as e:
        raise BadApiRequest(str(e))

    try:
        car = Car.create_with_user(
            user,
            request.json['license_plate'],
            location
        )
    except IntegrityError:
        raise BadApiRequest('Car already exists')
    except ValueError as e:
        raise BadApiRequest(str(e))

    return json_response(model_to_dict(car, recurse=False))


@app.route('/api/cars/<license_plate>', methods=['PUT'])
@auth.login_required
def update_car(license_plate):
    user = User.get(User.username == auth.username())

    try:
        car = Car.find_car_by_plate(user, license_plate)
    except DoesNotExist:
        raise BadApiRequest('Car not found')

    required_fields = ('latitude', 'longitude')
    validate_json_request(request, required_fields=required_fields)

    try:
        location = Location.create_from_string(
            request.json['latitude'],
            request.json['longitude']
        )
    except ValueError as e:
        raise BadApiRequest(str(e))

    car.update_location(location)

    return json_response(model_to_dict(car, recurse=False))


@app.route('/api/cars/<license_plate>', methods=['DELETE'])
@auth.login_required
def delete_car(license_plate):
    user = User.get(User.username == auth.username())

    try:
        car = Car.find_car_by_plate(user, license_plate)
    except DoesNotExist:
        raise BadApiRequest('Car not found')

    num_deleted = car.delete_instance()
    return json_response({'cars_deleted': num_deleted})


if __name__ == '__main__':
    app.run(debug=True)
