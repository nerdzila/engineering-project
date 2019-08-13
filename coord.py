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
