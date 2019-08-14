import hashlib
import os
import binascii
from peewee import (
    DatabaseProxy,
    Model,
    AutoField,
    CharField,
    FloatField,
    ForeignKeyField,
    ModelSelect
)

# Setup a database proxy instead of an actual database so we can specify it
# at runtime
database_proxy = DatabaseProxy()


class BaseModel(Model):
    """Base class that defines the database attribute for all models."""

    class Meta:
        database = database_proxy


class InvalidPassword(Exception):
    pass


class Location:
    """Non-database model used to validate and manage location data."""

    def __init__(self, latitude: float, longitude: float) -> 'Location':
        """Creates a new Location object with the given coordinates.

        Parameters
        ----------
        latitude : float
            Latitude, must be in the [-90, 90] range

        longitude : float
            Longitude, must be in the [-180, 180] range

        Raises
        ------
        ValueError
            If the coordinates' format is invalid.

        Returns
        -------
        Location
            A new Location object.
        """
        if not isinstance(latitude, float) or abs(latitude) > 90:
            raise ValueError('Invalid Latitude')

        if not isinstance(longitude, float) or abs(longitude) > 180:
            raise ValueError('Invalid Longitude')

        self.latitude = latitude
        self.longitude = longitude

    @classmethod
    def create_from_string(cls, latitude: str, longitude: str) -> 'Location':
        """Creates a new Location from text coordinates

        Parameters
        ----------
        latitude : str
            Latitude, string representing a float

        longitude : str
            Longitude, string representing a float

        Raises
        ------
        ValueError
            If the strings cannot be parsed as floats or if the the
            coordinates' format is invalid.

        Returns
        -------
        location
            A new Location object.
        """

        latitude = float(latitude)
        longitude = float(longitude)

        return cls(latitude, longitude)

    def __iter__(self):
        # Sometimes we need the coordinates as a sequence, this makes it easier
        return iter((self.latitude, self.longitude))


class User(BaseModel):
    """Peewee Model representing a User

    Attributes
    ----------
    id : AutoField
        autoincrementing primary key
    username : str
        unique username for the user
    key : str
        hashed and salted password
    salt : int
        the salt used for hashing the password
    """
    id = AutoField(null=False, primary_key=True)
    username = CharField(unique=True, null=False)
    key = CharField(null=False)
    salt = CharField(null=False)

    @classmethod
    def signup(cls, username: str, password: str) -> 'User':
        """Creates a new user.

        The username is stored as-is but the password is salted and hashed,
        two values, "salt" and "key" are kept to validate the password.

        Parameters
        ----------
        username : str
            username, must be unique

        password : str
            user's password, won't be stored

        Raises
        ------
        IntegrityError
            If username already exists.

        Returns
        -------
        user
            A new instance of user.
        """
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt,
                                  100000)
        key = binascii.hexlify(key)
        salt = binascii.hexlify(salt)
        new_user = cls.create(username=username, key=key, salt=salt)

        return new_user

    @classmethod
    def authenticate(cls, username: str, password: str):
        """Verifies password for the given user.

        Parameters
        ----------
        username : str
            username for an existing user

        password : str
            password to verify

        Raises
        ------
        DoesNotExist
            If the user does not exist.

        InvalidPassword
            If the password is incorrect.
        """
        user = cls.get(cls.username == username)
        salt = binascii.unhexlify(user.salt)
        key = binascii.unhexlify(user.key)
        test_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'),
                                       salt, 100000)

        if test_key != key:
            raise InvalidPassword("Password does not match record")


class Car(BaseModel):
    """Peewee Model representing a Car

    Attributes
    ----------
    id : AutoField
        autoincrementing primary key
    user : User
        the owner of this car
    license_plate : str
        the alphanumeric license plate for the car
    latitude : float
        last known latitude for this car
    longitud : float
        last known longitude for this car
    """
    id = AutoField(null=False, primary_key=True)
    user = ForeignKeyField(User, null=False)
    license_plate = CharField(unique=True, null=False)
    latitude = FloatField(null=False)
    longitude = FloatField(null=False)

    @classmethod
    def create_with_user(cls, user: User, license_plate: str,
                         location: Location) -> 'Car':
        """Creates a new car

        Parameters
        ----------
        user : User
            the owner of the car

        license_plate : str
            car's license plate

        location : Location
            last known location for the car

        Raises
        ------
        ValueError
            If the license plate is empty

        IntegrityError
            If the license plate already exists
        """
        license_plate = license_plate.strip()
        if len(license_plate) == 0:
            raise ValueError("License Plate can't be empty")

        latitude, longitude = location
        return Car.create(user=user, license_plate=license_plate,
                          latitude=latitude, longitude=longitude)

    @classmethod
    def find_user_cars(cls, user: User) -> 'ModelSelect':
        """Finds all cars owned by the given user

        Parameters
        ----------
        user : User
            the user whose cars we're finding

        Returns
        ------
        cars
            An iterable of cars (empty if the user owns no cars)
        """
        return cls.select().where(Car.user == user)

    @classmethod
    def find_car_by_plate(cls, user: User, plate: str) -> 'Car':
        """Finds the car with "plate" owned by "user".

        Parameters
        ----------
        user : User
            the owner of the car we're finding
        plate: str
            the license plate of the car we're finding

        Returns
        ------
        car
            the car with the given user and license plate

        Raises
        ------
        DoesNotExist
            If no car exists with the given characteristics.
        """
        return cls.get(Car.user == user, Car.license_plate == plate)

    def update_location(self, location: Location) -> None:
        """Updates the last known location of the current instance

        Parameters
        ----------
        location : Location
            the new location
        """
        self.latitude = location.latitude
        self.longitude = location.longitude
        self.save()

    def location(self) -> Location:
        """Returns the last known location for this car

        Returns
        -------
        location
            last known coordinates for this car as a Location object
        """
        return Location(self.latitude, self.longitude)
