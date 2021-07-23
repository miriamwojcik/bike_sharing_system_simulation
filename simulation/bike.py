# Bike Class used to create bike objects for the Aberdeen Bike-Sharing System model 

# bike id and location coordinates list passed in a constructor
class Bike:
    def __init__(self, id: str, location: list):
        self.id = id
        self.location = location

# Getters and setters
    def get_bike_id(self):
        return self.id

    def set_bike_id(self, bike_id):
        self.id = bike_id

    def get_bike_location(self):
        return self.location

    def set_bike_location(self, coordinates):
        self.location = coordinates