import os
from model import User, Car, database_proxy
from peewee import SqliteDatabase

if __name__ == "__main__":
    try:
        os.remove('data/dev.db')
    except FileNotFoundError:
        pass

    database = SqliteDatabase('data/dev.db')
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

    car1 = Car.create(user=user1, license_plate='LOL1337',
                      latitude=19.341803, longitude=-99.196494)
    car2 = Car.create(user=user1, license_plate='ASAP123',
                      latitude=19.435499, longitude=-99.274269)
    car3 = Car.create(user=user1, license_plate="FTW6667",
                      latitude=19.520504, longitude=-99.109185)
