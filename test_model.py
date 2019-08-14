import pytest
from os import remove
from model import User, Car, InvalidPassword, database_proxy, Location
from peewee import SqliteDatabase, DoesNotExist, IntegrityError

try:
    remove('data/test.db')
except FileNotFoundError:
    pass

database = SqliteDatabase('data/test.db')
database_proxy.initialize(database)

with database:
    database.create_tables([User, Car])


user1 = User.signup(
    username='user1',
    password='password1'
)

user2 = User.signup(
    username='user2',
    password='password2'
)

user3 = User.signup(
    username='user3',
    password='password3'
)


car1 = Car.create(user=user1, license_plate='LOL1337',
                  latitude=19.341803, longitude=-99.196494)
car2 = Car.create(user=user1, license_plate='ASAP123',
                  latitude=19.341803, longitude=-99.196494)
car3 = Car.create(user=user1, license_plate="FTW6667",
                  latitude=19.520504, longitude=-99.109185)


@pytest.fixture()
def default_user():
    return user1


@pytest.fixture()
def empty_user():
    return user2


@pytest.fixture()
def mutable_user():
    return user3


@pytest.fixture()
def default_user_cars():
    return [car1, car2, car3]


@pytest.fixture()
def default_car():
    return car1


@pytest.fixture()
def default_location():
    return Location(19.341803, 99.196494)


class TestLocation:
    def test_create(self):
        loc = Location.create_from_string('19.456233', '-99.109234')
        assert loc.latitude == 19.456233
        assert loc.longitude == -99.109234

    def test_incorrect_format(self):
        with pytest.raises(ValueError):
            Location.create_from_string('Hello', 'World')

    def test_incorrect_latitude(self):
        with pytest.raises(ValueError):
            Location.create_from_string('-102.345234', '-99.134938')

    def test_incorrect_longitude(self):
        with pytest.raises(ValueError):
            Location.create_from_string('-32.345234', '-209.134938')

    def test_iterable(self, default_location):
        expected_list = [default_location.latitude, default_location.longitude]
        assert expected_list == [c for c in default_location]


class TestUsers:
    def test_signup(self):
        new_user = User.signup('user_new', 'password_new')
        assert new_user.id is not None
        User.authenticate('user_new', 'password_new')
        expected_user = User.get(User.username == 'user_new')
        assert expected_user.id == new_user.id

    def test_auth_valid(self):
        # Must not raise an exception
        User.authenticate('user2', 'password2')

    def test_auth_invalid_user(self):
        with pytest.raises(DoesNotExist):
            User.authenticate('user4', 'password2')

    def test_auth_invalid_password(self):
        with pytest.raises(InvalidPassword):
            User.authenticate('user1', 'badpassword')


class TestCars:
    def test_create(self, mutable_user, default_location):
        car = Car.create_with_user(mutable_user, 'TEST123', default_location)
        assert car.id is not None

    def test_create_invalid_plates(self, default_user, default_location):
        with pytest.raises(ValueError):
            Car.create_with_user(default_user, '     ', default_location)

    def test_create_duplicate_plates(self, default_user, default_car,
                                     default_location):
        with pytest.raises(IntegrityError):
            Car.create_with_user(default_user, default_car.license_plate,
                                 default_location)

    def test_find_cars_by_user(self, default_user, default_user_cars):
        found_ids = set(car.id for car in Car.find_user_cars(default_user))
        assert set(car.id for car in default_user_cars) == found_ids

    def test_find_empty_car_list(self, empty_user):
        assert len(Car.find_user_cars(empty_user)) == 0

    def test_find_car_by_plate(self, default_user, default_car):
        found_car = Car.find_car_by_plate(default_user,
                                          default_car.license_plate)
        assert found_car.id == default_car.id

    def test_car_not_found_for_user(self, default_user, empty_user,
                                    default_car):
        with pytest.raises(DoesNotExist):
            Car.find_car_by_plate(empty_user, default_car.license_plate)

        with pytest.raises(DoesNotExist):
            Car.find_car_by_plate(default_user, 'MADEUP999')

    def test_update_location(self, default_car, default_location):
        assert tuple(default_car.location()) != tuple(default_location)

        default_car.update_location(default_location)
        updated_car = Car.get_by_id(default_car.id)
        assert tuple(updated_car.location()) == tuple(default_location)

    def test_delete_car(self, mutable_user):
        car = Car.find_car_by_plate(mutable_user, 'TEST123')
        num_deleted = car.delete_instance()
        assert num_deleted == 1
        assert len(Car.find_user_cars(mutable_user)) == 0
