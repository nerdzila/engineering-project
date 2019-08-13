import hashlib
import os
import binascii
from peewee import (
    DatabaseProxy,
    Model,
    AutoField,
    CharField,
    FloatField,
    ForeignKeyField
)

database_proxy = DatabaseProxy()


class InvalidPassword(Exception):
    pass


class Location:
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

    @classmethod
    def create_from_string(cls, latitude: str, longitude: str) -> 'Location':
        latitude = float(latitude)
        longitude = float(longitude)

        if abs(latitude) > 90:
            raise ValueError('Invalid Latitude')

        if abs(longitude) > 180:
            raise ValueError('Invalid Longitude')

        return cls(latitude, longitude)

    def __iter__(self):
        return iter((self.latitude, self.longitude))


class BaseModel(Model):
    class Meta:
        database = database_proxy


class User(BaseModel):
    id = AutoField(null=False)
    username = CharField(unique=True, null=False)
    key = CharField()
    salt = CharField()

    @classmethod
    def signup(cls, username, password):
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt,
                                  100000)
        key = binascii.hexlify(key)
        salt = binascii.hexlify(salt)
        new_user = cls.create(username=username, key=key, salt=salt)

        return new_user

    @classmethod
    def authenticate(cls, username, password):
        user = cls.get(cls.username == username)
        salt = binascii.unhexlify(user.salt)
        key = binascii.unhexlify(user.key)
        test_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'),
                                       salt, 100000)

        if test_key != key:
            raise InvalidPassword()

        return user


class Car(BaseModel):
    id = AutoField(null=False)
    user = ForeignKeyField(User, null=False)
    license_plate = CharField(unique=True, null=False)
    latitude = FloatField()
    longitude = FloatField()

    @classmethod
    def create_with_user(cls, user: User, license_plate: str,
                         location: Location) -> 'Car':
        license_plate = license_plate.strip()
        if len(license_plate) == 0:
            raise ValueError("License Plate can't be empty")

        latitude, longitude = location
        return Car.create(user=user, license_plate=license_plate,
                          latitude=latitude, longitude=longitude)

    @classmethod
    def find_user_cars(cls, user: User) -> 'Car':
        return cls.select().where(Car.user == user)

    @classmethod
    def find_car_by_plate(cls, user: User, plate: str) -> 'Car':
        return cls.get(Car.user == user, Car.license_plate == plate)

    def update_location(self, location: Location) -> None:
        self.latitude = location.latitude
        self.longitude = location.longitude
        self.save()

    def location(self) -> Location:
        return Location(self.latitude, self.longitude)
